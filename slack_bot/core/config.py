import os
import pathlib
from functools import lru_cache
from langchain_openai import ChatOpenAI
import motor.motor_asyncio
from pymongo import MongoClient

from dotenv import load_dotenv


load_dotenv()

class BaseConfig:
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.parent
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
    SIGNING_SECRET = os.getenv('SIGNING_SECRET')
    SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
    SERVICE_ACCOUNT_INFO = {
        "type": os.getenv("SERVICE_ACCOUNT_INFO_TYPE"),
        "project_id": os.getenv("SERVICE_ACCOUNT_INFO_PROJECT_ID"),
        "private_key_id": os.getenv("SERVICE_ACCOUNT_INFO_PRIVATE_KEY_ID"),
        "private_key": os.getenv("SERVICE_ACCOUNT_INFO_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("SERVICE_ACCOUNT_INFO_CLIENT_EMAIL"),
        "client_id": os.getenv("SERVICE_ACCOUNT_INFO_CLIENT_ID"),
        "auth_uri": os.getenv("SERVICE_ACCOUNT_INFO_AUTH_URI"),
        "token_uri": os.getenv("SERVICE_ACCOUNT_INFO_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("SERVICE_ACCOUNT_INFO_AUTH_PROVIDER"),
        "client_x509_cert_url": os.getenv("SERVICE_ACCOUNT_INFO_CLIENT_CERT_URL"),
        "universe_domain": os.getenv("SERVICE_ACCOUNT_INFO_UNIVERSE_DOMAIN"),
    }
    LLM_MINI = ChatOpenAI(model="gpt-4.1-mini", temperature=0.3, use_responses_api=True)
    DB_CLIENT = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_DB_URL")).slack
    MONGO_CLIENT = MongoClient(os.getenv('MONGO_DB_URL'))
    BREVO_API_KEY = os.getenv('BREVO_API_KEY')

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


