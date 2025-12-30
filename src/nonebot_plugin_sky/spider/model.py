from __future__ import annotations
import asyncio
import base64
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
import httpx
import aiofiles

from ..utils.bot_loader import config

from .exception import GetMblogsFailedError, UnknownError


class Auth:
    """
    认证信息管理
    """

    # 默认时区（北京时间）
    BEIJING_TZ = timezone(timedelta(hours=8))

    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        """
        获取标准请求头

        Returns:
            包含必要认证信息的headers字典
        """
        return {
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome"
                "/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
            ),
            "cookie": config.weibo_cookie
            if config.weibo_cookie
            else cls._get_default_cookie(),
            "referer": "https://www.weibo.com",
            "sec-ch-ua": '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            "sec-ch-ua-platform": '"Windows"',
        }

    @staticmethod
    def _get_default_cookie() -> str:
        """
        获取默认cookie

        Returns:
            cookie字符串
        """
        return "XSRF-TOKEN=VGRMWAWWnqPRQOpiwaB6LhOO; SUB=_2AkMeDrKVf8NxqwFRmv8TzWPmb45yyw3EieKoUkNOJRMxHRl-yT9xqm0GtRB6NY6cemIl_ZU7KL2sks8K-KAtPokzzFnP; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFyulOCYp-MxBc3AKYbqDI2; WBPSESS=PDVUzjtcUt2fIitQvMR4oRHUCeiVV-tSypB852MWl1DH-z_vQiKEaFOUKES3nmIKgcJG7BsYGqIMuzf4ZVfSt0L18A7NLqsBiZ_96CRDjA3oQbBRZY8Dpii2kFLxIGvibuyn62GPKl7exNK7T_hvvdlXD65baybj2V2LDpQVNqE="


@dataclass(frozen=True)
class Urls:
    """
    图片URL集合

    属性:
        bmiddle: 中等质量图片URL
        large: 大图URL
        largecover: 大封面图URL
        largest: 最大尺寸图片URL
        mw2000: 2000像素宽度图片URL
        original: 原始图片URL
        thumbnail: 缩略图URL
    """

    bmiddle: str
    large: str
    largecover: str
    largest: str
    mw2000: str
    original: str
    thumbnail: str

    def get_preferred_url(self, preference: List[str] | None = None) -> str:
        """
        获取首选图片URL

        Args:
            preference: URL类型偏好顺序，默认为["original", "largest", "large"]

        Returns:
            符合偏好的第一个可用URL

        Examples:
            url = urls.get_preferred_url(["original", "large"])
        """
        preference = preference or [
            "large",
            "original",
            "largest",
        ]
        for url_type in preference:
            if url := getattr(self, url_type, None):
                return url
        return self.thumbnail  # 最后兜底使用缩略图


@dataclass(frozen=True)
class Picture:
    """
    图片对象

    属性:
        pic_id: 图片唯一标识符
        urls: 图片URL集合
        size: 图片尺寸信息（可选）
        type: 图片类型（如"jpg", "png"）
    """

    pic_id: str
    urls: Urls
    size: Optional[Dict[str, int]] = None
    type: str = "jpg"

    def get_url(self, preference: List[str] | None = None) -> str:
        """获取首选图片URL"""
        return self.urls.get_preferred_url(preference)

    async def get_binary(self, url: str, client=None):
        """获取图片的二进制数据"""

        async def _get_client():
            if client:
                yield client
            else:
                async with httpx.AsyncClient() as temp_client:
                    yield temp_client

        try:
            async for c in _get_client():
                response = await c.get(url, headers=Auth.get_headers(), timeout=10.0)
                response.raise_for_status()
                path = httpx.URL(url).path
                filename = os.path.basename(path)
                return (filename, response.content)

        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            raise GetMblogsFailedError(f"HTTP请求失败: {status}") from e
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise GetMblogsFailedError("网络连接异常") from e
        except Exception as e:
            raise UnknownError("图片数据获取异常") from e

    @property
    def width(self) -> Optional[int]:
        """图片宽度（如有尺寸信息）"""
        return self.size["width"] if self.size and "width" in self.size else None

    @property
    def height(self) -> Optional[int]:
        """图片高度（如有尺寸信息）"""
        return self.size["height"] if self.size and "height" in self.size else None

    async def save(
        self, rename_as: str | None = None, parent: str = "weibo_images"
    ) -> Path:
        """将图片异步保存至本地"""
        root = Path(parent)
        if not root.exists():
            root.mkdir()
        url = self.get_url()
        result = await self.get_binary(url)
        if result is None:
            raise UnknownError("图片数据获取异常")
        filename, content = result
        extension = "." + filename.split(".")[-1]
        if rename_as is not None:
            filename = rename_as + extension
        async with aiofiles.open(root / filename, "wb") as f:
            await f.write(content)
            return root / filename

    async def to_base64(self) -> str:
        """将图片转为base64"""

        url = self.get_url()
        result = await self.get_binary(url)
        if result is None:
            raise UnknownError("图片数据获取异常")
        _, data = result
        return base64.b64encode(data).decode()


