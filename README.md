# Telegram Voice-Chat Bot [WIP]

Just Another [Obviously better!] Telegram Voice-Chat Bot To Play Music From Various Sources In Your Group

## Requirements

- Python 3.6 or higher
- A [Telegram API key](//docs.pyrogram.org/intro/setup#api-keys)
- A [Telegram bot token](//t.me/botfather)
- `ffmpeg` and `mpv media player`

## Run

1. `git clone https://github.com/thehamkercat/Telegram_VC_Bot`, to download the source code.
2. `cd Telegram_VC_Bot`, to enter the directory.
3. `pip3 install -r requirements.txt`, to install the requirements.
4. `cp sample_config.ini config.ini`
5. `cp sample_config.py config.py`
5. Edit `config.ini` and `config.py` with your own values.
6. Follow [This](https://www.kirsle.net/redirect-audio-out-to-mic-in-linux) tutorial to route your PC or Server's audio output to audio input.
7. Run with `python3 tgvcbot.py`
8. Open Telegram and start voice chat.
9. Send commands to bot to play music.


## Commands

1. `/jiosaavn <song_name>` To play music from jiosaavn.


## Note

1. More services will be added soon.

## Credits
1. `https://github.com/cyberboysumanjay/JioSaavnAPI` [For JioSaavnAPI]
