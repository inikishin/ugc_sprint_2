from functools import lru_cache
import os

from aiokafka import AIOKafkaProducer
import asyncio

from core.constants import TOPIC_BOOKMARKS, TOPIC_RATING, TOPIC_VIEWS, TOPIC_LAST_VIEW


class EventService:
    def __init__(self, servers: list[str]):
        self.producer = AIOKafkaProducer(bootstrap_servers=servers)

    async def _async_send_message(self,
                                  topic: str,
                                  key: str,
                                  value: str) -> None:
        await self.producer.start()
        try:
            await self.producer.send_and_wait(
                topic=topic,
                value=value.encode('UTF-8'),
                key=key.encode('UTF-8'),
            )
        finally:
            await self.producer.stop()

    async def _send_message(self, topic: str, key: str, value: str) -> None:
        asyncio.run(self._async_send_message(topic, key, value))

    def send_rating(self, user_id: str, movie_id: str, rating: float) -> None:
        self._send_message(TOPIC_RATING,
                           user_id,
                           f'{movie_id}+{str(rating)}')

    def send_history(self, user_id: str, movie_id: str, viewed: int) -> None:
        self._send_message(TOPIC_VIEWS,
                           user_id,
                           f'{movie_id}+{str(viewed)}')

    def send_bookmark(self, user_id: str, movie_id: str) -> None:
        self._send_message(TOPIC_BOOKMARKS,
                           user_id,
                           movie_id)

    def send_last_view_time(self, user_id: str, movie_id: str, paused_sec: int) -> None:
        self._send_message(TOPIC_LAST_VIEW,
                           user_id,
                           f'{movie_id}+{str(paused_sec)}')


@lru_cache()
def get_event_service() -> EventService:
    return EventService(
        [os.getenv('KAFKA_SERVER', 'localhost:9092')]
    )
