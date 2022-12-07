import json


def generate_bulk_body(index: str, data: list) -> str:
    """Генерация строки для массовой вставки данных согласно документации
    https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html

    https://elasticsearch-py.readthedocs.io/en/master/async.html#elasticsearch.AsyncElasticsearch.bulk
    """
    operations = [json.dumps({"index": {"_index": index, "_id": item["_id"]}})
                  + '\n'
                  + json.dumps(item['data']) for item in data]
    return '\n'.join(operations)
