# Telegram Voice-Chat Bot [WIP]

Just Another [Obviously better!] Telegram Voice-Chat Bot To Play Music From Various Sources In Your Group

<img src="tg_vc_bot.png" width="300" height="300">

## Requirements

- Python 3.6 or higher
- A [Telegram API key](//docs.pyrogram.org/intro/setup#api-keys)
- A [Telegram bot token](//t.me/botfather)
- `mpv media player` Install it From Your Linux Repository.

## Run

1. `git clone https://github.com/thehamkercat/Telegram_VC_Bot`, to download the source code.
2. `cd Telegram_VC_Bot`, to enter the directory.
3. `pip3 install -r requirements.txt`, to install the requirements.
4. `cp sample_config.ini config.ini`
5. `cp sample_config.py config.py`
5. Edit `config.ini` and `config.py` with your own values.
6. Follow [This](https://unix.stackexchange.com/questions/82259/how-to-pipe-audio-output-to-mic-input) to route your PC or Server's audio output to audio input.
7. Run JioSaavn Server `python3 plugins/app.py` Only do this if you want to play songs from JioSaavn too 
8. Run the bot `python3 tgvcbot.py`
9. Open Telegram and start voice chat.
10. Send commands to bot to play music.


## Commands

1. `/help` To show help screen.
2. `/stop` To stop any playing music. 
3. `/jiosaavn <song_name>` To play music from JioSaavn.
4. `/ytsearch <song_name>` To search for a song on Youtube.
5. `/youtube <song_link>` To play a song from YouTube.


## Note

1. More services will be added soon.

## Credits
1. `https://github.com/cyberboysumanjay/JioSaavnAPI` [For JioSaavnAPI]
