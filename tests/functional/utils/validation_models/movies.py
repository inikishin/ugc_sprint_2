from pydantic import BaseModel
import uuid


class Film(BaseModel):
    uuid: uuid.UUID
    title: str
    description: str
    imdb_rating: float
    genre: list
    directors: list
    actors: list
    writers: list


class FilmShort(BaseModel):
    uuid: uuid.UUID
    title: str
    imdb_rating: float


class Genre(BaseModel):
    uuid: uuid.UUID
    name: str


class Person(BaseModel):
    uuid: uuid.UUID
    full_name: str
    roles: list
