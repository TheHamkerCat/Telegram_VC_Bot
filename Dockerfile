FROM ubuntu:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

#Installing Dependencies
RUN apt-get -qq update        
RUN DEBIAN_FRONTEND="noninteractive" apt-get -qq install -y ffmpeg opus-tools bpm-tools python3 python3-pip
RUN pip3 install -U pip

#Installing Requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

#Copying all source
COPY . .

CMD ["python3","main.py"]
