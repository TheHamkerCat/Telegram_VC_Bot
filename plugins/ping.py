from pyrogram import Client, filters
from pyrogram.types import Message
from config import owner_id, sudo_chat_username, jio_saavn_api
import requests
import os
# Ping

@Client.on_message(filters.command(["ping"]) & (filters.chat(sudo_chat_username)) & (filters.user(owner_id)))
async def ping(_, message: Message):
    await message.reply_text("pong")

# Start

@Client.on_message(filters.command(["start"]) & (filters.chat(sudo_chat_username)) & (filters.user(owner_id)))
async def ping(_, message: Message):
    await message.reply_text("Hi I'm Telegram Voice Chat Bot")

# Jiosaavn

@Client.on_message(filters.command(["jiosaavn"]) & (filters.chat(sudo_chat_username)) & (filters.user(owner_id)))
async def ping(_, message: Message):
    if len(message.command) != 2:
        await message.reply_text("/upload requires one argument")
        return

    query = message.command[1]
    m = await message.reply_text("Searching...")
    r = requests.get(f"{jio_saavn_api}{query}")


    sname = r.json()[0]['song']
    slink = r.json()[0]['media_url']
    ssingers = r.json()[0]['singers']
    await message.reply_text(f"Playing {sname}-{ssingers}")
    os.system(f"mpv {slink} --no-video")
    await m.delete()
