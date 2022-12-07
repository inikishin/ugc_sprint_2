import uuid
from typing import Optional

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class ConfigMixin(BaseModel):

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class FilmPerson(ConfigMixin):
    id: uuid.UUID
    name: str


class Genre(ConfigMixin):
    id: uuid.UUID
    name: str


class Film(ConfigMixin):
    id: uuid.UUID
    imdb_rating: Optional[float]
    genre: list[Genre]
    title: str
    description: Optional[str]
    director: list[str]
    actors_names: list[str]
    writers_names: list[str]
    directors: list[FilmPerson]
    actors: list[FilmPerson]
    writers: list[FilmPerson]


class PersonRole(BaseModel):
    role: str
    film_ids: list[uuid.UUID]


class Person(BaseModel):
    id: uuid.UUID
    full_name: str
    roles: list[PersonRole]
