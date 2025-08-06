FROM python:3.13

RUN mkdir -p /usr/src/api
WORKDIR /usr/src/api

COPY requirements.txt /usr/src/api

RUN pip3 install -r requirements.txt

COPY ./api /usr/src/api
COPY ./tools /usr/src/api

CMD ["fastapi", "run", "api.py"]