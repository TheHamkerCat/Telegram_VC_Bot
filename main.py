from __future__ import unicode_literals
import youtube_dl
import asyncio
import aiohttp
import aiofiles
import time
import json
import os
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from youtube_search import YoutubeSearch
from config import owner_id, bot_token, radio_link, sudo_chat_id

app = Client(
    ":memory:",
    bot_token=bot_token,
    api_id=6,
    api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e",
)


# Get User Input
def kwairi(message):
    query = ""
    for i in message.command[1:]:
        query += f"{i} "
    return query


def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Os Determination

if os.name == 'nt':
    kill = "tskill"
else:
    kill = "killall -9"

# For Blacklist filter
blacks = []
# Global vars
s = None
m = None
current_player = None


# Ping and repo

@app.on_message(filters.command("repo") & ~filters.edited)
async def repo(_, message: Message):
    await message.reply_text(
        "[Github](https://github.com/thehamkercat/Telegram_vc_bot)"
        + " | [Group](t.me/TheHamkerChat)", disable_web_page_preview=True)


@app.on_message(
    filters.command(["ping"]) & filters.chat(sudo_chat_id) & ~filters.edited
)
async def ping(_, message):
    global blacks
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    start_time = int(round(time.time() * 1000))
    m = await message.reply_text(".")
    end_time = int(round(time.time() * 1000))
    await m.edit(f"{end_time - start_time} ms")


# Start


@app.on_message(filters.command(["start"]) & ~filters.edited)
async def start(_, message: Message):
    global blacks
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    await message.reply_text(
        "Hi I'm Telegram Voice Chat Bot. Join @PatheticProgrammers For Support."
    )


# Help


@app.on_message(
    filters.command(["help"]) & filters.chat(sudo_chat_id) & ~filters.edited
)
async def help(_, message: Message):
    global blacks
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    await message.reply_text(
        """Currently These Commands Are Supported.
/start To Start The bot.
/help To Show This Message.
/ping To Ping All Datacenters Of Telegram.
/end To Stop Any Playing Music (only works for current user playing and to Admins).
"/deezer" To Play A Song From Deezer.
"/jiosaavn" To Play A Song From Jiosaavn.
"/youtube" To Search For A Song And Play The Top-Most Song Or Play With A Link.
"/playlist" To Play A Playlist From Youtube.
/telegram To Play A Song Directly From Telegram File.
/radio To Play Radio Continuosly.
/users To Get A List Of Blacklisted Users.

Admin Commands:
/black To Blacklist A User.
/white To Whitelist A User.

NOTE: Do Not Assign These Commands To Bot Via BotFather"""
    )


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

# Deezer


