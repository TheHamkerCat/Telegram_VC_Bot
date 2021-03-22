FROM python:3.9.2-slim-buster

WORKDIR /app

ENV PIP_NO_CACHE_DIR 1

RUN pip3 install --upgrade pip setuptools

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN apt-get update \
 && apt-get install -y ffmpeg \
 && apt-get clean

COPY . .

RUN cp sample_config.py config.py

CMD ["python3", "main.py"]
