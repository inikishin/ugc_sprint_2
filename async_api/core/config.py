import os
from logging import config as logging_config
from pydantic import BaseSettings

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):

    PROJECT_NAME: str = os.getenv('PROJECT_NAME', 'movies')

    REDIS_HOST: str = os.getenv('REDIS_HOST', '127.0.0.1')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD: str = os.getenv('REDIS_PASSWORD', '')

    ELASTIC_HOST: str = os.getenv('ELASTIC_HOST', '127.0.0.1')
    ELASTIC_PORT: int = int(os.getenv('ELASTIC_PORT', 9200))
    ELASTIC_USERNAME: str = os.getenv('ELASTIC_USERNAME', '')
    ELASTIC_PASSWORD: str = os.getenv('ELASTIC_PASSWORD', '')

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    FILM_CACHE_EXPIRE_IN_SECONDS: int = 60 * 5  # 5 минут


cfg = Settings()
