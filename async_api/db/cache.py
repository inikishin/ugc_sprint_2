import logging
from abc import abstractmethod, ABC
from typing import Any, Callable

from aiocache import caches, cached
from aiocache.plugins import BasePlugin


from core.config import Settings, cfg


class BaseCache(ABC):

    @abstractmethod
    def cached(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Декоратор для кэширования
        """
        pass

    @abstractmethod
    async def clear(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    def get_hits(self) -> int:
        pass

    @abstractmethod
    def get_total(self) -> int:
        pass


class CacheLoggingPlugin(BasePlugin):

    async def pre_set(self, *args, **kwargs):
        cache = caches.get('redis')
        logging.info('Cache Miss. Info: %s', cache.hit_miss_ratio)


class RedisCache(BaseCache):

    def __init__(self, config: Settings):
        caches.set_config({
            'default': {
                'cache': 'aiocache.SimpleMemoryCache',
                'serializer': {
                    'class': 'aiocache.serializers.StringSerializer'
                }
            },
            'redis': {
                'cache': 'aiocache.RedisCache',
                'endpoint': config.REDIS_HOST,
                'port': config.REDIS_PORT,
                'password': config.REDIS_PASSWORD,
                'timeout': 1,
                'ttl': config.FILM_CACHE_EXPIRE_IN_SECONDS,
                'serializer': {
                    'class': 'aiocache.serializers.PickleSerializer'
                },
                'plugins': [
                    {'class': 'aiocache.plugins.HitMissRatioPlugin'},
                    {'class': 'aiocache.plugins.TimingPlugin'},
                    {'class': 'db.cache.CacheLoggingPlugin'}
                ]
            }
        })

    def cached(self, func: Callable[..., Any]) -> Callable[..., Any]:
        return cached(alias='redis')(func)

    async def clear(self):
        await caches.get('redis').clear()

    async def close(self):
        await caches.get('redis').close()

    def get_hits(self) -> int:
        return caches.get('redis').hit_miss_ratio['hits']

    def get_total(self) -> int:
        return caches.get('redis').hit_miss_ratio['total']


cache: BaseCache = RedisCache(cfg)
