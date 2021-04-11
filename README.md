# Telegram Voice-Chat Bot [ Pytgcalls ]

Telegram Voice-Chat Bot To Play Music With Pytgcalls From Various Sources In Your Group.

<img src="https://hamker.me/wl9twld.png" width="600" height="400">


# Support

1. All linux based os.


## Requirements

- Telegram API_ID and API_HASH
- Python 3.7 or higher 
- Userbot Needs To Be Admin In The Chat
- Install **ffmpeg**

## Run


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


Send [commands](https://github.com/thehamkercat/Telegram_VC_Bot/blob/master/README.md#commands) to bot to 
play music.


## Commands
Command | Description
:--- | :---
/help | Show Help Message.
/skip | Skip Any Playing Music.
/play youtube/saavn/deezer [SONG_NAME] | To Play A Song.
/telegram | Play A Song Directly From Telegram File.
/queue | Check Queue Status.
/joinvc | Join Voice Chat.
/leavevc | Leave Voice Chat.
/volume [1-200] | Adjust Volume.
/pause | Pause Music.
/resume | Resume Music.
/update | Update & Restart.

## Note

1. If you want any help you can ask [here](https://t.me/tgvcsupport)

## Credits

1. @MarshalX [For TgCalls]
2. Everyone who contributed to the project.
