import asyncio
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple, overload
import httpx
from nonebot import logger

from .exception import GetMblogsFailedError, UnknownError
from .model import Auth, Blog, Picture, Urls


class Spider:
    """新浪微博爬虫"""

    _BEIJING_TZ = timezone(timedelta(hours=8))
    _DATE_FORMAT = "%a %b %d %H:%M:%S %z %Y"

    def __init__(self, uid: int):
        """初始化爬虫实例

        Args:
            uid: 微博用户ID
        """
        self.uid = uid
        self._results: List[Blog] = []
        self._search_results: List[Blog] = []
        self._setup_headers()
        self._setup_apis()

    """ ===== 初始化配置 ===== """

    def _setup_headers(self) -> None:
        """配置请求头"""
        self.headers = Auth.get_headers()
        self.headers["referer"] = f"https://www.weibo.com/u/{self.uid}"

    def _setup_apis(self) -> None:
        """配置API端点"""
        self._api = {
            "mblogs": "https://weibo.com/ajax/statuses/mymblog",
        }

    """ ===== 核心数据获取 ===== """

    async def fetch(self, page: int = 0) -> "Spider":
        """获取指定页码的微博数据

        Args:
            page: 页码（从1开始）

        Returns:
            自身实例（支持链式调用）

        Raises:
            GetMblogsFailedError: 数据获取失败
        """
        try:
            params = {"uid": self.uid, "page": page, "feature": 0}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self._api["mblogs"],
                    headers=self.headers,
                    params=params,
                    timeout=10.0,
                )
                response.raise_for_status()
                content = response.json()

                if content.get("ok") != 1:
                    error_msg = content.get("msg", "数据加载失败")
                    raise GetMblogsFailedError(f"获取微博列表失败: {error_msg}")
                if not content.get("data"):
                    raise GetMblogsFailedError("获取微博列表失败, 超出最大能获取的索引")
                self._parse_mblogs(content["data"]["list"])
                return self

        except httpx.HTTPStatusError as e:
            raise GetMblogsFailedError(f"HTTP请求失败: {e.response.status_code}") from e
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise GetMblogsFailedError("网络连接异常") from e
        except Exception as e:
            raise UnknownError("数据处理异常") from e

    async def search(self, query: str, num: int = 1, start_page: int = 1) -> "Spider":
        """
        循环获取内容，直到收集到 num 条包含 query 的内容。
        """
        current_page = start_page

        # 使用循环代替递归
        while len(self._search_results) < num:
            try:
                await self.fetch(page=current_page)
                filtered = self.filter_by_regex(query)
                blog = filtered.all()
                if blog:
                    # 只有当这个 blog 之前没加过（去重）才加，不过翻页通常自带去重
                    self._search_results.extend(blog)

                current_page += 1

            except GetMblogsFailedError as e:
                logger.error(f"搜索结束: {e}")
                break
            except Exception as e:
                logger.error(f"发生未知错误: {e}")
                break

        self._results = self._search_results[:num]
        return self

    def _parse_mblogs(self, mblogs: List[Dict[str, Any]]) -> None:
        """解析微博数据

        Args:
            mblogs: 原始微博数据列表
        """
        for blog in mblogs:
            self._results.append(
                Blog(
                    mblogid=blog["mblogid"],
                    text_raw=blog["text_raw"],
                    url=f"https://www.weibo.com/{self.uid}/{blog['mblogid']}",
                    created_at=blog["created_at"],
                    pic_list=self._parse_pictures(blog),
                )
            )

    def _parse_pictures(self, blog: Dict[str, Any]) -> List[Picture]:
        """解析微博中的图片数据

        Args:
            blog: 单条微博数据

        Returns:
            图片对象列表
        """
        pic_list = []
        pic_infos = blog.get("pic_infos", {})

        for pic_info in pic_infos.values():
            urls = Urls(
                bmiddle=pic_info.get("bmiddle", {}).get("url"),
                large=pic_info.get("large", {}).get("url"),
                largecover=pic_info.get("largecover", {}).get("url"),
                largest=pic_info.get("largest", {}).get("url"),
                mw2000=pic_info.get("mw2000", {}).get("url"),
                original=pic_info.get("original", {}).get("url"),
                thumbnail=pic_info.get("thumbnail", {}).get("url"),
            )
            pic_list.append(Picture(pic_info.get("pic_id"), urls))

        return pic_list

    """ ===== 数据过滤 ===== """

    def filter_by_time(
        self, start: Optional[datetime] = None, end: Optional[datetime] = None
    ) -> "Spider":
        """按时间范围过滤微博

        Args:
            start: 开始时间（包含），None表示不限制开始时间
            end: 结束时间（包含），None表示不限制结束时间

        Returns:
            过滤后的实例（支持链式调用）

        Examples:
            - 获取今天的微博
            spider.filter_by_time()

            - 获取最近7天的微博
            week_ago = datetime.now() - timedelta(days=7)
            spider.filter_by_time(week_ago)

            - 获取特定日期范围的微博
            start_date = datetime(2023, 1, 1)
            end_date = datetime(2023, 1, 31)
            spider.filter_by_time(start_date, end_date)
        """
        # 获取当前北京时间（用于确定"今天"和默认结束时间）
        now_beijing = datetime.now(tz=self._BEIJING_TZ)

        if start is None and end is None:
            # 无参数 → 今天的数据
            start, end = self._get_today_range(now_beijing)
        elif start is not None and end is None:
            # 单参数 → 从start到今天
            start = self._normalize_time(start)
            end = now_beijing
        else:
            # 双参数 → 指定范围
            if start is not None:
                start = self._normalize_time(start)
            if end is not None:
                end = self._normalize_time(end)

        # 执行时间过滤
        self._results = [
            blog
            for blog in self._results
            if self._is_in_time_range(blog.created_at, start, end)
        ]
        return self

    def _get_today_range(self, now: datetime) -> Tuple[datetime, datetime]:
        """获取今天的时间范围"""
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return today_start, today_end

    def _normalize_time(self, dt: datetime) -> datetime:
        """标准化时间对象为北京时间

        规则：
        - naive datetime → 视为北京时间
        - 其他时区 → 转换为北京时间

        Args:
            dt: 原始时间对象

        Returns:
            标准化为北京时间的时间对象
        """
        if dt.tzinfo is None:
            return dt.replace(tzinfo=self._BEIJING_TZ)
        return dt.astimezone(self._BEIJING_TZ)

    def _is_in_time_range(
        self, created_at: str, start: Optional[datetime], end: Optional[datetime]
    ) -> bool:
        """检查时间是否在指定范围内

        Args:
            created_at: 微博时间字符串
            start: 开始时间
            end: 结束时间

        Returns:
            是否在时间范围内
        """
        try:
            dt = self._parse_created_at(created_at)

            if start and end:
                return start <= dt <= end
            if start:
                return dt >= start
            if end:
                return dt <= end
            return True

        except (ValueError, TypeError):
            return False

    def _parse_created_at(self, created_at: str) -> datetime:
        """解析微博时间字符串

        Args:
            created_at: 微博原始时间字符串

        Returns:
            标准化的时间对象（北京时间）
        """
        # 处理可能的多余空格
        clean_time_str = re.sub(r"\s+", " ", created_at).strip()
        dt = datetime.strptime(clean_time_str, self._DATE_FORMAT)
        return dt.astimezone(self._BEIJING_TZ)

    def filter_by_regex(self, pattern: str, flags: int = 0) -> "Spider":
        """按正则表达式过滤微博

        Args:
            pattern: 正则表达式
            flags: 正则标志位（如re.IGNORECASE）

        Returns:
            过滤后的实例
        """
        compiled = re.compile(pattern, flags)
        self._results = [
            blog for blog in self._results if compiled.search(blog.text_raw)
        ]
        return self

    """ ===== 结果处理 ===== """

    @overload
    def all(self) -> List[Blog]: ...

    @overload
    def all(self, limit: int) -> List[Blog]: ...

    def all(self, limit: Optional[int] = None) -> List[Blog]:
        """获取所有过滤结果

        Args:
            limit: 限制返回数量

        Returns:
            微博对象列表
        """
        return self._results[:limit] if limit is not None else self._results.copy()

    def one(self) -> Optional[Blog]:
        """获取第一条结果

        Returns:
            第一条微博或None
        """
        return self._results[0] if self._results else None

    def count(self) -> int:
        """获取结果数量

        Returns:
            结果数量
        """
        return len(self._results)

    def reset(self) -> "Spider":
        """重置结果集

        Returns:
            重置后的实例
        """
        self._results = []
        return self

    """ ===== 辅助方法 ===== """

    def __len__(self) -> int:
        """支持len()函数"""
        return self.count()

    def __bool__(self) -> bool:
        """支持布尔判断"""
        return bool(self._results)

    def __iter__(self):
        """支持迭代"""
        return iter(self._results)


async def main():
    spider = Spider(7360748659)
    fetcher = await spider.fetch()
    pattern = r"^#[^#]*光遇[^#]*超话]#\s*\d{1,2}\.\d{1,2}\s*"
    blog = fetcher.filter_by_regex(pattern).filter_by_time().one()
    print(blog)
    if blog is not None:
        text = await blog.fetch_long_text()
        print(text)
    else:
        print("No matching blog found.")
    # for pic in blog.pic_list:
    #     await pic.save()
    if blog is not None:
        print(await blog.save_all_images())
    else:
        print("No images to save.")


if __name__ == "__main__":
    asyncio.run(main())