@dataclass
class Blog:
    """
    微博条目

    属性:
        mblogid: 微博唯一标识符
        text_raw: 原始文本内容
        pic_list: 图片列表
        created_at: 创建时间字符串（格式：Wed Aug 06 00:01:13 +0800 2025）
        source: 发布来源（如"iPhone客户端"）
        attitudes_count: 点赞数
        comments_count: 评论数
        reposts_count: 转发数
    """

    mblogid: str
    text_raw: str
    url: str
    pic_list: List[Picture] = field(default_factory=list)
    created_at: str = ""

    # 缓存解析后的时间对象
    _parsed_datetime: Optional[datetime] = field(
        default=None, compare=False, repr=False
    )

    @classmethod
    def from_api_data(cls, data: Dict[str, Any]) -> Blog:
        """
        从API数据创建Blog对象

        Args:
            data: 原始API返回的微博数据

        Returns:
            Blog实例

        Examples:
            blog = Blog.from_api_data(api_response["data"]["list"][0])
        """
        # 解析图片
        pic_list = []
        pic_infos = data.get("pic_infos", {})
        for pic_info in pic_infos.values():
            urls = Urls(
                bmiddle=pic_info.get("bmiddle", {}).get("url", ""),
                large=pic_info.get("large", {}).get("url", ""),
                largecover=pic_info.get("largecover", {}).get("url", ""),
                largest=pic_info.get("largest", {}).get("url", ""),
                mw2000=pic_info.get("mw2000", {}).get("url", ""),
                original=pic_info.get("original", {}).get("url", ""),
                thumbnail=pic_info.get("thumbnail", {}).get("url", ""),
            )
            pic_list.append(
                Picture(
                    pic_id=pic_info.get("pid", ""),
                    urls=urls,
                    size=pic_info.get("size"),
                    type=pic_info.get("type", "jpg"),
                )
            )

        # 创建Blog实例
        return cls(
            mblogid=data["mblogid"],
            text_raw=data.get("text_raw", data.get("text", "")),
            url=data.get("url", ""),
            pic_list=pic_list,
            created_at=data.get("created_at", ""),
        )

    @property
    def get_datetime(self) -> Optional[datetime]:
        """
        解析后的时间对象（北京时间）

        Returns:
            datetime对象或None

        注意:
            第一次访问时解析，后续使用缓存
        """
        if self._parsed_datetime is not None:
            return self._parsed_datetime

        if not self.created_at:
            return None

        try:
            # 处理微博时间格式: "Wed Aug 06 00:01:13 +0800 2025"
            clean_time_str = re.sub(r"\s+", " ", self.created_at).strip()
            # 先解析为UTC时间
            dt = datetime.strptime(clean_time_str, "%a %b %d %H:%M:%S %z %Y")
            # 转换为北京时间
            self._parsed_datetime = dt.astimezone(Auth.BEIJING_TZ)
            return self._parsed_datetime
        except (ValueError, TypeError):
            return None

    @property
    def is_today(self) -> bool:
        """是否是今天发布的微博"""
        if not self.get_datetime:
            return False

        today = datetime.now(tz=Auth.BEIJING_TZ).date()
        return self.get_datetime.date() == today

    @property
    def has_pictures(self) -> bool:
        """是否有图片"""
        return bool(self.pic_list)

    def get_text_summary(self, max_length: int = 50) -> str:
        """
        获取文本摘要

        Args:
            max_length: 摘要最大长度

        Returns:
            截断后的文本摘要（如有省略添加...）
        """
        if len(self.text_raw) <= max_length:
            return self.text_raw
        return self.text_raw[: max_length - 2] + "..."

    def get_preferred_pictures(self, preference: List[str] | None = None) -> List[str]:
        """
        获取首选图片URL列表

        Args:
            preference: URL类型偏好顺序

        Returns:
            首选图片URL列表
        """
        return [pic.get_url(preference) for pic in self.pic_list]

    async def fetch_long_text(
        self, client: Optional[httpx.AsyncClient] = None
    ) -> str | None:
        """
        获取长文本内容

        Args:
            client: 可选的httpx客户端（用于复用连接）

        Returns:
            长文本内容或空字符串

        Raises:
            GetMblogsFailedError: 获取失败
            UnknownError: 未知错误
        """

        api = "https://weibo.com/ajax/statuses/longtext"
        params = {"id": self.mblogid}

        async def _get_client():
            if client:
                yield client
            else:
                async with httpx.AsyncClient() as temp_client:
                    yield temp_client

        try:
            async for c in _get_client():
                response = await c.get(
                    api, headers=Auth.get_headers(), params=params, timeout=10.0
                )
                response.raise_for_status()
                content = response.json()

                if content.get("ok") != 1:
                    error_msg = content.get("msg", "数据加载失败")
                    raise GetMblogsFailedError(f"获取长文本失败: {error_msg}")

                return content.get("data", {}).get("longTextContent", "")

        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            raise GetMblogsFailedError(f"HTTP请求失败: {status}") from e
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise GetMblogsFailedError("网络连接异常") from e
        except Exception as e:
            raise UnknownError("长文本获取异常") from e

    async def save_all_images(self) -> List[Path]:
        """将所有图片保存至本地，返回一个Path的列表"""
        tasks = [asyncio.create_task(pic.save()) for pic in self.pic_list]
        results = await asyncio.gather(*tasks)
        return results

    async def fetch_images_binary_list(self) -> List[bytes]:
        """获取当前文章内所有图片的二进制数据列表"""
        tasks = [
            asyncio.create_task(pic.get_binary(pic.get_url())) for pic in self.pic_list
        ]
        results = await asyncio.gather(*tasks)
        results = [i[1] for i in results if i is not None]
        return results

    async def fetch_images_base64_list(self) -> List[str]:
        """获取当前文章内所有图片的base64列表"""

        tasks = [asyncio.create_task(pic.to_base64()) for pic in self.pic_list]
        results = await asyncio.gather(*tasks)
        return results
