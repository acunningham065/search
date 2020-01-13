FROM python:3.7

ADD . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 3306
EXPOSE 5025

ENTRYPOINT ["python3", "search.py"]