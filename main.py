from __future__ import unicode_literals
import youtube_dl
import asyncio
import time
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from config import owner_id, sudo_chat_id, api_id, api_hash, ARQ_API
from pytgcalls import GroupCall
from Python_ARQ import ARQ
from functions import (
    convert_seconds,
    time_to_seconds,
    download_and_transcode_song,
    transcode,
    generate_cover_square,
    generate_cover,
)
from misc import HELP_TEXT, USERBOT_ONLINE_TEXT


# Global vars
playing = False
queue = []
chat_joined = False
input_file = "input.raw"


app = Client("tgvc", api_id=api_id, api_hash=api_hash)
vc = GroupCall(app, input_file)
arq = ARQ(ARQ_API)


# Join Voice Chat


@app.on_message(
    filters.command("joinvc") & filters.user(owner_id) & ~filters.edited
)
async def joinvc(_, message):
    global chat_joined
    try:
        if chat_joined:
            await message.reply_text("Bot Is Already In Voice Chat.")
            return
        chat_id = message.chat.id
        await vc.start(chat_id)
        chat_joined = True
        m = await message.reply_text("Joined The Voice Chat.")
    except Exception as e:
        print(str(e))
        await app.send_message(owner_id, text=str(e))


# Leave vc


@app.on_message(
    filters.command("leavevc") & filters.user(owner_id) & ~filters.edited
)
async def leavevc(_, message):
    global chat_joined
    if not chat_joined:
        await message.reply_text("Already out of the voice chat")
        return
    chat_joined = False
    m = await message.reply_text("Left The Voice Chat")


# Kill The Script


@app.on_message(filters.command("kill") & filters.user(owner_id))
async def killbot(_, message):
    await message.reply_text("Killed!")
    quit()


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
                print(f"Playing {song} via {service}")
                playing = True
                del queue[0]
                try:
                    await ytplay(requested_by, song)
                except Exception as e:
                    print(str(e))
                    await app.send_message(owner_id, text=str(e))
                    pass
            elif service == "saavn":
                print(f"Playing {song} via {service}")
                playing = True
                del queue[0]
                try:
                    await jiosaavn(requested_by, song)
                except Exception as e:
                    print(str(e))
                    await app.send_message(owner_id, text=str(e))
                    pass
            elif service == "deezer":
                print(f"Playing {song} via {service}")
                playing = True
                del queue[0]
                try:
                    await deezer(requested_by, song)
                except Exception as e:
                    print(str(e))
                    await app.send_message(owner_id, text=str(e))
                    pass


# Queue Append


@app.on_message(
    filters.command("play") & ~filters.edited & filters.chat(sudo_chat_id)
    )
async def queuer(_, message):
    if len(message.command) < 3:
        await message.reply_text(
            "**Usage:**\n/play youtube/saavn/deezer [song_name]"
        )
        return
    await message.delete()
    text = message.text.split(None, 2)[1:]
    service = text[0]
    song_name = text[1]
    requested_by = message.from_user.first_name
    services = ["youtube", "deezer", "saavn"]
    if service not in services:
        await app.send_message(
            message.chat.id,
            text="**Usage:**\n/play youtube/saavn/deezer [song_name]",
        )
        return
    queue.append(
        {"service": service, "song": song_name, "requested_by": requested_by}
    )
    m = await app.send_message(message.chat.id, text=f"Added To Queue.")


# Skip command


@app.on_message(
    filters.command("skip") & filters.chat(sudo_chat_id) & ~filters.edited
)
async def skip(_, message):
    global playing
    if len(queue) == 0:
        m = await message.reply_text("Queue Is Empty, Just Like Your Life.")
        return
    playing = False
    m = await message.reply_text("Skipped!")


# Query command


@app.on_message(
    filters.command("queue") & filters.chat(sudo_chat_id) & ~filters.edited
)
async def queue_list(_, message):
    if len(queue) != 0:
        i = 1
        text = ""
        for song in queue:
            text += f"**{i}. Platform:** {song['service']} | **Song:** {song['song']}\n"
            i += 1
        m = await message.reply_text(text, disable_web_page_preview=True)
    else:
        m = await message.reply_text("Queue Is Empty, Just Like Your Life.")


# Repo



@app.on_message(filters.command("repo") & ~filters.edited)
async def repo(_, message: Message):
    m = await message.reply_text(
        "[Github](https://github.com/thehamkercat/Telegram_vc_bot)"
        + " | [Group](t.me/PatheticProgrammers)",
        disable_web_page_preview=True,
    )


# Start


@app.on_message(filters.command("start") & ~filters.edited)
async def start(_, message: Message):
    await message.reply_text(
        "Hi I'm Telegram Voice Chat Bot. Join @PatheticProgrammers For Support."
    )


# Help


@app.on_message(filters.command("help") & ~filters.edited)
async def help(_, message: Message):
    await message.reply_text(HELP_TEXT)


# Deezer----------------------------------------------------------------------------------------


