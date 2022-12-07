import uuid
from typing import Any

genres_data_ids = [str(uuid.uuid4()) for i in range(3)]
persons_data_ids = [str(uuid.uuid4()) for i in range(5)]
films_data_ids = [str(uuid.uuid4()) for i in range(3)]

genres_data: list[dict[str, Any]] = [
    {"_id": genres_data_ids[0],
     "data": {"id": genres_data_ids[0], "name": "action"}},
    {"_id": genres_data_ids[1],
     "data": {"id": genres_data_ids[1], "name": "drama"}},
    {"_id": genres_data_ids[2],
     "data": {"id": genres_data_ids[2], "name": "comedy"}},
]

persons_data: list[dict[str, Any]] = [
    {"_id": persons_data_ids[0],
     "data": {
         "id": persons_data_ids[0],
         "full_name": "test person 1",
         "roles": [{"role": "director", "film_ids": films_data_ids}],
     }},
    {"_id": persons_data_ids[1],
     "data": {
         "id": persons_data_ids[1],
         "full_name": "test person 2",
         "roles": [{"role": "actor", "film_ids": films_data_ids}],
     }},
    {"_id": persons_data_ids[2],
     "data": {
         "id": persons_data_ids[2],
         "full_name": "test person 3",
         "roles": [{"role": "writer", "film_ids": films_data_ids}],
     }},
    {"_id": persons_data_ids[3],
     "data": {
         "id": persons_data_ids[3],
         "full_name": "test person 4",
         "roles": [{"role": "actor", "film_ids": films_data_ids}],
     }},
    {"_id": persons_data_ids[4],
     "data": {
         "id": persons_data_ids[4],
         "full_name": "test person 5",
         "roles": [{"role": "actor", "film_ids": films_data_ids}],
     }},
]

films_data: list[dict[str, Any]] = [
    {
        "_id": films_data_ids[0],
        "data": {
            "id": films_data_ids[0],
            "imdb_rating": 7,
            "genre": [
                genres_data[0]['data'],
                genres_data[1]['data'],
            ],
            "title": "test title 3",
            "description": "test description 3",
            "director": [persons_data[0]['data']["full_name"]],
            "actors_names": [persons_data[1]['data']["full_name"]],
            "writers_names": [persons_data[2]['data']["full_name"]],
            "directors": [{"id": persons_data[0]['data']['id'],
                           "name": persons_data[0]['data']['full_name']}],
            "actors": [{"id": persons_data[1]['data']['id'],
                        "name": persons_data[1]['data']['full_name']}],
            "writers": [{"id": persons_data[2]['data']['id'],
                         "name": persons_data[2]['data']['full_name']}]
        }
    },
    {
        "_id": films_data_ids[1],
        "data": {
            "id": films_data_ids[1],
            "imdb_rating": 8,
            "genre": [
                genres_data[2]['data'],
                genres_data[1]['data'],
            ],
            "title": "test title 5",
            "description": "test description 5",
            "director": [persons_data[0]['data']["full_name"]],
            "actors_names": [persons_data[1]['data']["full_name"]],
            "writers_names": [persons_data[2]['data']["full_name"]],
            "directors": [{"id": persons_data[0]['data']['id'],
                           "name": persons_data[0]['data']['full_name']}],
            "actors": [{"id": persons_data[1]['data']['id'],
                        "name": persons_data[1]['data']['full_name']}],
            "writers": [{"id": persons_data[2]['data']['id'],
                         "name": persons_data[2]['data']['full_name']}]
        }
    },
    {
        "_id": films_data_ids[2],
        "data": {
            "id": films_data_ids[2],
            "imdb_rating": 9,
            "genre": [
                genres_data[0]['data'],
                genres_data[2]['data'],
            ],
            "title": "test title 10",
            "description": "test description 10",
            "director": [persons_data[0]['data']["full_name"]],
            "actors_names": [persons_data[1]['data']["full_name"]],
            "writers_names": [persons_data[2]['data']["full_name"]],
            "directors": [{"id": persons_data[1]['data']['id'],
                           "name": persons_data[1]['data']['full_name']}],
            "actors": [{"id": persons_data[2]['data']['id'],
                        "name": persons_data[2]['data']['full_name']}],
            "writers": [{"id": persons_data[4]['data']['id'],
                         "name": persons_data[4]['data']['full_name']}]
        }
    },
]
