from functools import lru_cache
from typing import Optional, Any
from abc import abstractmethod, ABC

from elasticsearch import NotFoundError
from fastapi import Depends, HTTPException

from db.storage import get_storage, BaseStorage
from models.films import Person, Film
from helpers.service_helper import generate_sort_field


class BasePersonService(ABC):

    @abstractmethod
    async def get_by_id(self, person_id: str) -> Optional[Person]:
        pass

    @abstractmethod
    async def get_persons(
        self,
        query_string: str = None,
        filters: dict = None,
        sort: str = None,
        page_number: int = 1,
        page_size: int = 50
    ) -> Optional[list]:
        pass

    @abstractmethod
    async def get_person_films(
        self,
        person_id: str,
        page_number: int = 1,
        page_size: int = 50
    ) -> Optional[list]:
        pass


class ElasticPersonService(BasePersonService):

    def __init__(self, adapter: BaseStorage):
        self.elastic = adapter.get_connection()

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._get_person_from_elastic(person_id)
        if not person:
            return None

        return person

    async def _get_person_from_elastic(
            self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get('persons', person_id)
        except NotFoundError:
            return None

        return Person(**doc['_source'])

    async def _get_persons_from_elastic(
            self, query: dict,
            sort: Optional[str] = None,
            page_number: int = 1, page_size: int = 50) -> Optional[list]:
        try:
            persons = await self.elastic.search(
                index='persons',
                body={'query': query},
                from_=(page_number - 1) * page_size,
                size=page_size,
                sort=sort
            )
        except NotFoundError:
            return None

        return [
            Person(**doc['_source']) for doc in persons.get('hits').get('hits')
        ]

    async def get_persons(self,
                          query_string: str = None,
                          filters: dict = None,
                          sort: str = None,
                          page_number: int = 1,
                          page_size: int = 50) -> Optional[list]:

        sort_field = generate_sort_field(sort, ['name']) if sort else None

        query: dict[str, Any] = {}

        if filters:
            query['bool'] = {
                'must': [
                    {'match': {filters.get('field'): filters.get('value')}}
                ]
            }

        if query_string:
            query['query_string'] = {
                'query': f'*{query_string}*',
                'fields': ['full_name']
            }

        if len(query.keys()) == 0:
            query['match_all'] = {}

        return await self._get_persons_from_elastic(query=query,
                                                    sort=sort_field,
                                                    page_number=page_number,
                                                    page_size=page_size)

    async def get_person_films(self,
                               person_id: str,
                               page_number: int = 1,
                               page_size: int = 50) -> Optional[list]:
        person = await self.get_by_id(person_id)

        if person is None:
            return []

        ids = set()
        for role in person.roles:
            for film_id in role.film_ids:
                ids.add(str(film_id))

        query = {
            'bool': {
                'filter': {
                    'ids': {
                        'values': list(ids)
                    }
                }
            }
        }

        try:
            films = await self.elastic.search(
                index='movies',
                body={'query': query},
                from_=(page_number - 1) * page_size,
                size=page_size,
            )
        except NotFoundError:
            return []

        return [
            Film(**doc['_source']) for doc in films.get('hits').get('hits')
        ]


@lru_cache()
def get_person_service(
        adapter: BaseStorage = Depends(get_storage),
) -> BasePersonService:
    return ElasticPersonService(adapter)
