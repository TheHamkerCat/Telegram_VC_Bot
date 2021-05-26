from __future__ import unicode_literals

import asyncio
import os
import subprocess
import traceback
from sys import version as pyver

from pyrogram import Client, filters, idle
from pytgcalls import GroupCall

from functions import deezer, saavn, youtube
from misc import HELP_TEXT, REPO_TEXT, START_TEXT

is_config = os.path.exists("config.py")

if is_config:
    from config import *
else:
    from sample_config import *

if HEROKU:
    if is_config:
        from config import SESSION_STRING
    elif not is_config:
        from sample_config import SESSION_STRING


# Pyrogram Client
if not HEROKU:
    app = Client("tgvc", api_id=API_ID, api_hash=API_HASH)
else:
    app = Client(SESSION_STRING, api_id=API_ID, api_hash=API_HASH)


# This is where queue info and functions will be stored
queue: asyncio.Queue = asyncio.Queue()


call = {}  # This is where calls will be stored


@app.on_message(
    filters.command("start")
    & ~filters.private
    & (filters.user(SUDOERS) | filters.chat(SUDO_CHAT_ID))
)
async def start(_, message):
    await message.reply_text(START_TEXT, quote=False)


@app.on_message(
    filters.command("help")
    & ~filters.private
    & (filters.user(SUDOERS) | filters.chat(SUDO_CHAT_ID))
)
async def help(_, message):
    await message.reply_text(HELP_TEXT, quote=False)


@app.on_message(
    filters.command("repo")
    & ~filters.private
    & (filters.user(SUDOERS) | filters.chat(SUDO_CHAT_ID))
)
async def repo(_, message):
    await message.reply_text(REPO_TEXT, quote=False)


@app.on_message(
    filters.command("joinvc")
    & (filters.user(SUDOERS) | filters.chat(SUDO_CHAT_ID))
    & ~filters.private
)
async def joinvc(_, message):
    global call
    chat_id = message.chat.id
    if str(chat_id) in call.keys():
        await message.reply_text(
            "__**Bot Is Already In The VC**__", quote=False
        )
        return
    vc = GroupCall(
        client=app,
        input_filename=f"input.raw",
        play_on_repeat=True,
        enable_logs_to_console=False,
    )
    await vc.start(chat_id)
    call[str(chat_id)] = vc
    await message.reply_text("__**Joined The Voice Chat.**__", quote=False)


@app.on_message(
    filters.command("leavevc") & filters.user(SUDOERS) & ~filters.private
)
async def leavevc(_, message):
    vc = call[str(message.chat.id)]
    await vc.leave_current_group_call()
    await vc.stop()
    await message.reply_text(
        "__**Left The Voice Chat, Restarting Client....**__", quote=False
    )
    os.execvp(
        f"python{str(pyver.split(' ')[0])[:3]}",
        [f"python{str(pyver.split(' ')[0])[:3]}", "main.py"],
    )


@app.on_message(
    filters.command("update") & filters.user(SUDOERS) & ~filters.private
)
async def update_restart(_, message):
    await message.reply_text(
        f'```{subprocess.check_output(["git", "pull"]).decode("UTF-8")}```',
        quote=False,
    )
    os.execvp(
        f"python{str(pyver.split(' ')[0])[:3]}",
        [f"python{str(pyver.split(' ')[0])[:3]}", "main.py"],
    )


@app.on_message(
    filters.command("volume")
    & ~filters.private
    & (filters.user(SUDOERS) | filters.chat(SUDO_CHAT_ID))
)
async def volume_bot(_, message):
    vc = call[str(message.chat.id)]
    usage = "**Usage:**\n/volume [1-200]"
    if len(message.command) != 2:
        await message.reply_text(usage, quote=False)
        return
    volume = int(message.text.split(None, 1)[1])
    if (volume < 1) or (volume > 200):
        await message.reply_text(usage, quote=False)
        return
    try:
        await vc.set_my_volume(volume=volume)
    except ValueError:
        await message.reply_text(usage, quote=False)
        return
    await message.reply_text(f"**Volume Set To {volume}**", quote=False)


running = False


@app.on_message(
    filters.command("play")
    & ~filters.private
    & (filters.user(SUDOERS) | filters.chat(SUDO_CHAT_ID))
)
async def queuer(_, message):
    global running
    try:
        usage = "**Usage:**\n__**/play youtube/saavn/deezer Song_Name**__"
        if len(message.command) < 3:
            await message.reply_text(usage, quote=False)
            return
        text = message.text.split(None, 2)[1:]
        service = text[0].lower()
        song_name = text[1]
        requested_by = message.from_user.first_name
        services = ["youtube", "deezer", "saavn"]
        if service not in services:
            await message.reply_text(usage, quote=False)
            return
        await message.delete()
        if not queue.empty():
            await message.reply_text("__**Added To Queue.__**", quote=False)
        await queue.put(
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
        if not running:
            running = True
            await start_queue()
    except Exception as e:
        await message.reply_text(str(e), quote=False)
        e = traceback.format_exc()
        print(e)


@app.on_message(
    filters.command("queue")
    & ~filters.private
    & (filters.user(SUDOERS) | filters.chat(SUDO_CHAT_ID))
)
async def queue_list(_, message):
    if queue.empty():
        return await message.reply_text(
            "__**Queue Is Empty, Just Like Your Life.**__", quote=False
        )
    await message.reply_text(f"**There are {queue.qsize()} songs in queue.**")


# Queue handler


async def start_queue():
    while True:
        data = await queue.get()
        service = data["service"]
        await service(data["requested_by"], data["query"], data["message"])


# Telegram Audio [Other players are in functions.py]


@app.on_message(
    filters.command("telegram") & filters.chat(SUDO_CHAT_ID) & ~filters.edited
)
async def tgplay(_, message):
    if len(queue) != 0:
        await message.reply_text(
            "__**You Can Only Play Telegram Files After The Queue Gets "
            + "Finished.**__",
            quote=False,
        )
        return
    if not message.reply_to_message:
        await message.reply_text("__**Reply to an audio.**__", quote=False)
        return
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
    await loop.run_in_executor(None, transcode, song)
    await m.edit(f"**Playing** __**{message.reply_to_message.link}.**__")
    await asyncio.sleep(duration)
    os.remove(song)


app.start()
print("\nBot Starting...\nFor Support Join https://t.me/TGVCSUPPORT\n")
idle()
