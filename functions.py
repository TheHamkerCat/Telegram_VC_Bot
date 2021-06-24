import asyncio
import functools
import os

import aiofiles
import ffmpeg
import youtube_dl
from aiohttp import ClientSession
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.raw.types import InputGroupCall
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.phone import EditGroupCallTitle
from Python_ARQ import ARQ

from db import db

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

app = Client(
    SESSION_STRING if HEROKU else "tgvc", api_id=API_ID, api_hash=API_HASH
)
session = ClientSession()
arq = ARQ(ARQ_API, ARQ_API_KEY, session)
themes = ["darkred", "lightred", "green", "purple", "skyblue", "dark", "black"]


def get_theme(chat_id) -> str:
    theme = "purple"
    if chat_id not in db:
        db[chat_id] = {}
    if "theme" not in db[chat_id]:
        db[chat_id]["theme"] = theme
    theme = db[chat_id]["theme"]
    return theme


def change_theme(name: str, chat_id):
    if chat_id not in db:
        db[chat_id] = {}
    if "theme" not in db[chat_id]:
        db[chat_id]["theme"] = "green"
    db[chat_id]["theme"] = name


# Get default service from config
def get_default_service() -> str:
    services = ["youtube", "deezer", "saavn"]
    try:
        config_service = DEFAULT_SERVICE.lower()
        if config_service in services:
            return config_service
        else:           # Invalid DEFAULT_SERVICE
            return "youtube"
    except NameError:   # DEFAULT_SERVICE not defined
        return "youtube"


async def pause_skip_watcher(message: Message, duration: int, chat_id: int):
    try:
        chat_id = message.chat.id
        db[chat_id]["call"].set_is_mute(False)
        if "skipped" not in db[chat_id]:
            db[chat_id]["skipped"] = False
        if "paused" not in db[chat_id]:
            db[chat_id]["paused"] = False
        if "stopped" not in db[chat_id]:
            db[chat_id]["stopped"] = False
        if "replayed" not in db[chat_id]:
            db[chat_id]["replayed"] = False
        restart_while = False
        while True:
            for _ in range(duration * 10):
                if db[chat_id]["skipped"]:
                    db[chat_id]["skipped"] = False
                    return await message.delete()
                if db[chat_id]["paused"]:
                    while db[chat_id]["paused"]:
                        await asyncio.sleep(0.1)
                        continue
                if db[chat_id]["stopped"]:
                    restart_while=True
                    break
                if db[chat_id]["replayed"]:
                    restart_while = True
                    db[chat_id]["replayed"] = False
                    break
                if "queue_breaker" in db[chat_id] and db[chat_id]["queue_breaker"] != 0:
                    break
                await asyncio.sleep(0.1)
            if not restart_while:
                break
            restart_while = False
            await asyncio.sleep(0.1)
        db[chat_id]["skipped"] = False
    except:
        pass


async def change_vc_title(title: str, chat_id):
    peer = await app.resolve_peer(chat_id)
    chat = await app.send(GetFullChannel(channel=peer))
    data = EditGroupCallTitle(call=chat.full_chat.call, title=title)
    await app.send(data)


def transcode(filename: str, chat_id: str):
    ffmpeg.input(filename).output(
        f"input{chat_id}.raw",
        format="s16le",
        acodec="pcm_s16le",
        ac=2,
        ar="48k",
        loglevel="error",
    ).overwrite_output().run()
    os.remove(filename)


# Download song
async def download_and_transcode_song(url, chat_id):
    song = f"{chat_id}.mp3"
    async with session.get(url) as resp:
        if resp.status == 200:
            f = await aiofiles.open(song, mode="wb")
            await f.write(await resp.read())
            await f.close()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, functools.partial(transcode, song, chat_id)
    )


# Convert seconds to mm:ss
def convert_seconds(seconds: int):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(
        int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":")))
    )


