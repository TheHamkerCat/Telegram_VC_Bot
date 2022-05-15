import asyncio
import os
import traceback
from shlex import quote
from subprocess import Popen, check_output

import aiofiles
from aiohttp import ClientSession
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client
from pyrogram.types import Message
from Python_ARQ import ARQ

from db import db

is_config = os.path.exists("config.py")

if is_config:
    from config import *
else:
    from sample_config import *

app = Client(
    "bot",
    in_memory=True,
    bot_token=BOT_TOKEN,
    api_id=6,
    api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e",
)
session = ClientSession()
arq = ARQ(ARQ_API, ARQ_API_KEY, session)

ffmpeg_proc = None

# Get default service from config
def get_default_service() -> str:
    services = ["youtube", "saavn"]
    try:
        config_service = DEFAULT_SERVICE.lower()
        if config_service in services:
            return config_service
        else:  # Invalid DEFAULT_SERVICE
            return "youtube"
    except NameError:  # DEFAULT_SERVICE not defined
        return "youtube"


async def pause_skip_watcher(message: Message, duration: int):
    try:
        if "skipped" not in db:
            db["skipped"] = False
        if "paused" not in db:
            db["paused"] = False
        if "stopped" not in db:
            db["stopped"] = False
        if "replayed" not in db:
            db["replayed"] = False
        restart_while = False
        while True:
            for _ in range(duration * 10):
                if db["skipped"]:
                    db["skipped"] = False
                    try:
                        ffmpeg_proc.kill()
                    except Exception as e:
                        print(e)
                        pass

                    return await message.delete()
                if db["paused"]:
                    while db["paused"]:
                        await asyncio.sleep(0.1)
                        continue
                if db["stopped"]:
                    restart_while = True
                    break
                if db["replayed"]:
                    restart_while = True
                    db["replayed"] = False
                    break
                if "queue_breaker" in db:
                    if db["queue_breaker"] != 0:
                        break
                await asyncio.sleep(0.1)
            if not restart_while:
                break
            restart_while = False
            await asyncio.sleep(0.1)
        db["skipped"] = False
    except Exception as e:
        e = traceback.format_exc()
        print(str(e))
        pass


# Play song
async def play_song_ffmpeg(url):
    global ffmpeg_proc

    if "http" in url:
        url = str(quote(url))

    if "youtube" in url:
        url = check_output(
            ["youtube-dl", "-f", "best", "--get-url", url]).decode()

    ffmpeg_proc = Popen(
        [
            "ffmpeg", "-re", "-nostdin", "-i", url, "-vcodec", "libx264",
            "-preset:v", "ultrafast", "-acodec", "aac", "-f", "flv",
            f"{STREAM_URL}{STREAM_KEY}",
        ],
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
    return sum(
        int(x) * 60 ** i
        for i, x in enumerate(reversed(str(time).split(":")))
    )


# Change image size
def change_image_size(max_width: int, max_height: int, image):
    width_ratio = max_width / image.size[0]
    height_ratio = max_height / image.size[1]
    new_width = int(width_ratio * image.size[0])
    new_height = int(height_ratio * image.size[1])
    new_image = image.resize((new_width, new_height))
    return new_image


async def send(*args, **kwargs):
    await app.send_message(CHAT_ID, *args, **kwargs)


# Generate cover for youtube
async def generate_cover(
    requested_by, title, artist, duration, thumbnail
):
    async with session.get(thumbnail) as resp:
        if resp.status == 200:
            f = await aiofiles.open("background.png", mode="wb")
            await f.write(await resp.read())
            await f.close()
    background = "./background.png"
    final = "final.png"
    temp = "temp.png"
    image1 = Image.open(background)
    image2 = Image.open("etc/foreground.png")
    image3 = change_image_size(1280, 720, image1)
    image4 = change_image_size(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save(temp)
    img = Image.open(temp)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("etc/font.otf", 32)
    draw.text(
        (190, 550), f"Title: {title}", (255, 255, 255), font=font
    )
    draw.text(
        (190, 590),
        f"Duration: {duration}",
        (255, 255, 255),
        font=font,
    )
    draw.text(
        (190, 630),
        f"Artist: {artist}",
        (255, 255, 255),
        font=font,
    )
    draw.text(
        (190, 670),
        f"Requested By: {requested_by}",
        (255, 255, 255),
        font=font,
    )
    img.save(final)
    os.remove(temp)
    os.remove(background)
    return final


async def run_async(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)


async def play_and_gencover(
    requested_by, title, artist, duration, thumbnail, url
):
    return await asyncio.gather(
        generate_cover(
            requested_by,
            title,
            artist,
            duration,
            thumbnail,
        ),
        play_song_ffmpeg(url),
    )


async def get_song(query: str, service: str):
    if service == "saavn":
        resp = await arq.saavn(query)
        if not resp.ok:
            return
        song = resp.result[0]
        title = song.song[0:30]
        duration = int(song.duration)
        thumbnail = song.image
        artist = (
            song.singers
            if not isinstance(song.singers, list)
            else song.singers[0]
        )
        url = song.media_url
    elif service == "youtube":
        resp = await arq.youtube(query)
        if not resp.ok:
            return
        song = resp.result[0]
        title = song.title[0:30]
        duration = time_to_seconds(song.duration)
        thumbnail = song.thumbnails[0]
        artist = song.channel
        url = "https://youtube.com" + song.url_suffix
    else:
        return

    return title, duration, thumbnail, artist, url


async def play_song(requested_by, query, message, service):
    m = await message.reply_text(
        f"__**Searching for {query} on {service}.**__", quote=False
    )
    # get song title, url etc
    song = await get_song(query, service)
    if not song:
        return await m.edit("There's no such song on " + service)

    title, duration, thumbnail, artist, url = song

    if service == "youtube":
        if duration >= 1800:
            return await m.edit("[ERROR]: SONG_TOO_BIG")

        await m.edit("__**Generating thumbnail.**__")
        cover = await generate_cover(
            requested_by,
            title,
            artist,
            convert_seconds(duration),
            thumbnail,
        )
        await m.edit("__**Playing in a few seconds...**__")

        await play_song_ffmpeg(url)
    else:
        await m.edit(
            "__**Generating thumbnail, Preparing to play.**__"
        )
        cover, _ = await play_and_gencover(
            requested_by,
            title,
            artist,
            convert_seconds(duration),
            thumbnail,
            url,
        )
    await m.delete()
    caption = f"""
**Name:** {title[:45]}
**Duration:** {convert_seconds(duration)}
**Requested By:** {message.from_user.mention}
**Platform:** {service}
"""
    await m.delete()
    m = await message.reply_photo(
        photo=cover,
        caption=caption,
    )
    os.remove(cover)
    await pause_skip_watcher(m, duration)
    await m.delete()


# Telegram


async def telegram(message):
    err = "__**Can't play that**__"
    reply = message.reply_to_message
    if not reply:
        return await message.reply_text(err)
    if not reply.audio:
        return await message.reply_text(err)
    if not reply.audio.duration:
        return await message.reply_text(err)
    if int(reply.audio.file_size) >= 104857600:
        return await message.reply_text("[ERROR]: SONG_TOO_BIG")
    m = await message.reply_text("__**Downloading.**__")
    song = await message.reply_to_message.download()
    await m.edit("__**Transcoding.**__")
    await play_song_ffmpeg(song)
    await m.edit(f"__**Playing {reply.link} in a moment**__",
                 disable_web_page_preview=True)
    await pause_skip_watcher(m, reply.audio.duration)
    if os.path.exists(song):
        os.remove(song)
