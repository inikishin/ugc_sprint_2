import os

from extract import Extract
from load import Load
from transform import Transform


class ETL:
    def __init__(self):
        self.load = Load(host=os.getenv('CLICKHOUSE_HOST', 'localhost'))
        self.transform = Transform()
        self.extract = Extract(transform=self.transform,
                               load=self.load,
                               host=os.getenv('KAFKA_HOST', 'localhost:9092'))

    def run(self):
        self.extract.run()


etl = ETL()
etl.run()
