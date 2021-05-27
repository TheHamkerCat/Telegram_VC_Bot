from __future__ import unicode_literals

import asyncio
import functools
import os
import subprocess
import traceback
from sys import version as pyver

# Initialize db
import db
db.init()

from pyrogram import filters, idle
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired
from pyrogram.raw.functions.phone import CreateGroupCall
from pyrogram.raw.types import InputPeerChannel
from pyrogram.types import Message
from pytgcalls import GroupCall

from db import db
from functions import (change_theme, deezer, get_theme, saavn, themes,
                       transcode, youtube, app)
from misc import HELP_TEXT, REPO_TEXT


running = False  # Tells if the queue is running or not


@app.on_message(filters.command("help") & ~filters.private)
async def help(_, message):
    await message.reply_text(HELP_TEXT, quote=False)


@app.on_message(filters.command("repo") & ~filters.private)
async def repo(_, message):
    await message.reply_text(REPO_TEXT, quote=False)


@app.on_message(filters.command("theme") & ~filters.private)
async def theme_func(_, message):
    usage = f"Wrong theme, select one from below\n{' | '.join(themes)}"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    theme = message.text.split(None, 1)[1].strip()
    if theme not in themes:
        return await message.reply_text(usage)
    change_theme(theme, message.chat.id)
    await message.reply_text(f"Changed theme to {theme}")


@app.on_message(filters.command("joinvc") & ~filters.private)
async def joinvc(_, message):
    chat_id = message.chat.id
    if chat_id not in db:
        db[chat_id] = {}

    if "call" in db[chat_id]:
        return await message.reply_text(
            "__**Bot Is Already In The VC**__", quote=False
        )
    os.popen(
        f"cp etc/sample_input.raw input{chat_id}.raw"
    )  # No security issue here
    vc = GroupCall(
        client=app,
        input_filename=f"input{chat_id}.raw",
        play_on_repeat=True,
        enable_logs_to_console=False,
    )
    try:
        await vc.start(chat_id)
    except RuntimeError:
        peer = await app.resolve_peer(chat_id)
        startVC = CreateGroupCall(
            peer=InputPeerChannel(
                channel_id=peer.channel_id,
                access_hash=peer.access_hash,
            ),
            random_id=app.rnd_id() // 9000000000,
        )
        try:
            await app.send(startVC)
            await joinvc(_, message)
        except ChatAdminRequired:
            return await message.reply_text(
                "Make me admin with message delete and vc manage permission"
            )
    db[chat_id]["call"] = vc
    await message.reply_text("__**Joined The Voice Chat.**__", quote=False)


@app.on_message(filters.command("leavevc") & ~filters.private)
async def leavevc(_, message):
    chat_id = message.chat.id
    if chat_id in db:
        if "call" in db[chat_id]:
            vc = db[chat_id]["call"]
            del db[chat_id]["call"]
            await vc.leave_current_group_call()
            await vc.stop()
    await message.reply_text("__**Left The Voice Chat**__", quote=False)


@app.on_message(filters.command("volume") & ~filters.private)
async def volume_bot(_, message):
    usage = "**Usage:**\n/volume [1-200]"
    chat_id = message.chat.id
    if chat_id not in db:
        return await message.reply_text("VC isn't started")
    if "call" not in db[chat_id]:
        return await message.reply_text("VC isn't started")
    vc = db[chat_id]["call"]
    if len(message.command) != 2:
        return await message.reply_text(usage, quote=False)
    volume = int(message.text.split(None, 1)[1])
    if (volume < 1) or (volume > 200):
        return await message.reply_text(usage, quote=False)
    try:
        await vc.set_my_volume(volume=volume)
    except ValueError:
        return await message.reply_text(usage, quote=False)
    await message.reply_text(f"**Volume Set To {volume}**", quote=False)


@app.on_message(filters.command("pause") & ~filters.private)
async def pause_song_func(_, message):
    chat_id = message.chat.id
    if chat_id not in db:
        return await message.reply_text("**VC isn't started**")
    if "call" not in db[chat_id]:
        return await message.reply_text("**VC isn't started**")
    if "paused" in db[chat_id]:
        if db[chat_id]["paused"] == True:
            return await message.reply_text("**Already paused**")
    db[chat_id]["paused"] = True
    vc = db[chat_id]["call"]
    vc.pause_playout()
    await message.reply_text(
        "**Paused The Music, Send `/resume` To Resume.**", quote=False
    )


@app.on_message(filters.command("resume") & ~filters.private)
async def resume_song(_, message):
    chat_id = message.chat.id
    if chat_id not in db:
        return await message.reply_text("**VC isn't started**")
    if "call" not in db[chat_id]:
        return await message.reply_text("**VC isn't started**")
    if "paused" in db[chat_id]:
        if db[chat_id]["paused"] == False:
            return await message.reply_text("**Already playing**")
    db[chat_id]["paused"] = False
    vc = db[chat_id]["call"]
    vc.resume_playout()
    await message.reply_text(
        "**Resumed, Send `/pause` To Pause The Music.**", quote=False
    )


