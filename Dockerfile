FROM python:3.8.5-slim

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /app

RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install --system

ADD . /app

CMD uvicorn --host=0.0.0.0 main:app --log-level debug --reload
