FROM python:3.6-slim

WORKDIR /code

COPY src/ .

COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/code/entrypoint.sh"]
