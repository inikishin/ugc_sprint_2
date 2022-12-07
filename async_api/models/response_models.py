import uuid
from typing import Optional

from models.films import ConfigMixin


class FilmPerson(ConfigMixin):
    uuid: uuid.UUID
    full_name: str


class FilmGenre(ConfigMixin):
    uuid: uuid.UUID
    name: str


class Film(ConfigMixin):
    uuid: uuid.UUID
    imdb_rating: Optional[float]
    genre: list[FilmGenre]
    title: str
    description: str
    directors: list[FilmPerson]
    actors: list[FilmPerson]
    writers: list[FilmPerson]


class SearchItemFilm(ConfigMixin):
    uuid: uuid.UUID
    title: str
    imdb_rating: Optional[float]


class Genre(ConfigMixin):
    uuid: uuid.UUID
    name: str


class PersonRole(ConfigMixin):
    role: str
    film_ids: list[uuid.UUID]


class Person(ConfigMixin):
    uuid: uuid.UUID
    full_name: str
    roles: list[PersonRole]


class PersonFilm(ConfigMixin):
    uuid: uuid.UUID
    title: str
    imdb_rating: Optional[float]
