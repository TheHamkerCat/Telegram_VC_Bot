from __future__ import unicode_literals
import os
import asyncio
import subprocess
import youtube_dl
from Python_ARQ import ARQ
from pytgcalls import GroupCall
from sys import version as pyver
from pyrogram import Client, filters
from misc import HELP_TEXT, START_TEXT, REPO_TEXT
from functions import (
    transcode,
    download_and_transcode_song,
    convert_seconds,
    time_to_seconds,
    generate_cover,
    generate_cover_square,
)

# TODO Make it look less messed up
is_config = os.path.exists("config.py")

if is_config:
    from config import (
        API_ID, API_HASH,
        SUDO_CHAT_ID,
        SUDOERS, ARQ_API, HEROKU
    )
elif not is_config:
    from sample_config import (
        API_ID, API_HASH,
        SUDO_CHAT_ID,
        SUDOERS, ARQ_API, HEROKU
    )

if HEROKU:
    if is_config:
        from config import SESSION_STRING
    elif not is_config:
        from sample_config import SESSION_STRING

queue = []  # This is where the whole song queue is stored
playing = False  # Tells if something is playing or not

# Pyrogram Client
if not HEROKU:
    app = Client("tgvc", api_id=API_ID, api_hash=API_HASH)
else:
    app = Client(SESSION_STRING, api_id=API_ID, api_hash=API_HASH)

# Pytgcalls Client
vc = GroupCall(
    client=app,
    input_filename="input.raw",
    play_on_repeat=True,
    enable_logs_to_console=False,
)

# Arq Client
arq = ARQ(ARQ_API)


async def delete(message):
    await asyncio.sleep(10)
    await message.delete()


@app.on_message(filters.command("start") & filters.chat(SUDO_CHAT_ID))
async def start(_, message):
    await send(START_TEXT)


@app.on_message(filters.command("help") & filters.chat(SUDO_CHAT_ID))
async def help(_, message):
    await send(HELP_TEXT)


@app.on_message(filters.command("repo") & filters.chat(SUDO_CHAT_ID))
async def repo(_, message):
    await send(REPO_TEXT)


@app.on_message(filters.command("joinvc") & filters.user(SUDOERS))
async def joinvc(_, message):
    try:
        if vc.is_connected:
            await send("__**Bot Is Already In Voice Chat.**__")
            return
        chat_id = message.chat.id
        await vc.start(chat_id)
        await send("__**Joined The Voice Chat.**__")
    except Exception as e:
        print(str(e))
        await send(str(e))


@app.on_message(filters.command("rejoinvc") & filters.user(SUDOERS))
async def joinvc(_, message):
    try:
        if vc.is_connected:
            await send("__**Bot Is Already In Voice Chat.**__")
            return
        chat_id = message.chat.id
        await vc.reconnect()
        await send("__**Joined The Voice Chat.**__")
    except Exception as e:
        print(str(e))
        await send(str(e))


@app.on_message(filters.command("leavevc") & filters.user(SUDOERS))
async def leavevc(_, message):
    if not vc.is_connected:
        await send("__**Already Out Of Voice Chat.**__")
        return
    await vc.leave_current_group_call()
    await vc.stop()
    await send("__**Left The Voice Chat, Restarting Client....**__")
    os.execvp(
        f"python{str(pyver.split(' ')[0])[:3]}",
        [f"python{str(pyver.split(' ')[0])[:3]}", "main.py"],
    )


@app.on_message(filters.command("update") & filters.user(SUDOERS))
async def update_restart(_, message):
    await send(
        f'```{subprocess.check_output(["git", "pull"]).decode("UTF-8")}```'
    )
    os.execvp(
        f"python{str(pyver.split(' ')[0])[:3]}",
        [f"python{str(pyver.split(' ')[0])[:3]}", "main.py"],
    )


@app.on_message(filters.command("pause") & filters.chat(SUDO_CHAT_ID))
async def pause_song(_, message):
    vc.pause_playout()
    await send("**Paused The Music, Send /resume To Resume.**")


@app.on_message(filters.command("resume") & filters.chat(SUDO_CHAT_ID))
async def resume_song(_, message):
    vc.resume_playout()
    await send("**Resumed, Send /pause To Pause The Music.**")


@app.on_message(filters.command("volume") & filters.chat(SUDO_CHAT_ID))
async def volume_bot(_, message):
    usage = "**Usage:**\n/volume [1-200]"
    if len(message.command) != 2:
        await send(usage)
        return
    volume = int(message.text.split(None, 1)[1])
    if (volume < 1) or (volume > 200):
        await send(usage)
        return
    try:
        await vc.set_my_volume(volume=volume)
    except ValueError:
        await send(usage)
        return
    await send(f"**Volume Set To {volume}**")


@app.on_message(filters.command("play") & filters.chat(SUDO_CHAT_ID))
async def queuer(_, message):
    usage = "**Usage:**\n__**/play youtube/saavn/deezer Song_Name**__"
    if len(message.command) < 3:
        await send(usage)
        return
    text = message.text.split(None, 2)[1:]
    service = text[0].lower()
    song_name = text[1]
    requested_by = message.from_user.first_name
    services = ["youtube", "deezer", "saavn"]
    if service not in services:
        await send(usage)
        return
    if len(queue) > 0:
        await message.delete()
        await send("__**Added To Queue.__**")
        queue.append(
            {
                "service": service,
                "song": song_name,
                "requested_by": requested_by,
            }
        )
        await play()
        return
    await message.delete()
    queue.append(
        {
            "service": service,
            "song": song_name,
            "requested_by": requested_by,
        }
    )
    await play()


