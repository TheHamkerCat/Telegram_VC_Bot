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
                       transcode, youtube, app, get_default_service, telegram, session)
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
        return await message.reply_text("__**Bot Is Already In The VC**__")
    os.popen(
        f"cp etc/sample_input.raw input{chat_id}.raw"
    )

    vc = GroupCall(
        app,
        f"input{chat_id}.raw"
    )

    db[chat_id]["call"] = vc

    try:
        await db[chat_id]["call"].start(chat_id)
    except:
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
            await db[chat_id]["call"].start(chat_id)
        except ChatAdminRequired:
            del db[chat_id]["call"]
            return await message.reply_text(
                "Make me admin with message delete and vc manage permission"
            )
    await message.reply_text("__**Joined The Voice Chat.**__")


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
    if queue.empty() and ("playlist" not in db[chat_id] or not db[chat_id]["playlist"]):
        return await message.reply_text(
            "__**Queue Is Empty, Just Like Your Life.**__", quote=False
        )
    db[chat_id]["skipped"] = True
    await message.reply_text("__**Skipped!**__")


@app.on_message(filters.command("play") & ~filters.private)
async def queuer(_, message):
    global running
    chat_id = message.chat.id
    try:
        usage = "**Usage:**\n__**/play Song_Name**__ (uses youtube service)\n__**/play youtube/saavn/deezer Song_Name**__\n__**/play Reply_On_Audio**__"
        if len(message.command) < 2 and (not message.reply_to_message or not message.reply_to_message.audio):
            return await message.reply_text(usage, quote=False)
        if chat_id not in db:
            db[chat_id] = {}
        if "call" not in db[chat_id]:
            return await message.reply_text("**Use /joinvc First!**")
        if message.reply_to_message and message.reply_to_message.audio:
            service = "telegram"
            song_name = message.reply_to_message.audio.title
        else:
            text = message.text.split("\n")[0]
            text = text.split(None, 2)[1:]
            service = text[0].lower()
            services = ["youtube", "deezer", "saavn"]
            if service in services:
                song_name = text[1]
            else:
                service = get_default_service()
                song_name = " ".join(text)
        requested_by = message.from_user.first_name
        if chat_id not in db:
            db[chat_id] = {}
        if "queue" not in db[chat_id]:
            db[chat_id]["queue"] = asyncio.Queue()
        if not db[chat_id]["queue"].empty() or ("running" in db[chat_id] and db[chat_id]["running"]):
            await message.reply_text("__**Added To Queue.__**", quote=False)
        
        await db[chat_id]["queue"].put(
            {
                "service": deezer
                if service == "deezer"
                else saavn
                if service == "saavn"
                else youtube
                if service == "youtube"
                else telegram,
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
    if len(message.text.split()) > 1 and message.text.split()[1].lower() == "plformat":
        pl_format = True
    else:
        pl_format = False
    text = ""
    for count, song in enumerate(queue._queue, 1):
        if not pl_format:
            text += f"**{count}. {song['service'].__name__}** | __{song['query']}__  |  {song['requested_by']}\n"
        else:
            text += f"{song['query']}\n"
    if len(text) > 4090:
        return await message.reply_text(
            f"**There are {queue.qsize()} songs in queue.**"
        )
    await message.reply_text(text)

# Queue handler


async def start_queue(chat_id, message=None):
    while True:
        db[chat_id]["call"].set_is_mute(True)
        if "queue_breaker" in db[chat_id] and db[chat_id]["queue_breaker"] != 0:
            db[chat_id]["queue_breaker"] -= 1
            if db[chat_id]["queue_breaker"] == 0:
                del db[chat_id]["queue_breaker"]
            break
        if db[chat_id]["queue"].empty():
            if "playlist" not in db[chat_id] or not db[chat_id]["playlist"]:
                db[chat_id]["running"] = False
                db[chat_id]["call"].set_is_mute(False)
                break
            else:
                await playlist(app, message, redirected=True)
        data = await db[chat_id]["queue"].get()
        service = data["service"]
        await service(data["requested_by"], data["query"], data["message"])


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
    if not text:
        return await message.reply_text("There are no active voice chats")
    await message.reply_text(text)


@app.on_message(filters.command("stop") & ~filters.private)
async def stop_vc(_, message):
    global db
    chat_id = message.chat.id
    if chat_id not in db:
        return await message.reply_text("**VC isn't started**")
    if "call" not in db[chat_id]:
        return await message.reply_text("**VC isn't started**")
    vc = db[chat_id]["call"]
    vc.set_is_mute(True)
    if "stopped" not in db[chat_id]:
        db[chat_id]["stopped"] = False
    db[chat_id]["stopped"] = True
    await message.reply_text(
        "**Stopped, Send /start To Start.**", quote=False
    )


@app.on_message(filters.command("start") & ~filters.private)
async def start_vc(_, message):
    global db
    chat_id = message.chat.id
    if chat_id not in db:
        return await message.reply_text("**VC isn't started**")
    if "call" not in db[chat_id]:
        return await message.reply_text("**VC isn't started**")
    vc = db[chat_id]["call"]
    vc.set_is_mute(False)
    if "stopped" not in db[chat_id]:
        db[chat_id]["stopped"] = False
    db[chat_id]["stopped"] = False
    await message.reply_text(
        "**Started, Send /stop To Stop.**", quote=False
    )


@app.on_message(filters.command("replay") & ~filters.private)
async def replay_vc(_, message):
    global db
    chat_id = message.chat.id
    if chat_id not in db:
        return await message.reply_text("**VC isn't started**")
    if "call" not in db[chat_id]:
        return await message.reply_text("**VC isn't started**")
    vc = db[chat_id]["call"]
    vc.set_is_mute(True)
    vc.set_is_mute(False)
    if "replayed" not in db[chat_id]:
        db[chat_id]["replayed"] = False
    db[chat_id]["replayed"] = True
    await message.reply_text(
        "**The Music Replayed**", quote=False
    )


@app.on_message(filters.command("delqueue") & ~filters.private)
async def clear_queue(_, message):
    global db
    chat_id = message.chat.id
    if chat_id not in db:
        return await message.reply_text("**VC isn't started**")
    if "call" not in db[chat_id]:
        return await message.reply_text("**VC isn't started**")
    if ("queue" not in db[chat_id] or db[chat_id]["queue"].empty()) and ("playlist" not in db[chat_id] or not db[chat_id]["playlist"]):
        return await message.reply_text("**Queue Already is Empty**")
    db[chat_id]["playlist"] = False
    db[chat_id]["queue"] = asyncio.Queue()
    await message.reply_text(
        "**Successfully Cleared the Queue**",
        quote=False
    )


@app.on_message(filters.command("playlist") & ~filters.private)
async def playlist(_, message: Message, redirected = False):
    chat_id = message.chat.id
    if message.reply_to_message:
        raw_playlist = message.reply_to_message.text
    elif len(message.text) > 9:
        raw_playlist = message.text[10:]
    else:
        usage = "**Usage: Same as /play\n\nExample:\n__**/playlist song_name1\nsong_name2\nyoutube song_name3**__"
        return await message.reply_text(usage, quote=False)
    if chat_id not in db:
        db[chat_id] = {}
    if "call" not in db[chat_id]:
        return await message.reply_text("**Use /joinvc First!**")
    if "playlist" not in db[chat_id]:
        db[chat_id]["playlist"] = False
    if "running" in db[chat_id] and db[chat_id]["running"]:
        db[chat_id]["queue_breaker"] = 1
    db[chat_id]["playlist"] = True
    db[chat_id]["queue"] = asyncio.Queue()
    for line in raw_playlist.split("\n"):
        services = ["youtube", "deezer", "saavn"]
        if line.split()[0].lower() in services:
            service = line.split()[0].lower()
            song_name = " ".join(line.split()[1:])
        else:
            service = "youtube"
            song_name = line
        requested_by = message.from_user.first_name
        await db[chat_id]["queue"].put(
            {
                "service": deezer
                if service == "deezer"
                else saavn
                if service == "saavn"
                else youtube
                if service == "youtube"
                else telegram,
                "requested_by": requested_by,
                "query": song_name,
                "message": message,
            }
        )
    if not redirected:
        db[chat_id]["running"] = True
        await message.reply_text(
            "**Playlist Started.**"
        )
        await start_queue(chat_id, message=message)


@app.on_message(filters.command("lyric") & ~filters.private)
async def lyrics(_, message):
    global db
    chat_id = message.chat.id
    if chat_id not in db or "call" not in db[chat_id]:
        return await message.reply_text("**VC isn't started**")
    if "currently" not in db[chat_id]:
        return await message.reply_text("**No Song is Playing**")
    msg = await message.reply_text("**__Getting Lyric__**")
    data = db[chat_id]["currently"]
    lyric = await get_lyric(data["query"], data["artist"], data["song"])
    await msg.edit_text(lyric, parse_mode=None)


app.start()
idle()
print("Waiting for Deleting Input Files...")
for x in os.listdir():
    if x.endswith(".raw") or x.endswith(".mp3"):
        os.remove(x)
print("Turning Off...")
async def closeSession(session):
    await session.close()
m_loop = asyncio.get_event_loop()
m_loop.run_until_complete(closeSession(session))
db.clear()
app.stop()
m_loop.close()
