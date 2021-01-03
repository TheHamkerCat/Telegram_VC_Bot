from pyrogram import Client, filters
from pyrogram.types import Message
from config import owner_id, sudo_chat_username, jio_saavn_api
import requests
import os
import asyncio
# Ping

@Client.on_message(filters.command(["ping"]) & (filters.chat(sudo_chat_username)) & (filters.user(owner_id)))
async def ping(_, message: Message):
    j = await message.reply_text("Wait, Pinging all Datacenters`")
    result = ""
    for i in range(1, 6):
        datacenter = (f"https://cdn{i}.telesco.pe")
        ping1 = round(requests.head(datacenter).elapsed.total_seconds() * 1000)
        result += f'`DC{i} - {ping1}ms`\n'
    await j.edit(result)

# Start

@Client.on_message(filters.command(["start"]) & (filters.chat(sudo_chat_username)) & (filters.user(owner_id)))
async def start(_, message: Message):
    await message.reply_text("Hi I'm Telegram Voice Chat Bot, Pressing /help wen?")

# Help

@Client.on_message(filters.command(["help"]) & (filters.chat(sudo_chat_username)) & (filters.user(owner_id)))
async def help(_, message: Message):
    await message.reply_text('''Currently These Commands Are Supported.
/start To Start The bot
/help To Show This Message
/ping To Ping All Datacenters Of Telegram
"/jiosaavn <song_name>" To Play A Song From Jiosaavn

NOTE: Do Not Assign These Commands To Bot Via BotFather''')

# Jiosaavn
s = None
m = None
@Client.on_message(filters.command(["jiosaavn"]) & (filters.chat(sudo_chat_username)) & (filters.user(owner_id)))
async def jiosaavn(_, message: Message):
    global s
    global m
    if len(message.command) != 2:
        await message.reply_text("/upload requires one argument")
        return

    query = message.command[1]
    m = await message.reply_text("Searching...")
    r = requests.get(f"{jio_saavn_api}{query}")


    sname = r.json()[0]['song']
    slink = r.json()[0]['media_url']
    ssingers = r.json()[0]['singers']
    await m.edit(f"Playing {sname}-{ssingers}")
#    os.system(f"mpv {slink} --no-video")
    s = await asyncio.create_subprocess_shell(f"mpv {slink} --no-video", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await s.communicate()
    await m.delete()

# Stop

@Client.on_message(filters.command(["stop"]) & (filters.chat(sudo_chat_username)) & (filters.user(owner_id)))
async def stop(_, message: Message):
    s.terminate()
    try:
        await m.delete()
    except:
        pass

    i = await message.reply_text("Stopped!")
    await asyncio.sleep(5)
    await i.delete()




