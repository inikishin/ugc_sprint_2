from pydantic import BaseModel


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str


class WhoResponse(BaseModel):
    auth: bool
    user: dict
