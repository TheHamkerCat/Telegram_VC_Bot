from __future__ import unicode_literals

import asyncio
import traceback
from asyncio import Lock

from pyrogram import filters, idle
from pyrogram.types import Message

# Initialize db
import db

db.init()

from db import db
from functions import (CHAT_ID, app, get_default_service, play_song,
                       session,  telegram,
            )
from misc import HELP_TEXT, REPO_TEXT

running = False  # Tells if the queue is running or not


@app.on_message(
    filters.command("help") 
    & ~filters.private
    & filters.chat(CHAT_ID)
)
async def help_handler(_, message):
    await message.reply_text(HELP_TEXT, quote=False)


@app.on_message(
    filters.command("repo") 
    & ~filters.private
    & filters.chat(CHAT_ID)
)
async def repo(_, message):
    await message.reply_text(REPO_TEXT, quote=False)


@app.on_message(
    filters.command("skip") & ~filters.private & filters.chat(CHAT_ID)
)
async def skip_func(_, message):
    queue = db["queue"]
    if queue.empty() and ("playlist" not in db or not db["playlist"]):
        await message.reply_text(
            "__**Queue Is Empty, Just Like Your Life.**__"
        )
        return await message.delete()
    db["skipped"] = True
    await message.reply_text("__**Skipped!**__")
    await message.delete()


PLAY_LOCK = Lock()


@app.on_message(
    filters.command("play") & ~filters.private & filters.chat(CHAT_ID)
)
async def queuer(_, message):
    global running
    try:
        usage = """
**Usage:**
__/play Song_Name__
__/play youtube/saavn Song_Name__
__/play Reply_On_Audio__"""

        async with PLAY_LOCK:
            if (
                len(message.command) < 2
                and not message.reply_to_message
            ):
                return await message.reply_text(usage)
            if message.reply_to_message:
                if message.reply_to_message.audio:
                    service = "telegram"
                    song_name = message.reply_to_message.audio.title
                else:
                    return await message.reply_text(
                        "**Reply to a telegram audio file**"
                    )
            else:
                text = message.text.split("\n")[0]
                text = text.split(None, 2)[1:]
                service = text[0].lower()
                services = ["youtube", "saavn"]
                if service in services:
                    song_name = text[1]
                else:
                    service = get_default_service()
                    song_name = " ".join(text)
                if "http" in song_name or ".com" in song_name:
                    return await message.reply("Links aren't supported.")

            requested_by = message.from_user.first_name
            if "queue" not in db:
                db["queue"] = asyncio.Queue()
            if not db["queue"].empty() or db.get("running"):
                await message.reply_text("__**Added To Queue.__**")

            await db["queue"].put(
                {
                    "service": service or telegram,
                    "requested_by": requested_by,
                    "query": song_name,
                    "message": message,
                }
            )
        if not db.get("running"):
            db["running"] = True
            await start_queue()
    except Exception as e:
        await message.reply_text(str(e))
        e = traceback.format_exc()
        print(e)


@app.on_message(
    filters.command("queue")
    & ~filters.private
    & filters.chat(CHAT_ID)
)
async def queue_list(_, message):
    if "queue" not in db:
        db["queue"] = asyncio.Queue()
    queue = db["queue"]
    if queue.empty():
        return await message.reply_text(
            "__**Queue Is Empty, Just Like Your Life.**__"
        )
    if (
        len(message.text.split()) > 1
        and message.text.split()[1].lower() == "plformat"
    ):
        pl_format = True
    else:
        pl_format = False
    text = ""
    for count, song in enumerate(queue._queue, 1):
        if not pl_format:
            text += (
                f"**{count}. {song['service']}** "
                + f"| __{song['query']}__  |  {song['requested_by']}\n"
            )
        else:
            text += song["query"] + "\n"
    if len(text) > 4090:
        return await message.reply_text(
            f"**There are {queue.qsize()} songs in queue.**"
        )
    await message.reply_text(text)


# Queue handler


async def start_queue(message=None):
    print("Starting queue")
    while db:
        if "queue_breaker" in db and db.get("queue_breaker") != 0:
            db["queue_breaker"] -= 1
            if db["queue_breaker"] == 0:
                del db["queue_breaker"]
            break
        if db["queue"].empty():
            if "playlist" not in db or not db["playlist"]:
                db["running"] = False
                break
            else:
                await playlist(app, message, redirected=True)
        data = await db["queue"].get()
        service = data["service"]
        if service == "telegram":
            await telegram(data["message"])
        else:
            await play_song(
                data["requested_by"],
                data["query"],
                data["message"],
                service,
            )


@app.on_message(
    filters.command("delqueue")
    & ~filters.private
    & filters.chat(CHAT_ID)
)
async def clear_queue(_, message):
    global db
    if "call" not in db:
        return await message.reply_text("**VC isn't started**")
    if ("queue" not in db or db["queue"].empty()) and (
        "playlist" not in db or not db["playlist"]
    ):
        return await message.reply_text("**Queue Already is Empty**")
    db["playlist"] = False
    db["queue"] = asyncio.Queue()
    await message.reply_text("**Successfully Cleared the Queue**")


@app.on_message(
    filters.command("playlist")
    & ~filters.private
    & filters.chat(CHAT_ID)
)
async def playlist(_, message: Message, redirected=False):
    if message.reply_to_message:
        raw_playlist = message.reply_to_message.text
    elif len(message.text) > 9:
        raw_playlist = message.text[10:]
    else:
        usage = """
**Usage: Same as /play
Example:
    __**/playlist song_name1
    song_name2
    youtube song_name3**__"""

        return await message.reply_text(usage)
    if "call" not in db:
        return await message.reply_text("**Use /joinvc First!**")
    if "playlist" not in db:
        db["playlist"] = False
    if "running" in db and db.get("running"):
        db["queue_breaker"] = 1
    db["playlist"] = True
    db["queue"] = asyncio.Queue()
    for line in raw_playlist.split("\n"):
        services = ["youtube", "saavn"]
        if line.split()[0].lower() in services:
            service = line.split()[0].lower()
            song_name = " ".join(line.split()[1:])
        else:
            service = "youtube"
            song_name = line
        requested_by = message.from_user.first_name
        await db["queue"].put(
            {
                "service": service or telegram,
                "requested_by": requested_by,
                "query": song_name,
                "message": message,
            }
        )
    if not redirected:
        db["running"] = True
        await message.reply_text("**Playlist Started.**")
        await start_queue(message)


async def main():
    await app.start()
    print("Bot started!")
    await idle()
    await session.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
