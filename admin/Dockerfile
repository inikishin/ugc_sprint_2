FROM python:3.9.13-slim-buster

WORKDIR /data

RUN apt-get update
RUN apt-get -y install curl nginx

COPY ./admin/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir --no-warn-script-location

COPY ./admin .
RUN python manage.py collectstatic --noinput

COPY ./admin/nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./admin/nginx/site.conf /etc/nginx/conf.d/site.conf

EXPOSE 80

CMD ["./entrypoint.sh"]
