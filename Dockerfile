FROM python:3.7.12-slim-buster
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y sqlite3 libsqlite3-dev
WORKDIR /dir
COPY . ./
RUN pip install -r ./requirements.txt

CMD ["python","-m", "src.__init__", "test/data/data.csv", "1800", "1000", "True"]