@app.on_message(filters.command("skip") & ~filters.private)
async def skip_func(_, message):
    chat_id = message.chat.id
    if chat_id not in db:
        return await message.reply_text("**VC isn't started**")
    if "queue" not in db[chat_id]:
        return await message.reply_text("**VC isn't started**")
    queue = db[chat_id]["queue"]
    if queue.empty():
        return await message.reply_text(
            "__**Queue Is Empty, Just Like Your Life.**__", quote=False
        )
    db[chat_id]["skipped"] = True
    await message.reply_text("__**Skipped!**__", quote=False)


@app.on_message(filters.command("play") & ~filters.private)
async def queuer(_, message):
    global running
    try:
        usage = "**Usage:**\n__**/play youtube/saavn/deezer Song_Name**__"
        if len(message.command) < 3:
            return await message.reply_text(usage, quote=False)
        text = message.text.split(None, 2)[1:]
        service = text[0].lower()
        song_name = text[1]
        requested_by = message.from_user.first_name
        services = ["youtube", "deezer", "saavn"]
        if service not in services:
            return await message.reply_text(usage, quote=False)
        await message.delete()
        chat_id = message.chat.id
        if chat_id not in db:
            db[chat_id] = {}

        if "queue" not in db[chat_id]:
            db[chat_id]["queue"] = asyncio.Queue()
        if not db[chat_id]["queue"].empty():
            await message.reply_text("__**Added To Queue.__**", quote=False)
        await db[chat_id]["queue"].put(
            {
                "service": deezer
                if service == "deezer"
                else saavn
                if service == "saavn"
                else youtube,
                "requested_by": requested_by,
                "query": song_name,
                "message": message,
            }
        )
        if "running" not in db[chat_id]:
            db[chat_id]["running"] = False
        if not db[chat_id]["running"]:
            db[chat_id]["running"] = True
            await start_queue(chat_id)
    except Exception as e:
        await message.reply_text(str(e), quote=False)
        e = traceback.format_exc()
        print(e)


@app.on_message(filters.command("queue") & ~filters.private)
async def queue_list(_, message):
    chat_id = message.chat.id
    if chat_id not in db:
        db[chat_id] = {}
    if "queue" not in db[chat_id]:
        db[chat_id]["queue"] = asyncio.Queue()
    queue = db[chat_id]["queue"]
    if queue.empty():
        return await message.reply_text(
            "__**Queue Is Empty, Just Like Your Life.**__", quote=False
        )
    text = ""
    for count, song in enumerate(queue._queue, 1):
        text += f"**{count}. {song['service'].__name__}** | __{song['query']}__  |  {song['requested_by']}\n"
    if len(text) > 4090:
        return await message.reply_text(
            f"**There are {queue.qsize()} songs in queue.**"
        )
    await message.reply_text(text)

# Queue handler


async def start_queue(chat_id):
    while True:
        data = await db[chat_id]["queue"].get()
        service = data["service"]
        await service(data["requested_by"], data["query"], data["message"])


# Telegram Audio [Other players are in functions.py]


@app.on_message(filters.command("telegram") & ~filters.private)
async def tgplay(_, message):
    chat_id = message.chat.id
    if chat_id not in db:
        db[chat_id] = {}
    if "queue" not in db[chat_id]:
        db[chat_id]["queue"] = asyncio.Queue()
    queue = db[chat_id]["queue"]
    if not queue.empty():
        return await message.reply_text(
            "__**You Can Only Play Telegram Files After The Queue Gets "
            + "Finished.**__",
            quote=False,
        )
    if not message.reply_to_message:
        return await message.reply_text(
            "__**Reply to an audio.**__", quote=False
        )
    if not message.reply_to_message.audio:
        return await message.reply_text(
            "__**Only Audio Files (Not Document) Are Supported.**__",
            quote=False,
        )
    if int(message.reply_to_message.audio.file_size) >= 104857600:
        return await message.reply_text(
            "__**Bruh! Only songs within 100 MB.**__", quote=False
        )
    duration = message.reply_to_message.audio.duration
    if not duration:
        return await message.reply_text(
            "__**Only Songs With Duration Are Supported.**__", quote=False
        )
    m = await message.reply_text("__**Downloading.**__", quote=False)
    song = await message.reply_to_message.download()
    await m.edit("__**Transcoding.**__")
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, functools.partial(transcode, song, chat_id)
    )
    await m.edit(f"**Playing** __**{message.reply_to_message.link}.**__")
    await asyncio.sleep(duration)
    os.remove(song)


@app.on_message(filters.command("listvc") & ~filters.private)
async def list_vc(_, message):
    if len(db) == 0:
        return await message.reply_text("There are no active voice chats")
    chats = []
    for chat in db:
        if "call" in db[chat]:
            chats.append(int(chat))
    text = ""
    for count, chat_id in enumerate(chats, 1):
        try:
            chat = await app.get_chat(chat_id)
            chat_title = chat.title
        except Exception:
            chat_title = "Private"
        text += f"**{count}.** [`{chat_id}`]  **{chat_title}**\n"
    await message.reply_text(text)


app.start()
print("\nBot Starting...\nFor Support Join https://t.me/TGVCSUPPORT\n")
idle()
