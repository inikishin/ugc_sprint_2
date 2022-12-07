from typing import Any
from abc import abstractmethod, ABC

from elasticsearch import AsyncElasticsearch

from core.config import Settings


class BaseStorage(ABC):

    @abstractmethod
    def get_connection(self) -> Any:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass


class EmptyStorage(BaseStorage):

    def get_connection(self) -> Any:
        return

    async def close(self) -> None:
        return


class ElasticStorage(BaseStorage):

    def __init__(self, cfg: Settings):
        elastic_conn_string = 'http://{user}:{password}@{host}:{port}/'.format(
            user=cfg.ELASTIC_USERNAME,
            password=cfg.ELASTIC_PASSWORD,
            host=cfg.ELASTIC_HOST,
            port=cfg.ELASTIC_PORT
        )
        self.elastic = AsyncElasticsearch(
            hosts=[elastic_conn_string]
        )

    def get_connection(self) -> Any:
        return self.elastic

    async def close(self) -> None:
        await self.elastic.close()


adapter: BaseStorage = EmptyStorage()


async def get_storage() -> BaseStorage:
    return adapter
