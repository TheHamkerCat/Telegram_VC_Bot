# Telegram Voice-Chat Bot [FFMPEG]

Telegram Voice-Chat Bot To Play Music From Various Sources In Your Group.

<img src="https://dl.hamker.in/files/8sug65vr.png" width="500" height="300">

### Environment requirements
- Linux-based OS. **You cannot run this on Windows natively, Use WSL or 
  Docker**
- Python 3.9 or later.
- ffmpeg package, look below for instructions.


## Run (Assuming you have a debian-based distro)

#### I recommend using Docker, but do this if you know what you're doing.
```sh
$ git clone https://github.com/thehamkercat/Telegram_VC_Bot
$ cd Telegram_VC_Bot
$ sudo apt-get install ffmpeg
$ pip3 install -U pip
$ pip3 install -U -r requirements.txt
$ cp sample_config.py config.py
```
Edit **config.py** with your own values.

```sh
$ python3 main.py
```

## Heroku

Read this -> https://t.me/TGVCSupport/17542

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/thehamkercat/Telegram_VC_Bot/tree/master)


Send [commands](https://github.com/thehamkercat/Telegram_VC_Bot/blob/master/README.md#commands) to bot to 
play music.


## Docker

```sh
$ git clone https://github.com/thehamkercat/Telegram_VC_Bot && cd Telegram_VC_Bot
$ cp sample.env .env
```
Edit **.env** with your own values.

```sh
$ sudo docker build . -t tgvc-bot
$ sudo docker run tgvc-bot
```
To stop use `CTRL+C`


## Commands
Command | Description
:--- | :---
/help | Show Help Message.
/skip | Skip Any Playing Music.
/play [SONG_NAME] | To Play A Song Using Saavn.<br>Service used can be changed in config (`DEFAULT_SERVICE`).
/play youtube/saavn [SONG_NAME] | To Play A Song Using Specific Service.
/play [with reply to an audio file] | To Play A Song With TG Audio File.
/queue | Check Queue Status.
/delqueue | Deletes Queue List and Playlist.
/playlist [songs name separated by line] | Start Playing Playlist.


## Note

1. If you want any help you can ask [here](https://t.me/tgvcsupport)

## Credits

1. Thanks to everyone who contributed to the project.
