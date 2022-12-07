from http import HTTPStatus
import uuid

from fastapi import APIRouter, Depends, Query, HTTPException

from db.cache import cache
from api.v1.status import GENRE_DETAILS_NOT_FOUND, Message
from models.response_models import Genre
from services.genres import BaseGenreService, get_genre_service


router = APIRouter()


@router.get('/',
            response_model=list[Genre],
            summary='Список жанров',
            description="""Возвращает полный список жанров""",
            )
@cache.cached
async def all_genres(
        page_number: int = Query(default=1, alias='page[number]'),
        page_size: int = Query(default=50, alias='page[size]'),
        genre_service: BaseGenreService = Depends(get_genre_service)
) -> list[Genre]:
    """
    Список жанров
    """

    genres = await genre_service.get_genres(
        page_number=page_number,
        page_size=page_size,
    )

    if not genres:
        return []

    return [
        Genre(
            uuid=genre.id,
            name=genre.name,
        ) for genre in genres
    ]


@router.get(
    '/{genre_id}',
    responses={
        HTTPStatus.OK.value: {'response': Genre},
        HTTPStatus.NOT_FOUND.value: {'response': Message}
    },
    summary='Данные по конкретному жанру',
    description="""Возвращает данные по конкретному жанру""",
)
@cache.cached
async def genre_details(
        genre_id: uuid.UUID,
        genre_service: BaseGenreService = Depends(get_genre_service)) -> Genre:
    """
    Данные по конкретному жанру

    genre_id: uuid
    """

    genre = await genre_service.get_by_id(str(genre_id))

    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=GENRE_DETAILS_NOT_FOUND)

    return Genre(
        uuid=genre.id,
        name=genre.name
    )
