import time

import backoff
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from backoff_hdlr import backoff_hdlr
from constants import TOPIC_BOOKMARKS, TOPIC_RATING, TOPIC_VIEWS, TOPIC_LAST_VIEW
from config import logger


class Extract:
    @backoff.on_exception(backoff.expo,
                          [NoBrokersAvailable, ValueError],
                          on_backoff=backoff_hdlr)
    def __init__(self, transform, load, host):
        self.extract = KafkaConsumer(
            TOPIC_BOOKMARKS, TOPIC_RATING, TOPIC_VIEWS, TOPIC_LAST_VIEW,
            bootstrap_servers=[host],
            auto_offset_reset='earliest',
            group_id='etl-clickhouse',
            enable_auto_commit=False,
        )
        self.transform = transform
        self.load = load

    @backoff.on_exception(backoff.expo,
                          [NoBrokersAvailable, ValueError],
                          on_backoff=backoff_hdlr)
    def run(self):
        mem_storage = {
            TOPIC_BOOKMARKS: [],
            TOPIC_RATING: [],
            TOPIC_VIEWS: [],
            TOPIC_LAST_VIEW: []
        }
        last_insert = time.time()

        for message in self.extract:
            if message.topic == TOPIC_BOOKMARKS:
                data = self.transform.get_bookmark_data(message.key.decode('utf-8'),
                                                        message.value.decode('utf-8'))
                mem_storage[TOPIC_BOOKMARKS].append(data)
            elif message.topic == TOPIC_RATING:
                data = self.transform.get_rating_data(message.key.decode('utf-8'),
                                                      message.value.decode('utf-8'))
                mem_storage[TOPIC_RATING].append(data)
            elif message.topic == TOPIC_VIEWS:
                data = self.transform.get_history_data(message.key.decode('utf-8'),
                                                       message.value.decode('utf-8'))
                mem_storage[TOPIC_VIEWS].append(data)
            elif message.topic == TOPIC_LAST_VIEW:
                data = self.transform.get_last_view_time_data(message.key.decode('utf-8'),
                                                              message.value.decode('utf-8'))
                mem_storage[TOPIC_LAST_VIEW].append(data)
            else:
                logger.warning('Unknown topic: %s', message.topic)
                logger.warning('Message:')
                logger.warning('key: %s', message.key.decode('utf-8'))
                logger.warning('value: %s', message.value.decode('utf-8'))

            # Данные в click house отправляем батчами раз в 60 секунд
            data_len = 0
            for topic_values in mem_storage.values():
                data_len += len(topic_values)

            if (data_len >= 10_000) or ((time.time() - last_insert) > 60):
                for topic in mem_storage:
                    self.load.insert_data(topic, mem_storage[topic])

                mem_storage = {
                    TOPIC_BOOKMARKS: [],
                    TOPIC_RATING: [],
                    TOPIC_VIEWS: [],
                    TOPIC_LAST_VIEW: []
                }
                last_insert = time.time()
                self.extract.commit()