# Change image size
def changeImageSize(maxWidth: int, maxHeight: int, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


# Generate cover for youtube


async def generate_cover(
    requested_by, title, views_or_artist, duration, thumbnail, chat_id
):
    async with session.get(thumbnail) as resp:
        if resp.status == 200:
            f = await aiofiles.open(f"background{chat_id}.png", mode="wb")
            await f.write(await resp.read())
            await f.close()
    background = f"./background{chat_id}.png"
    final = f"final{chat_id}.png"
    temp = f"temp{chat_id}.png"
    image1 = Image.open(background)
    image2 = Image.open(f"etc/foreground_{get_theme(chat_id)}.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save(temp)
    img = Image.open(temp)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("etc/font.otf", 32)
    draw.text((190, 550), f"Title: {title}", (255, 255, 255), font=font)
    draw.text((190, 590), f"Duration: {duration}", (255, 255, 255), font=font)
    draw.text(
        (190, 630),
        f"Views/Artist: {views_or_artist}",
        (255, 255, 255),
        font=font,
    )
    draw.text(
        (190, 670), f"Requested By: {requested_by}", (255, 255, 255), font=font
    )
    img.save(final)
    os.remove(temp)
    os.remove(background)
    try:
        await change_vc_title(title, chat_id)
    except Exception:
        await app.send_message(chat_id, text="[ERROR]: FAILED TO EDIT VC TITLE, MAKE ME ADMIN.")
        pass
    return final


# Deezer


async def deezer(requested_by, query, message: Message):
    m = await message.reply_text(
        f"__**Searching for {query} on Deezer.**__", quote=False
    )
    songs = await arq.deezer(query, 1)
    if not songs.ok:
        return await m.edit(songs.result)
    songs = songs.result
    title = songs[0].title
    duration = convert_seconds(int(songs[0].duration))
    thumbnail = songs[0].thumbnail
    artist = songs[0].artist
    db[chat_id]["currently"] = {"artist": artist, "song": title, "query": query}
    url = songs[0].url
    await m.edit("__**Downloading And Transcoding.**__")
    cover, _ = await asyncio.gather(
        generate_cover(
            requested_by, title, artist, duration, thumbnail, message.chat.id
        ),
        download_and_transcode_song(url, message.chat.id),
    )
    await m.delete()
    caption = (
        f"🏷 **Name:** [{title[:45]}]({url})\n⏳ **Duration:** {duration}\n"
        + f"🎧 **Requested By:** {message.from_user.mention}\n📡 **Platform:** Deezer"
    )
    m = await message.reply_photo(
        photo=cover,
        caption=caption,
    )
    os.remove(cover)
    duration = int(songs[0]["duration"])
    await pause_skip_watcher(m, duration, message.chat.id)
    await m.delete()


async def get_lyric(query: str, artist, song):
    if song and artist:
        q = song + artist
    elif song:
        q = song
    else:
        q = artist
    res = await arq.lyrics(q)
    if res.result == "Couldn't find any lyrics for that song!":
        res = await arq.lyrics(query)
    return res.result


# saavn


async def saavn(requested_by, query, message):
    m = await message.reply_text(
        f"__**Searching for {query} on JioSaavn.**__", quote=False
    )
    songs = await arq.saavn(query)
    if not songs.ok:
        return await m.edit(songs.result)
    songs = songs.result
    sname = songs[0].song
    slink = songs[0].media_url
    ssingers = songs[0].singers
    db[chat_id]["currently"] = {"artist": ssingers[0] if type(ssingers) == list else ssingers, "song": sname, "query": query}
    sthumb = songs[0].image
    sduration = songs[0].duration
    sduration_converted = convert_seconds(int(sduration))
    await m.edit("__**Downloading And Transcoding.**__")
    cover, _ = await asyncio.gather(
        generate_cover(
            requested_by,
            sname,
            ssingers,
            sduration_converted,
            sthumb,
            message.chat.id,
        ),
        download_and_transcode_song(slink, message.chat.id),
    )
    await m.delete()
    caption = (
        f"🏷 **Name:** {sname[:45]}\n⏳ **Duration:** {sduration_converted}\n"
        + f"🎧 **Requested By:** {message.from_user.mention}\n📡 **Platform:** JioSaavn"
    )
    m = await message.reply_photo(
        photo=cover,
        caption=caption,
    )
    os.remove(cover)
    duration = int(sduration)
    await pause_skip_watcher(m, duration, message.chat.id)
    await m.delete()


# Youtube


async def youtube(requested_by, query, message):
    ydl_opts = {"format": "bestaudio", "quiet": True}
    m = await message.reply_text(
        f"__**Searching for {query} on YouTube.**__", quote=False
    )
    results = await arq.youtube(query)
    if not results.ok:
        return await m.edit(results.result)
    results = results.result
    link = f"https://youtube.com{results[0].url_suffix}"
    title = results[0].title
    db[chat_id]["currently"] = {"artist": None, "song": title, "query": query}
    thumbnail = results[0].thumbnails[0]
    duration = results[0].duration
    views = results[0].views
    if time_to_seconds(duration) >= 1800:
        return await m.edit("__**Bruh! Only songs within 30 Mins.**__")
    await m.edit("__**Processing Thumbnail.**__")
    cover = await generate_cover(
        requested_by, title, views, duration, thumbnail, message.chat.id
    )
    await m.edit("__**Downloading Music.**__")
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        audio_file = ydl.prepare_filename(info_dict)
        ydl.process_info(info_dict)
    await m.edit("__**Transcoding.**__")
    song = f"audio{message.chat.id}.webm"
    os.rename(audio_file, song)
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, functools.partial(transcode, song, message.chat.id)
    )
    await m.delete()
    caption = (
        f"🏷 **Name:** [{title[:45]}]({link})\n⏳ **Duration:** {duration}\n"
        + f"🎧 **Requested By:** {message.from_user.mention}\n📡 **Platform:** YouTube"
    )
    m = await message.reply_photo(
        photo=cover,
        caption=caption,
    )
    os.remove(cover)
    duration = int(time_to_seconds(duration))
    await pause_skip_watcher(m, duration, message.chat.id)
    await m.delete()


# Telegram


async def telegram(_, __, message):
    global db
    chat_id = message.chat.id
    if chat_id not in db:
        db[chat_id] = {}
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
    title = message.reply_to_message.audio.title
    performer = message.reply_to_message.audio.performer
    db[chat_id]["currently"] = {"artist": performer, "song": title, "query": None}
    song = await message.reply_to_message.download()
    await m.edit("__**Transcoding.**__")
    try:
        if message.reply_to_message.audio.title:
            title = message.reply_to_message.audio.title
        else:
            title = message.reply_to_message.audio.performer
        await change_vc_title(title, chat_id)
    except Exception:
        await app.send_message(chat_id, text="[ERROR]: FAILED TO EDIT VC TITLE, MAKE ME ADMIN.")
        pass
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, functools.partial(transcode, song, chat_id)
    )
    await m.edit(f"**Playing** __**{message.reply_to_message.link}.**__")
    await pause_skip_watcher(m, duration, message.chat.id)
    try:
        os.remove(song)
    except:
        pass
