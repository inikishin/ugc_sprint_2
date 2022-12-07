from pydantic import BaseSettings, BaseModel, Field


class OauthYandex(BaseModel):
    oauth_url: str = 'https://oauth.yandex.ru/'
    login_url: str = 'https://login.yandex.ru/'
    client_id: str
    client_secret: str


class Settings(BaseSettings):
    oauth_yandex: OauthYandex

    class Config:
        case_sensitive = False
        env_file_encoding = 'utf-8'
        env_file = '.env'
        env_nested_delimiter = '__'
