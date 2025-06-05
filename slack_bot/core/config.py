import os
import pathlib
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()

class BaseConfig:
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.parent
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
    SIGNING_SECRET = os.getenv('SIGNING_SECRET')


class DevelopmentConfig(BaseConfig):
    Issuer = "http://localhost:8000"
    Audience = "http://localhost:3000"


class ProductionConfig(BaseConfig):
    Issuer = ""
    Audience = ""


@lru_cache()
def get_settings() -> DevelopmentConfig | ProductionConfig:
    config_cls_dict = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
    }
    config_name = os.getenv('FASTAPI_CONFIG', default='development')
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()