@app.on_message(
    filters.command(["deezer"])
    & filters.chat(sudo_chat_id)
    & ~filters.edited
)
async def deezer(_, message: Message):
    global blacks
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    global s
    global m
    global current_player

    if len(message.command) < 2:
        await message.reply_text("/jiosaavn requires an argument")
        return
    try:
        os.system(f"{kill} mpv")
    except:
        pass
    try:
        await m.delete()
    except:
        pass
    try:
        await message.delete()
    except:
        pass
    query = kwairi(message)
    current_player = message.from_user.id
    m = await message.reply_text(f"Searching for `{query}`on Deezer")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://52.0.6.104:8000/deezer/{query}/1"
            ) as resp:
                r = json.loads(await resp.text())
    except Exception as e:
        await m.edit(str(e))
        return
    title = r[0]['title']
    duration = convert_seconds(int(r[0]['duration']))
    thumbnail = r[0]['thumbnail']
    artist = r[0]['artist']
    url = r[0]['url']
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()
    image1 = Image.open("./background.png")
    image2 = Image.open("etc/foreground_square.png")
    image3 = changeImageSize(600, 500, image1)
    image4 = changeImageSize(600, 500, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("etc/font.otf", 20)
    draw.text(
        (150, 380), f"Title: {title}", (255, 255, 255), font=font
    )
    draw.text(
        (150, 405), f"Artist: {artist}", (255, 255, 255), font=font
    )
    draw.text(
        (150, 430),
        f"Duration: {duration} Seconds",
        (255, 255, 255),
        font=font,
    )
    draw.text(
        (150, 455),
        f"Played By: {message.from_user.first_name}",
        (255, 255, 255),
        font=font,
    )
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")
    await m.delete()
    m = await message.reply_photo(
        caption=f"Playing `{title}` Via Deezer #music\nRequested by {message.from_user.first_name}",
        photo="final.png",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "STOP", callback_data="end"
                    )
                ]
            ]
        ),
        parse_mode="markdown",
    )

    s = await asyncio.create_subprocess_shell(
        f"mpv {url} --no-video",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await s.wait()
    await m.delete()


# Jiosaavn


@app.on_message(
    filters.command(["jiosaavn"])
    & filters.chat(sudo_chat_id)
    & ~filters.edited
)
async def jiosaavn(_, message: Message):
    global blacks
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    global s
    global m
    global current_player

    if len(message.command) < 2:
        await message.reply_text("/jiosaavn requires an argument")
        return
    try:
        os.system(f"{kill} mpv")
    except:
        pass
    try:
        await m.delete()
    except:
        pass
    try:
        await message.delete()
    except:
        pass

    query = kwairi(message)
    current_player = message.from_user.id

    m = await message.reply_text(f"Searching for `{query}`on JioSaavn")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://jiosaavnapi.bhadoo.uk/result/?query={query}"
            ) as resp:
                r = json.loads(await resp.text())
    except Exception as e:
        await m.edit(str(e))
        return
    sname = r[0]["song"]
    slink = r[0]["media_url"]
    ssingers = r[0]["singers"]
    sthumb = r[0]["image"]
    sduration = r[0]["duration"]
    sduration_converted = convert_seconds(int(sduration))
    await m.edit("Processing Thumbnail.")
    async with aiohttp.ClientSession() as session:
        async with session.get(sthumb) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image1 = Image.open("./background.png")
    image2 = Image.open("etc/foreground_square.png")
    image3 = changeImageSize(600, 500, image1)
    image4 = changeImageSize(600, 500, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("etc/font.otf", 20)
    draw.text(
        (150, 380), f"Title: {sname}", (255, 255, 255), font=font
    )
    draw.text(
        (150, 405), f"Artist: {ssingers}", (255, 255, 255), font=font
    )
    draw.text(
        (150, 430),
        f"Duration: {sduration_converted} Seconds",
        (255, 255, 255),
        font=font,
    )
    draw.text(
        (150, 455),
        f"Played By: {message.from_user.first_name}",
        (255, 255, 255),
        font=font,
    )
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")
    await m.delete()
    m = await message.reply_photo(
        caption=f"Playing `{sname}` Via Jiosaavn #music\nRequested by {message.from_user.first_name}",
        photo="final.png",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "STOP", callback_data="end"
                    )
                ]
            ]
        ),
        parse_mode="markdown",
    )

    s = await asyncio.create_subprocess_shell(
        f"mpv {slink} --no-video",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await s.wait()
    await m.delete()


# Youtube Play

@app.on_message(
    filters.command(["youtube"]) & filters.chat(sudo_chat_id) & ~filters.edited
)
async def ytplay(_, message: Message):
    global blacks
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    global m
    global s
    global current_player

    if len(message.command) < 2:
        await message.reply_text("/youtube requires one argument")
        return
    try:
        await message.delete()
    except:
        pass
    try:
        await m.delete()
    except:
        pass
    try:
        os.system(f"{kill} mpv")
    except:
        pass
    try:
        os.remove("audio.webm")
    except:
        pass
    ydl_opts = {"format": "bestaudio"}
    query = kwairi(message)
    current_player = message.from_user.id
    m = await message.reply_text(f"Searching for `{query}`on YouTube")
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
    except Exception as e:
        await m.edit(str(e))
        return
    link = f"https://youtube.com{results[0]['url_suffix']}"
    title = results[0]["title"]
    thumbnail = results[0]["thumbnails"][0]
    duration = results[0]["duration"]
    views = results[0]["views"]
    await m.edit("Processing Thumbnail.")
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image1 = Image.open("./background.png")
    image2 = Image.open("etc/foreground.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("etc/font.otf", 32)
    draw.text((190, 550), f"Title: {title}", (255, 255, 255), font=font)
    draw.text(
        (190, 590), f"Duration: {duration}", (255, 255, 255), font=font
    )
    draw.text((190, 630), f"Views: {views}", (255, 255, 255), font=font)
    draw.text(
        (190, 670),
        f"Played By: {message.from_user.first_name}",
        (255, 255, 255),
        font=font,
    )
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")
    await m.edit("Downloading Music.")
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        audio_file = ydl.prepare_filename(info_dict)
        ydl.process_info(info_dict)
        os.rename(audio_file, "audio.webm")
    await m.delete()
    m = await message.reply_photo(
        caption=f"Playing [{title}]({link}) Via YouTube #music\nRequested by {message.from_user.first_name}",
        photo="final.png",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "STOP", callback_data="end"
                    )
                ]
            ]
        ),
        parse_mode="markdown",
    )
    os.remove("final.png")
    s = await asyncio.create_subprocess_shell(
        "mpv audio.webm --no-video",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await s.wait()
    await m.delete()


# youtube playlist


@app.on_message(
    filters.command(["playlist"])
    & filters.chat(sudo_chat_id)
    & ~filters.edited
)
async def playlist(_, message: Message):
    global blacks
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    global m
    global s
    global current_player

    if len(message.command) != 2:
        await message.reply_text(
            "/playlist requires one youtube playlist link"
        )
        return
    try:
        await message.delete()
    except:
        pass
    try:
        await m.delete()
    except:
        pass
    try:
        os.system(f"{kill} mpv")
    except:
        pass
    try:
        os.remove("audio.webm")
    except:
        pass

    link = message.command[1]
    ydl_opts = {"format": "bestaudio"}
    current_player = message.from_user.id

    m = await message.reply_text("Processing Playlist...")
    with youtube_dl.YoutubeDL():
        result = youtube_dl.YoutubeDL().extract_info(link, download=False)

        if "entries" in result:
            video = result["entries"]
            await m.edit(
                f"Found {len(result['entries'])} Videos In Playlist, Playing Them All.\n>>>Requested by {message.from_user.first_name}<<<"
            )
            ii = 1
            for i, item in enumerate(video):
                video = result["entries"][i]["webpage_url"]
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(video, download=False)
                    audio_file = ydl.prepare_filename(info_dict)
                    ydl.process_info(info_dict)
                    os.rename(audio_file, "audio.webm")
                await m.edit(
                    f"Playing `{result['entries'][i]['title']}`, Song Number `{ii}` In Playlist, `{len(result['entries']) - ii}` In Queue. \nRequested by - {message.from_user.mention}"
                )
                s = await asyncio.create_subprocess_shell(
                    "mpv audio.webm --no-video",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await s.wait()
                ii += 1
                os.remove("audio.webm")


# Telegram Audio


@app.on_message(
    filters.command(["telegram"]) & filters.chat(sudo_chat_id) & ~filters.edited
)
async def tgplay(_, message: Message):
    global blacks
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    global m
    global s
    global current_player

    if not message.reply_to_message:
        await message.reply_text("Reply To A Telegram Audio To Play It.")
        return
    try:
        await message.delete()
    except:
        pass
    try:
        await m.delete()
    except:
        pass
    try:
        os.system(f"{kill} mpv")
    except:
        pass
    try:
        os.remove("audio.webm")
    except:
        pass
    try:
        os.remove("downloads/audio.webm")
    except:
        pass
    current_player = message.from_user.id
    m = await message.reply_text("Downloading")
    await app.download_media(message.reply_to_message, file_name="audio.webm")
    await m.edit(f"Playing `{message.reply_to_message.link}` via Telegram.\n>>>Requested by {message.from_user.first_name}<<<")
    s = await asyncio.create_subprocess_shell(
        "mpv downloads/audio.webm --no-video",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await s.wait()
    await m.delete()
    os.remove("downloads/audio.webm")


# Radio


@app.on_message(
    filters.command(["radio"]) & filters.chat(sudo_chat_id) & ~filters.edited
)
async def radio(_, message: Message):
    global blacks
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    global m
    global s
    global current_player

    try:
        os.system(f"{kill} mpv")
    except:
        pass
    try:
        await m.delete()
    except:
        pass
    try:
        await message.delete()
    except:
        pass

    try:
        os.remove("audio.webm")
    except:
        pass
    current_player = message.from_user.id
    m = await message.reply_text(
        f"Playing Radio\nRequested by - {message.from_user.mention}"
    )
    s = await asyncio.create_subprocess_shell(
        f"mpv {radio_link} --no-video",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await s.wait()
    await m.delete()


# End Music


async def getadmins(chat_id):
    admins = []
    async for i in app.iter_chat_members(chat_id, filter="administrators"):
        admins.append(i.user.id)
    admins.append(current_player)  # Includes Current Player ID
    admins.append(owner_id)
    return admins


@app.on_message(
    filters.command(["end"]) & filters.chat(sudo_chat_id) & ~filters.edited
)
async def end(_, message: Message):
    global blacks
    global m
    global s

    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    list_of_admins = await getadmins(message.chat.id)
    if message.from_user.id not in list_of_admins:
        await message.reply_text("Well, you're not admin or Current Player, SO YOU CAN'T STOP"
                                 + " ME, LOL")
        return
    try:
        os.remove("audio.webm")
    except:
        pass

    try:
        await message.delete()
    except:
        pass
    try:
        os.system(f"{kill} mpv")
    except:
        pass
    try:
        s.terminate()
    except:
        pass
    try:
        await m.delete()
    except:
        pass

    await message.reply_text(
        f"{message.from_user.mention} Stopped The Music."
    )


@app.on_callback_query(filters.regex("end"))
async def end_callback(_, CallbackQuery):
    list_of_admins = await getadmins(CallbackQuery.message.chat.id)
    if CallbackQuery.from_user.id not in list_of_admins:
        await app.answer_callback_query(
            CallbackQuery.id, "Well, you're not admin or Current Player, SO YOU CAN'T STOP"
            + " ME, LOL", show_alert=True)
        return
    global blacks
    global m
    global s

    chat_id = int(CallbackQuery.message.chat.id)
    if CallbackQuery.from_user.id in blacks:
        return
    try:
        os.remove("audio.webm")
    except:
        pass
    try:
        os.system(f"{kill} mpv")
    except:
        pass
    try:
        s.terminate()
    except:
        pass
    try:
        await m.delete()
    except:
        pass
    await app.send_message(
        chat_id,
        f"{CallbackQuery.from_user.mention} - {CallbackQuery.from_user.id} Stopped The Music.",
    )


# Ban


@app.on_message(
    filters.command(["black"]) & filters.chat(sudo_chat_id) & ~filters.edited
)
async def blacklist(_, message: Message):
    global blacks
    if message.from_user.id != owner_id:
        await message.reply_text("Only owner can blacklist users.")
        return
    if not message.reply_to_message:
        await message.reply_text(
            "Reply to a message with /black to blacklist a user."
        )
        return
    if message.reply_to_message.from_user.id in blacks:
        await message.reply_text("This user is already blacklisted.")
        return
    blacks.append(message.reply_to_message.from_user.id)
    await message.reply_text(
        f"Blacklisted {message.reply_to_message.from_user.mention}"
    )


# Unban


@app.on_message(
    filters.command(["white"]) & filters.chat(sudo_chat_id) & ~filters.edited
)
async def whitelist(_, message: Message):
    global blacks
    if message.from_user.id != owner_id:
        await message.reply_text("Only owner can whitelist users.")
        return
    if not message.reply_to_message:
        await message.reply_text("Reply to a message to whitelist a user.")
        return
    if message.reply_to_message.from_user.id in blacks:
        blacks.remove(message.reply_to_message.from_user.id)
        await message.reply_text(
            f"Whitelisted {message.reply_to_message.from_user.mention}"
        )
    else:
        await message.reply_text("This user is already whitelisted.")


# Blacklisted users


@app.on_message(
    filters.command(["users"]) & filters.chat(sudo_chat_id) & ~filters.edited
)
async def users(client, message: Message):
    global blacks
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    output = "Blacklisted Users:\n"
    n = 1
    for i in blacks:
        usern = (await client.get_users(i)).mention
        output += f"{n}. {usern}\n"
        n += 1
    if len(blacks) == 0:
        await message.reply_text("No Users Are Blacklisted")
        return
    await message.reply_text(output)


print("Bot Starting...\nFor Support Join https://t.me/PatheticProgrammers\n")
app.run()
