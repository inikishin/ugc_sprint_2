from functools import lru_cache
from typing import Optional, Any
from abc import abstractmethod, ABC

from elasticsearch import NotFoundError
from fastapi import Depends, HTTPException

from db.storage import get_storage, BaseStorage
from models.films import Genre
from helpers.service_helper import generate_sort_field


class BaseGenreService(ABC):

    @abstractmethod
    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        pass

    @abstractmethod
    async def get_genres(
        self,
        query_string: str = None,
        filters: dict = None,
        sort: str = None,
        page_number: int = 1,
        page_size: int = 50
    ) -> Optional[list]:
        pass


class ElasticGenreService(BaseGenreService):

    def __init__(self, adapter: BaseStorage):
        self.elastic = adapter.get_connection()

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        """
        Получаем экземпляр объекта Жанр по genre_id
        """
        genre = await self._get_genre_from_elastic(genre_id)
        if not genre:
            return None

        return genre

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        try:
            doc = await self.elastic.get('genres', genre_id)
        except NotFoundError:
            return None

        return Genre(**doc['_source'])

    async def _get_genres_from_elastic(self, query: dict,
                                       sort: Optional[str] = None,
                                       page_number: int = 1,
                                       page_size: int = 50) -> Optional[list]:
        try:
            genres = await self.elastic.search(
                index='genres',
                body={'query': query},
                from_=(page_number - 1) * page_size,
                size=page_size,
                sort=sort
            )
        except NotFoundError:
            return None

        return [
            Genre(**doc['_source']) for doc in genres.get('hits').get('hits')
        ]

    async def get_genres(self,
                         query_string: str = None,
                         filters: dict = None,
                         sort: str = None,
                         page_number: int = 1,
                         page_size: int = 50) -> Optional[list]:
        """
        Получаем список жанров, в зависимости от условий
        отбора и сортировки
        """

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
                'query': query_string,
                'fields': ['name']
            }

        if len(query.keys()) == 0:
            query['match_all'] = {}

        return await self._get_genres_from_elastic(query=query,
                                                   sort=sort_field,
                                                   page_number=page_number,
                                                   page_size=page_size)


@lru_cache()
def get_genre_service(
        adapter: BaseStorage = Depends(get_storage),
) -> BaseGenreService:
    return ElasticGenreService(adapter)
