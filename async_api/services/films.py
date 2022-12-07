from functools import lru_cache
from typing import Optional, Any
from abc import abstractmethod, ABC

from elasticsearch import NotFoundError
from fastapi import Depends, HTTPException

from db.storage import get_storage, BaseStorage
from models.films import Film
from helpers.service_helper import generate_sort_field

class BaseFilmService(ABC):

    @abstractmethod
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        pass

    @abstractmethod
    async def get_films(
        self,
        query_string: str = None,
        genre_filter_id: str = None,
        sort: str = None,
        page_number: int = 1,
        page_size: int = 50
    ) -> Optional[list]:
        pass


class ElasticFilmService(BaseFilmService):

    def __init__(self, adapter: BaseStorage):
        self.elastic = adapter.get_connection()

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._get_film_from_elastic(film_id)
        if not film:
            return None
        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def _get_films_from_elastic(self, query: dict,
                                      sort: Optional[str] = None,
                                      page_number: int = 1,
                                      page_size: int = 50) -> Optional[list]:
        try:
            films = await self.elastic.search(
                index='movies',
                body={'query': query},
                from_=(page_number - 1) * page_size,
                size=page_size,
                sort=sort
            )
        except NotFoundError:
            return None

        return [
            Film(**doc['_source']) for doc in films.get('hits').get('hits')
        ]

    async def get_films(self,
                        query_string: str = None,
                        genre_filter_id: str = None,
                        sort: str = None,
                        page_number: int = 1,
                        page_size: int = 50) -> Optional[list]:
        """
        Функция получения списка фильмов из elastic с различными параметрами.

        query_string: Строка для полнотекстового поиска по полям фильма

        genre_filter_id: Строка с id жанра

        sort: Параметр сортировки вида '<+ или -><имя_поля>'

        page_number: номер страницы

        page_size: число записей на странице

        return: Возвращает список фильмов
        """
        sort_field = generate_sort_field(sort, ['imdb_rating']) if sort else None

        query: dict[str, Any] = {}

        if genre_filter_id:
            query["nested"] = {
                "path": "genre",
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"genre.id": genre_filter_id}}
                        ]
                    }
                }
            }

        if query_string:
            query['query_string'] = {
                'query': query_string,
                'fields': ['title', 'description']
            }

        if len(query.keys()) == 0:
            query['match_all'] = {}

        return await self._get_films_from_elastic(query=query,
                                                  sort=sort_field,
                                                  page_number=page_number,
                                                  page_size=page_size)


@lru_cache()
def get_film_service(
        adapter: BaseStorage = Depends(get_storage),
) -> BaseFilmService:
    return ElasticFilmService(adapter)
