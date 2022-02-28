FROM python:3.8-alpine

RUN mkdir -p /usr/src/app
COPY . /usr/src/app
WORKDIR /usr/src/app

RUN pip install .

EXPOSE 8081

CMD ["waitress-serve", "--port=8081", "--call", "src.physrisk_api.app:create_app"]