@app.on_message(
    filters.command("skip") & filters.user(SUDOERS) & ~filters.edited
)
async def skip(_, message):
    global playing
    if len(queue) == 0:
        await send("__**Queue Is Empty, Just Like Your Life.**__")
        return
    playing = False
    await send("__**Skipped!**__")
    await play()


@app.on_message(filters.command("queue") & filters.chat(SUDO_CHAT_ID))
async def queue_list(_, message):
    if len(queue) != 0:
        i = 1
        text = ""
        for song in queue:
            text += f"**{i}. Platform:** __**{song['service']}**__ " \
                     + f"| **Song:** __**{song['song']}**__\n"
            i += 1
        m = await send(text)
        await delete(message)
        await m.delete()

    else:
        m = await send("__**Queue Is Empty, Just Like Your Life.**__")
        await delete(message)
        await m.delete()


# Queue handler


async def play():
    global queue, playing
    while not playing:
        await asyncio.sleep(2)
        if len(queue) != 0:
            service = queue[0]["service"]
            song = queue[0]["song"]
            requested_by = queue[0]["requested_by"]
            if service == "youtube":
                playing = True
                del queue[0]
                try:
                    await ytplay(requested_by, song)
                except Exception as e:
                    print(str(e))
                    await send(str(e))
                    playing = False
                    pass
            elif service == "saavn":
                playing = True
                del queue[0]
                try:
                    await jiosaavn(requested_by, song)
                except Exception as e:
                    print(str(e))
                    await send(str(e))
                    playing = False
                    pass
            elif service == "deezer":
                playing = True
                del queue[0]
                try:
                    await deezer(requested_by, song)
                except Exception as e:
                    print(str(e))
                    await send(str(e))
                    playing = False
                    pass


# Deezer----------------------------------------------------------------------------------------


async def deezer(requested_by, query):
    global playing
    m = await send(f"__**Searching for {query} on Deezer.**__")
    try:
        songs = await arq.deezer(query, 1)
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
    await generate_cover_square(
        requested_by, title, artist, duration, thumbnail
    )
    await m.edit("__**Downloading And Transcoding.**__")
    await download_and_transcode_song(url)
    await m.delete()
    caption = f"🏷 **Name:** [{title[:35]}]({url})\n⏳ **Duration:** {duration}\n" \
               + f"🎧 **Requested By:** {requested_by}\n📡 **Platform:** Deezer"
    m = await app.send_photo(
        chat_id=SUDO_CHAT_ID,
        photo="final.png",
        caption=caption,
    )
    os.remove("final.png")
    await asyncio.sleep(int(songs[0]["duration"]))
    await m.delete()
    playing = False


# Jiosaavn--------------------------------------------------------------------------------------


async def jiosaavn(requested_by, query):
    global playing
    m = await send(f"__**Searching for {query} on JioSaavn.**__")
    try:
        songs = await arq.saavn(query)
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
    caption = f"🏷 **Name:** {sname[:35]}\n⏳ **Duration:** {sduration_converted}\n" \
               + f"🎧 **Requested By:** {requested_by}\n📡 **Platform:** JioSaavn"
    m = await app.send_photo(
        chat_id=SUDO_CHAT_ID,
        caption=caption,
        photo="final.png",
    )
    os.remove("final.png")
    await asyncio.sleep(int(sduration))
    await m.delete()
    playing = False


# Youtube Play-----------------------------------------------------


async def ytplay(requested_by, query):
    global playing
    ydl_opts = {"format": "bestaudio"}
    m = await send(f"__**Searching for {query} on YouTube.**__")
    try:
        results = await arq.youtube(query)
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
    caption = f"🏷 **Name:** [{title[:35]}]({link})\n⏳ **Duration:** {duration}\n" \
               + f"🎧 **Requested By:** {requested_by}\n📡 **Platform:** YouTube"
    m = await app.send_photo(
        chat_id=SUDO_CHAT_ID,
        caption=caption,
        photo="final.png",
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
        await send("__**You Can Only Play Telegram Files After The Queue Gets "
                   + "Finished.**__")
        return
    if not message.reply_to_message:
        await send("__**Reply to an audio.**__")
        return
    if message.reply_to_message.audio:
        if int(message.reply_to_message.audio.file_size) >= 104857600:
            await send("__**Bruh! Only songs within 100 MB.**__")
            playing = False
            return
        duration = message.reply_to_message.audio.duration
        if not duration:
            await send("__**Only Songs With Duration Are Supported.**__")
            return
        m = await send("__**Downloading.**__")
        song = await message.reply_to_message.download()
        await m.edit("__**Transcoding.**__")
        transcode(song)
        await m.edit(f"**Playing** __**{message.reply_to_message.link}.**__")
        await asyncio.sleep(duration)
        playing = False
        return
    await send("__**Only Audio Files (Not Document) Are Supported.**__")


async def send(text):
    m = await app.send_message(
        SUDO_CHAT_ID, text=text, disable_web_page_preview=True
    )
    return m


print(
    "\nBot Starting...\nFor Support Join https://t.me/PatheticProgrammers\n"
)


app.run()
