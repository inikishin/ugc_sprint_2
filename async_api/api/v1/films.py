import uuid
from typing import Optional
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from db.cache import cache
from api.v1.status import FILM_DETAILS_NOT_FOUND, Message
from models.response_models import FilmPerson, FilmGenre, Film, SearchItemFilm
from services.films import BaseFilmService, get_film_service


router = APIRouter()


@router.get('/',
            response_model=list[SearchItemFilm],
            summary='Список фильмов',
            description="""Возвращает отсортированный по рейтингу список
            фильмов, с возможностью отбора по жанру""",
            )
@cache.cached
async def all_films(
        sort: str = '-imdb_rating',
        genre: Optional[uuid.UUID] = Query(
            default=None, alias='filter[genre]'),
        page_number: int = Query(default=1, alias='page[number]'),
        page_size: int = Query(default=50, alias='page[size]'),
        film_service: BaseFilmService = Depends(get_film_service)
) -> list[SearchItemFilm]:
    """
    Главная страница

    sort: -imdb_rating or +imdb_rating,
    filter[genre]: uuid,
    page[number]: int,
    page[size]: int
    """
    films = await film_service.get_films(
        genre_filter_id=str(genre) if genre else None,
        sort=sort,
        page_number=page_number,
        page_size=page_size,
    )

    if not films:
        return []

    return [
        SearchItemFilm(
            uuid=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating
        ) for film in films
    ]


@router.get('/search',
            response_model=list[SearchItemFilm],
            summary='Поиск по фильмам',
            description="""Возвращает список найденных фильмов на основе
            запроса""",
            )
@cache.cached
async def film_search(
        query: str,
        page_number: int = Query(default=1, alias='page[number]'),
        page_size: int = Query(default=50, alias='page[size]'),
        film_service: BaseFilmService = Depends(get_film_service)
) -> list[SearchItemFilm]:
    """
    Поиск по фильмам

    query: str,
    page[number]: int,
    page[size]: int
    """

    films = await film_service.get_films(
        query_string=query,
        page_number=page_number,
        page_size=page_size,
    )

    if not films:
        return []

    return [
        SearchItemFilm(
            uuid=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating
        ) for film in films
    ]


@router.get(
    '/{film_id}',
    responses={
        HTTPStatus.OK.value: {'response': Film},
        HTTPStatus.NOT_FOUND.value: {'response': Message}
    },
    summary='Полная информация по фильму',
    description="""Возвращает полную информацию по фильму""",
)
@cache.cached
async def film_details(
        film_id: uuid.UUID,
        film_service: BaseFilmService = Depends(get_film_service)
) -> Film:
    """
    Полная информация по фильму

    film_id: uuid
    """
    film = await film_service.get_by_id(str(film_id))

    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=FILM_DETAILS_NOT_FOUND)

    return Film(
        uuid=film.id,
        imdb_rating=film.imdb_rating,
        genre=[
            FilmGenre(uuid=x.id, name=x.name) for x in film.genre
        ],
        title=film.title,
        description=film.description,
        directors=[
            FilmPerson(uuid=x.id, full_name=x.name) for x in film.directors
        ],
        actors=[
            FilmPerson(uuid=x.id, full_name=x.name) for x in film.actors
        ],
        writers=[
            FilmPerson(uuid=x.id, full_name=x.name) for x in film.writers
        ]
    )
