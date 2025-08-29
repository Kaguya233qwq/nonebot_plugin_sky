from pathlib import Path


class Config:
    BASE_PATH = Path(__file__).parent.parent
    SKY_ROOT_PATH = Path("Sky")
    RESOURCE_PATH = BASE_PATH / "resources"
    IMAGES_PATH = RESOURCE_PATH / "images"
    
    CONFIG_FILE = SKY_ROOT_PATH / "config.ini"
    TEMPLATE_FILE = SKY_ROOT_PATH / "cmd_template.txt"
