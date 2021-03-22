FROM python:3.9.2-slim-buster

ENV PIP_NO_CACHE_DIR 1

RUN pip3 install --upgrade pip setuptools

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN apt-get install -y ffmpeg

COPY . .

CMD ["python3", "main.py"]
