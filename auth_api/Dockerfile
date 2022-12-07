FROM python:3.9.13-slim-buster

WORKDIR /data

RUN apt-get update
RUN apt-get -y install curl

RUN groupadd -r api_group && useradd -d /data -r -g api_group api_user \
    && chown api_user:api_group -R /data

USER api_user

COPY ./auth_api/requirements.txt requirements.txt

ENV PATH "/data/.local/bin:$PATH"

RUN pip3 install -r requirements.txt --user --no-cache-dir --no-warn-script-location

COPY ./auth_api .

# logging
RUN mkdir /data/log
RUN touch /data/log/access_print.log
RUN touch /data/log/error_print.log
RUN touch /data/log/output_print.log

EXPOSE 8000

CMD ["./entrypoint.sh"]
