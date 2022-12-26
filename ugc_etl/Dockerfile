FROM python:3.9.13-slim-buster

WORKDIR /app

COPY ./ugc_etl/requirements.txt requirements.txt

RUN apt-get update
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./ugc_etl .

CMD python main.py