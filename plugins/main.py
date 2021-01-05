from __future__ import unicode_literals
import requests
import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from config import jio_saavn_api, sudo_chat_id
from youtube_search import YoutubeSearch
import youtube_dl

print("Bot Started!")
# Ping

@Client.on_message(filters.command(["ping"]) & (filters.chat(sudo_chat_id)))
async def ping(_, message: Message):
    j = await message.reply_text("Wait, Pinging all Datacenters`")
    result = ""
    for i in range(1, 6):
        datacenter = (f"https://cdn{i}.telesco.pe")
        ping1 = round(requests.head(datacenter).elapsed.total_seconds() * 1000)
        result += f'`DC{i} - {ping1}ms`\n'
    await j.edit(result)

# Start

@Client.on_message(filters.command(["start"]) & (filters.chat(sudo_chat_id)))
async def start(_, message: Message):
    await message.reply_text("Hi I'm Telegram Voice Chat Bot, Pressing /help wen?")

# Help

@Client.on_message(filters.command(["help"]) & (filters.chat(sudo_chat_id)))
async def help(_, message: Message):
    await message.reply_text('''Currently These Commands Are Supported.
/start To Start The bot.
/help To Show This Message.
/ping To Ping All Datacenters Of Telegram.
/end To Stop Any Playing Music.
"/jiosaavn <song_name>" To Play A Song From Jiosaavn.
"/ytsearch <song_name>" To Search For A Song On Youtube.
"/youtube <song_link>" To Play A Song From Youtube.
/radio To Play Radio Continuosly

NOTE: Do Not Assign These Commands To Bot Via BotFather''')

# Jiosaavn
#Global vars
s = None
m = None
@Client.on_message(filters.command(["jiosaavn"]) & (filters.chat(sudo_chat_id)))
async def jiosaavn(_, message: Message):
    global s
    global m
    try:
        os.system("killall -9 mpv")
    except:
        pass
    try:
        await message.delete()
    except:
        pass
    if len(message.command) < 2:
        await message.reply_text("/jiosaavn requires an argument")
        return

    query = message.text.replace("/jiosaavn ", "")
    m = await message.reply_text("Searching...")
    r = requests.get(f"{jio_saavn_api}{query}")


    sname = r.json()[0]['song']
    slink = r.json()[0]['media_url']
    ssingers = r.json()[0]['singers']
    await m.edit(f"Playing {sname}-{ssingers}")
    s = await asyncio.create_subprocess_shell(f"mpv {slink} --no-video", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

# Youtube Searching

@Client.on_message(filters.command(["ytsearch"]) & (filters.chat(sudo_chat_id)))
async def youtube_search(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    
    if len(message.command) < 2:
        await message.reply_text("/ytsearch requires one argument")
        return

    query = message.text.replace("/ytsearch ", "")
    m = await message.reply_text("Searching....")
    results = YoutubeSearch(query, max_results=4).to_dict()
    i = 0
    text = ""
    while i < 4:
        text += f"Title - {results[i]['title']}\n"
        text += f"Duration - {results[i]['duration']}\n"
        text += f"Views - {results[i]['views']}\n"
        text += f"Channel - {results[i]['channel']}\n"
        text += f"https://youtube.com{results[i]['url_suffix']}\n\n"
        i += 1
    await m.edit(text, disable_web_page_preview=True)
    await asyncio.sleep(40)
    await m.delete()

# Youtube Playing

@Client.on_message(filters.command(["youtube"]) & (filters.chat(sudo_chat_id)))
async def youtube(_, message: Message):
    global m
    global s
    try:
        await message.delete()
    except:
        pass
    try:
        await m.delete()
    except:
        pass
    try:
        os.system("killall -9 mpv")
    except:
        pass
    try:
        os.remove("audio.mp3")
    except:
        pass

    if len(message.command) < 2:
        await message.reply_text("/youtube requires one argument")
        return
    
    ydl_opts = {
        'format': 'bestaudio'
    }

    link = message.command[1]
    try:
        response = requests.get(link)
    except:
        await message.reply_text("Link not found, or your internet is ded af")
        return
    m = await message.reply_text("Downloading....")
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        audio_file = ydl.prepare_filename(info_dict)
        ydl.process_info(info_dict)
        os.rename(audio_file, "audio.webm")
    await m.edit(f"Playing {audio_file}")
    s = await asyncio.create_subprocess_shell(f"mpv audio.webm --no-video", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await s.wait()
    await m.delete()

# Radio

@Client.on_message(filters.command(["radio"]) & (filters.chat(sudo_chat_id)))
async def radio(_, message: Message):
    global m
    global s

    try:
        os.system("killall -9 mpv")
    except:
        pass

    try:
        await message.delete()
    except:
        pass

    try:
        os.remove("audio.mp3")
    except:
        pass
    m = await message.reply_text("Playing Radio....")
    s = await asyncio.create_subprocess_shell(f"mpv http://peridot.streamguys.com:7150/Mirchi --no-video", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)



# Stop

@Client.on_message(filters.command(["end"]) & (filters.chat(sudo_chat_id)))
async def stop(_, message: Message):
    try:
        os.remove("audio.mp3")
    except:
        pass

    try:
        await message.delete()
    except:
        pass
    try:
        os.system("killall -9 mpv")
    except:
        pass
    try:
        s.terminate()
    except:
        pass
    try:
        await m.delete()
    except:
        pass

    i = await message.reply_text("Stopped!")
    await asyncio.sleep(5)
    await i.delete()
