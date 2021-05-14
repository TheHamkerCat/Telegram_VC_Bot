from __future__ import unicode_literals

import asyncio
import os
import subprocess
import traceback
from sys import version as pyver

import youtube_dl
from pyrogram import Client, filters, idle
from pytgcalls import GroupCall
from Python_ARQ import ARQ

from functions import (convert_seconds, download_and_transcode_song,
                       generate_cover, generate_cover_square, time_to_seconds,
                       transcode)
from misc import HELP_TEXT, REPO_TEXT, START_TEXT

# TODO Make it look less messed up
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

queue = []  # This is where the whole song queue is stored
playing = False  # Tells if something is playing or not
call = {}

# Pyrogram Client
if not HEROKU:
    app = Client("tgvc", api_id=API_ID, api_hash=API_HASH)
else:
    app = Client(SESSION_STRING, api_id=API_ID, api_hash=API_HASH)

# Pytgcalls Client


# Arq Client
arq = ARQ(ARQ_API, ARQ_API_KEY)


async def delete(message):
    await asyncio.sleep(10)
    await message.delete()


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
    try:
        if str(chat_id) in call.keys():
            await message.reply_text("__**Bot Is Already In The VC**__", quote=False)
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
    except Exception as e:
        e = traceback.format_exc
        print(str(e))


@app.on_message(filters.command("leavevc") & filters.user(SUDOERS) & ~filters.private)
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


@app.on_message(filters.command("update") & filters.user(SUDOERS) & ~filters.private)
async def update_restart(_, message):
    await message.reply_text(
        f'```{subprocess.check_output(["git", "pull"]).decode("UTF-8")}```', quote=False
    )
    os.execvp(
        f"python{str(pyver.split(' ')[0])[:3]}",
        [f"python{str(pyver.split(' ')[0])[:3]}", "main.py"],
    )


@app.on_message(
    filters.command("pause")
    & ~filters.private
    & (filters.user(SUDOERS) | filters.chat(SUDO_CHAT_ID))
)
async def pause_song(_, message):
    vc = call[str(message.chat.id)]
    vc.pause_playout()
    await message.reply_text(
        "**Paused The Music, Send `/resume` To Resume.**", quote=False
    )


