from pydantic import BaseModel


class MovieRating(BaseModel):
    movie_id: str
    user_id: str
    rating: float


class MovieHistory(BaseModel):
    movie_id: str
    user_id: str
    viewed: int


class MovieBookmark(BaseModel):
    movie_id: str
    user_id: str


class MovieLastViewTime(BaseModel):
    movie_id: str
    user_id: str
    paused_sec: int


class SuccessResponse(BaseModel):
    msg: str = "Success"
