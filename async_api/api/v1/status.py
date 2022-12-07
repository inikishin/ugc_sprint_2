from pydantic import BaseModel


FILM_DETAILS_NOT_FOUND = 'film not found'
PERSON_DETAILS_NOT_FOUND = 'person not found'
GENRE_DETAILS_NOT_FOUND = 'genre not found'


class Message(BaseModel):
    detail: str