@app.on_message(
    filters.command("resume")
    & ~filters.private
    & (filters.user(SUDOERS) | filters.chat(SUDO_CHAT_ID))
)
async def resume_song(_, message):
    vc = call[str(message.chat.id)]
    vc.resume_playout()
    await message.reply_text(
        "**Resumed, Send `/pause` To Pause The Music.**", quote=False
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


@app.on_message(
    filters.command("play")
    & ~filters.private
    & (filters.user(SUDOERS) | filters.chat(SUDO_CHAT_ID))
)
async def queuer(_, message):
    global queue
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
        if len(queue) > 0:
            await message.reply_text("__**Added To Queue.__**", quote=False)
        queue.append(
            {
                "service": service,
                "song": song_name,
                "requested_by": requested_by,
                "message": message,
            }
        )
        await play()
    except Exception as e:
        e = traceback.format_exc()
        print(e)
        await message.reply_text(str(e), quote=False)


@app.on_message(filters.command("skip") & ~filters.private & filters.user(SUDOERS))
async def skip(_, message):
    global playing
    if len(queue) == 0:
        await message.reply_text(
            "__**Queue Is Empty, Just Like Your Life.**__", quote=False
        )
        return
    playing = False
    await message.reply_text("__**Skipped!**__", quote=False)
    await play()


@app.on_message(
    filters.command("queue")
    & ~filters.private
    & (filters.user(SUDOERS) | filters.chat(SUDO_CHAT_ID))
)
async def queue_list(_, message):
    if len(queue) != 0:
        i = 1
        text = ""
        for song in queue:
            text += (
                f"**{i}. Platform:** __**{song['service']}**__ "
                + f"| **Song:** __**{song['song']}**__\n"
            )
            i += 1
        m = await message.reply_text(text, quote=False)
        await delete(message)
        await m.delete()

    else:
        m = await message.reply_text(
            "__**Queue Is Empty, Just Like Your Life.**__", quote=False
        )
        await delete(message)
        await m.delete()


# Queue handler


async def play():
    global queue, playing
    while not playing:
        await asyncio.sleep(0.1)
        if len(queue) != 0:
            service = queue[0]["service"]
            song = queue[0]["song"]
            requested_by = queue[0]["requested_by"]
            message = queue[0]["message"]
            if service == "youtube":
                playing = True
                del queue[0]
                try:
                    await ytplay(requested_by, song, message)
                except Exception as e:
                    print(str(e))
                    playing = False
                    pass
            elif service == "saavn":
                playing = True
                del queue[0]
                try:
                    await jiosaavn(requested_by, song, message)
                except Exception as e:
                    print(str(e))
                    playing = False
                    pass
            elif service == "deezer":
                playing = True
                del queue[0]
                try:
                    await deezer(requested_by, song, message)
                except Exception as e:
                    print(str(e))
                    playing = False
                    pass


# Deezer----------------------------------------------------------------------------------------


async def deezer(requested_by, query, message):
    global playing
    m = await message.reply_text(
        f"__**Searching for {query} on Deezer.**__", quote=False
    )
    try:
        songs = await arq.deezer(query, 1)
        if not songs.ok:
            await message.reply_text(songs.result)
            return
        songs = songs.result
        title = songs[0].title
        duration = convert_seconds(int(songs[0].duration))
        thumbnail = songs[0].thumbnail
        artist = songs[0].artist
        url = songs[0].url
    except Exception:
        await m.edit("__**Found No Song Matching Your Query.**__")
        playing = False
        return
    await m.edit("__**Generating Thumbnail.**__")
    await generate_cover_square(requested_by, title, artist, duration, thumbnail)
    await m.edit("__**Downloading And Transcoding.**__")
    await download_and_transcode_song(url)
    await m.delete()
    caption = (
        f"🏷 **Name:** [{title[:35]}]({url})\n⏳ **Duration:** {duration}\n"
        + f"🎧 **Requested By:** {message.from_user.mention}\n📡 **Platform:** Deezer"
    )
    m = await message.reply_photo(
        photo="final.png",
        caption=caption,
    )
    os.remove("final.png")
    await asyncio.sleep(int(songs[0]["duration"]))
    await m.delete()
    playing = False


# Jiosaavn--------------------------------------------------------------------------------------


async def jiosaavn(requested_by, query, message):
    global playing
    m = await message.reply_text(
        f"__**Searching for {query} on JioSaavn.**__", quote=False
    )
    try:
        songs = await arq.saavn(query)
        if not songs.ok:
            await message.reply_text(songs.result)
            return
        songs = songs.result
        sname = songs[0].song
        slink = songs[0].media_url
        ssingers = songs[0].singers
        sthumb = songs[0].image
        sduration = songs[0].duration
        sduration_converted = convert_seconds(int(sduration))
    except Exception as e:
        await m.edit("__**Found No Song Matching Your Query.**__")
        print(str(e))
        playing = False
        return
    await m.edit("__**Processing Thumbnail.**__")
    await generate_cover_square(
        requested_by, sname, ssingers, sduration_converted, sthumb
    )
    await m.edit("__**Downloading And Transcoding.**__")
    await download_and_transcode_song(slink)
    await m.delete()
    caption = (
        f"🏷 **Name:** {sname[:35]}\n⏳ **Duration:** {sduration_converted}\n"
        + f"🎧 **Requested By:** {message.from_user.mention}\n📡 **Platform:** JioSaavn"
    )
    m = await message.reply_photo(
        photo="final.png",
        caption=caption,
    )
    os.remove("final.png")
    await asyncio.sleep(int(sduration))
    await m.delete()
    playing = False


# Youtube Play-----------------------------------------------------


async def ytplay(requested_by, query, message):
    global playing
    ydl_opts = {"format": "bestaudio"}
    m = await message.reply_text(
        f"__**Searching for {query} on YouTube.**__", quote=False
    )
    try:
        results = await arq.youtube(query)
        if not results.ok:
            await message.reply_text(results.result)
            return
        results = results.result
        link = f"https://youtube.com{results[0].url_suffix}"
        title = results[0].title
        thumbnail = results[0].thumbnails[0]
        duration = results[0].duration
        views = results[0].views
        if time_to_seconds(duration) >= 1800:
            await m.edit("__**Bruh! Only songs within 30 Mins.**__")
            playing = False
            return
    except Exception as e:
        await m.edit("__**Found No Song Matching Your Query.**__")
        playing = False
        print(str(e))
        return
    await m.edit("__**Processing Thumbnail.**__")
    await generate_cover(requested_by, title, views, duration, thumbnail)
    await m.edit("__**Downloading Music.**__")
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        audio_file = ydl.prepare_filename(info_dict)
        ydl.process_info(info_dict)
    await m.edit("__**Transcoding.**__")
    os.rename(audio_file, "audio.webm")
    transcode("audio.webm")
    await m.delete()
    caption = (
        f"🏷 **Name:** [{title[:35]}]({link})\n⏳ **Duration:** {duration}\n"
        + f"🎧 **Requested By:** {message.from_user.mention}\n📡 **Platform:** YouTube"
    )
    m = await message.reply_photo(
        photo="final.png",
        caption=caption,
    )
    os.remove("final.png")
    await asyncio.sleep(int(time_to_seconds(duration)))
    playing = False
    await m.delete()


# Telegram Audio------------------------------------


@app.on_message(
    filters.command("telegram") & filters.chat(SUDO_CHAT_ID) & ~filters.edited
)
async def tgplay(_, message):
    global playing
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
    if message.reply_to_message.audio:
        if int(message.reply_to_message.audio.file_size) >= 104857600:
            await message.reply_text(
                "__**Bruh! Only songs within 100 MB.**__", quote=False
            )
            playing = False
            return
        duration = message.reply_to_message.audio.duration
        if not duration:
            await message.reply_text(
                "__**Only Songs With Duration Are Supported.**__", quote=False
            )
            return
        m = await message.reply_text("__**Downloading.**__", quote=False)
        song = await message.reply_to_message.download()
        await m.edit("__**Transcoding.**__")
        transcode(song)
        await m.edit(f"**Playing** __**{message.reply_to_message.link}.**__")
        await asyncio.sleep(duration)
        playing = False
        return
    await message.reply_text(
        "__**Only Audio Files (Not Document) Are Supported.**__", quote=False
    )


app.start()
print("\nBot Starting...\nFor Support Join https://t.me/TGVCSUPPORT\n")
idle()
