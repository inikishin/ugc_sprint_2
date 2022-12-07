FROM python:3.9.13-slim-buster

WORKDIR /data

RUN apt-get update
RUN apt-get -y install curl

RUN groupadd -r api_group && useradd -d /data -r -g api_group api_user \
    && chown api_user:api_group -R /data

USER api_user

COPY requirements.txt requirements.txt

ENV PATH "/data/.local/bin:$PATH"

RUN pip3 install -r requirements.txt --user --no-cache-dir --no-warn-script-location

EXPOSE 8000

WORKDIR /data/async_api

CMD [ "gunicorn", "main:app", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker" ]
