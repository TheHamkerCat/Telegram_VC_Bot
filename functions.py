import asyncio
import os

import aiofiles
import ffmpeg
import youtube_dl
from aiohttp import ClientSession
from PIL import Image, ImageDraw, ImageFont
from Python_ARQ import ARQ

is_config = os.path.exists("config.py")

if is_config:
    from config import *
else:
    from sample_config import *

# Arq Client
session = ClientSession()
arq = ARQ(ARQ_API, ARQ_API_KEY, session)


def transcode(filename):
    ffmpeg.input(filename).output(
        "input.raw",
        format="s16le",
        acodec="pcm_s16le",
        ac=2,
        ar="48k",
        loglevel="error",
    ).overwrite_output().run()
    os.remove(filename)


# Download song
async def download_and_transcode_song(url):
    song = "song.mp3"
    async with session.get(url) as resp:
        if resp.status == 200:
            f = await aiofiles.open(song, mode="wb")
            await f.write(await resp.read())
            await f.close()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, transcode, song)


# Convert seconds to mm:ss
def convert_seconds(seconds):
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
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


# Generate cover for youtube


async def generate_cover(
    requested_by, title, views_or_artist, duration, thumbnail
):
    async with session.get(thumbnail) as resp:
        if resp.status == 200:
            f = await aiofiles.open("background.png", mode="wb")
            await f.write(await resp.read())
            await f.close()
    theme = (
        "foreground_green.png"
        if COVER_THEME == "green"
        else "foreground_red.png"
    )
    image1 = Image.open("./background.png")
    image2 = Image.open(f"etc/{theme}")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
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
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")
    return "final.png"


# Deezer


async def deezer(requested_by, query, message):
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
    url = songs[0].url
    await m.edit("__**Downloading And Transcoding.**__")
    cover, _ = await asyncio.gather(
        generate_cover(requested_by, title, artist, duration, thumbnail),
        download_and_transcode_song(url),
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
    await asyncio.sleep(int(songs[0]["duration"]))
    await m.delete()


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
    sthumb = songs[0].image
    sduration = songs[0].duration
    sduration_converted = convert_seconds(int(sduration))
    await m.edit("__**Downloading And Transcoding.**__")
    cover, _ = await asyncio.gather(
        generate_cover(
            requested_by, sname, ssingers, sduration_converted, sthumb
        ),
        download_and_transcode_song(slink),
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
    await asyncio.sleep(int(sduration))
    await m.delete()


# Youtube


async def youtube(requested_by, query, message):
    ydl_opts = {"format": "bestaudio"}
    m = await message.reply_text(
        f"__**Searching for {query} on YouTube.**__", quote=False
    )
    results = await arq.youtube(query)
    if not results.ok:
        return await m.edit(results.result)
    results = results.result
    link = f"https://youtube.com{results[0].url_suffix}"
    title = results[0].title
    thumbnail = results[0].thumbnails[0]
    duration = results[0].duration
    views = results[0].views
    if time_to_seconds(duration) >= 1800:
        return await m.edit("__**Bruh! Only songs within 30 Mins.**__")
    await m.edit("__**Processing Thumbnail.**__")
    cover = await generate_cover(
        requested_by, title, views, duration, thumbnail
    )
    await m.edit("__**Downloading Music.**__")
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        audio_file = ydl.prepare_filename(info_dict)
        ydl.process_info(info_dict)
    await m.edit("__**Transcoding.**__")
    song = "audio.webm"
    os.rename(audio_file, song)
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, transcode, song)
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
    await asyncio.sleep(int(time_to_seconds(duration)))
    await m.delete()
