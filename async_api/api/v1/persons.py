import uuid
from http import HTTPStatus
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException

from db.cache import cache
from api.v1.status import PERSON_DETAILS_NOT_FOUND, Message
from models.response_models import PersonRole, Person, PersonFilm
from services.persons import BasePersonService, get_person_service


router = APIRouter()


@router.get('/search',
            response_model=list[Person],
            summary='Поиск по персонам',
            description="""Поиск по персонам на основании предоставленного 
            значения в параметре запроса""",
            )
@cache.cached
async def person_search(
        query: str,
        page_number: int = Query(default=1, alias='page[number]'),
        page_size: int = Query(default=50, alias='page[size]'),
        person_service: BasePersonService = Depends(get_person_service)
) -> list[Person]:
    """
    Поиск по персонам

    query: str,
    page[number]: int,
    page[size]: int
    """

    persons = await person_service.get_persons(
        query_string=query,
        page_number=page_number,
        page_size=page_size,
    )

    if not persons:
        return []

    return [
        Person(
            uuid=person.id,
            full_name=person.full_name,
            roles=[
                PersonRole(role=role.role, film_ids=role.film_ids)
                for role in person.roles
            ]
        ) for person in persons
    ]


@router.get('/{person_id}/film',
            response_model=list[PersonFilm],
            summary='Фильмы по персоне',
            description="""Возвращает список фильмов для конкретной персоны""",
            )
@cache.cached
async def person_films_details(
        person_id: uuid.UUID,
        page_number: int = Query(default=1, alias='page[number]'),
        page_size: int = Query(default=50, alias='page[size]'),
        person_service: BasePersonService = Depends(get_person_service)
) -> list[PersonFilm]:
    """
    Фильмы по персоне

    person_id: uuid
    """

    films = await person_service.get_person_films(
        str(person_id),
        page_number,
        page_size)

    if not films:
        return []

    return [
        PersonFilm(
            uuid=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating
        ) for film in films
    ]


@router.get(
    '/{person_id}',
    responses={
        HTTPStatus.OK.value: {'response': Person},
        HTTPStatus.NOT_FOUND.value: {'response': Message}
    },
    summary='Данные по персоне',
    description="""Возвращает данные по конкретной персоне""",
)
@cache.cached
async def person_details(
        person_id: UUID,
        person_service: BasePersonService = Depends(get_person_service)
) -> Person:
    """
    Данные по персоне

    person_id: uuid
    """

    person = await person_service.get_by_id(str(person_id))

    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=PERSON_DETAILS_NOT_FOUND)

    return Person(
        uuid=person.id,
        full_name=person.full_name,
        roles=[
            PersonRole(role=role.role, film_ids=role.film_ids)
            for role in person.roles
        ]
    )