async def deezer(requested_by, query):
    global playing
    m = await app.send_message(
        sudo_chat_id, text=f"Searching for `{query}` on Deezer"
    )
    try:
        songs = await arq.deezer(query, 1)
        title = songs[0].title
        duration = convert_seconds(int(songs[0].duration))
        thumbnail = songs[0].thumbnail
        artist = songs[0].artist
        url = songs[0].url
    except:
        await m.edit(
            "Found Literally Nothing, You Should Work On Your English!"
        )
        playing = False
        return
    await m.edit("Generating Thumbnail")
    await generate_cover_square(
        requested_by, title, artist, duration, thumbnail
    )
    await m.edit("Downloading And Transcoding.")
    await download_and_transcode_song(url)
    await m.delete()
    m = await app.send_photo(
        chat_id=sudo_chat_id,
        photo="final.png",
        caption=f"Playing [{title}]({url}) Via Deezer.",
    )
    os.remove("final.png")
    await asyncio.sleep(int(r[0]["duration"]))
    await m.delete()
    playing = False


# Jiosaavn--------------------------------------------------------------------------------------


async def jiosaavn(requested_by, query):
    global playing
    m = await app.send_message(
        sudo_chat_id, text=f"Searching for `{query}` on JioSaavn"
    )
    try:
        songs = await arq.saavn(query)
        sname = songs[0].song
        slink = songs[0].media_url
        ssingers = songs[0].singers
        sthumb = songs[0].image
        sduration = songs[0].duration
        sduration_converted = convert_seconds(int(sduration))
    except Exception as e:
        await m.edit(
            "Found Literally Nothing!, You Should Work On Your English."
        )
        print(str(e))
        playing = False
        return
    await m.edit("Processing Thumbnail.")
    await generate_cover_square(
        requested_by, sname, ssingers, sduration_converted, sthumb
    )
    await m.edit("Downloading And Transcoding.")
    await download_and_transcode_song(slink)
    await m.delete()
    m = await app.send_photo(
        chat_id=sudo_chat_id,
        caption=f"Playing `{sname}` Via Jiosaavn",
        photo="final.png",
    )
    os.remove("final.png")
    await asyncio.sleep(sduration)
    await m.delete()
    playing = False


# Youtube Play-----------------------------------------------------------------------------------


async def ytplay(requested_by, query):
    global playing
    ydl_opts = {"format": "bestaudio"}
    m = await app.send_message(
        sudo_chat_id, text=f"Searching for `{query}` on YouTube"
    )
    try:
        results = await arq.youtube(query, 1) 
        link = f"https://youtube.com{results[0].url_suffix}"
        title = results[0].title
        thumbnail = results[0].thumbnails[0]
        duration = results[0].duration
        views = results[0].views
        if time_to_seconds(duration) >= 1800:
            await m.edit("Bruh! Only songs within 30 Mins")
            playing = False
            return
    except Exception as e:
        await m.edit(
            "Found Literally Nothing!, You Should Work On Your English."
        )
        playing = False
        print(str(e))
        return
    await m.edit("Processing Thumbnail.")
    await generate_cover(requested_by, title, views, duration, thumbnail)
    await m.edit("Downloading Music.")
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        audio_file = ydl.prepare_filename(info_dict)
        ydl.process_info(info_dict)
    await m.edit("Transcoding")
    os.rename(audio_file, "audio.webm")
    transcode("audio.webm")
    await m.delete()
    m = await app.send_photo(
        chat_id=sudo_chat_id,
        caption=f"Playing [{title}]({link}) Via YouTube",
        photo="final.png",
    )
    os.remove("final.png")
    await asyncio.sleep(time_to_seconds(duration))
    playing = False
    await m.delete()


# Telegram Audio--------------------------------------------------------------------------------


@app.on_message(
    filters.command("telegram") & filters.chat(sudo_chat_id) & ~filters.edited
)
async def tgplay(_, message):
    global playing
    if len(queue) != 0:
        await message.reply_text(
            "You Can Only Play Telegram Files After The Queue Gets Finished."
        )
        return
    if not message.reply_to_message:
        await message.reply_text("Reply to an audio")
        return
    if message.reply_to_message.audio:
        if int(message.reply_to_message.audio.file_size) >= 104857600:
            await message.reply_text("Bruh! Only songs within 100 MB")
            playing = False
            return
    elif message.reply_to_message.document:
        if int(message.reply_to_message.document.file_size) >= 104857600:
            await message.reply_text("Bruh! Only songs within 100 MB")
            playing = False
            return
    m = await message.reply_text("Downloading")
    await app.download_media(message.reply_to_message, file_name="audio.webm")
    await m.edit(f"Playing `{message.reply_to_message.link}`")
    playing = False
    os.remove("downloads/audio.webm")


print(
    "\nBot Starting...\nFor Support Join https://t.me/PatheticProgrammers\n"
)

try:
    with app:
        app.send_message(sudo_chat_id, text=USERBOT_ONLINE_TEXT)
except:
    pass


try:
    app.run()
except KeyboardInterrupt:
    print("Killed!")
    exit()
