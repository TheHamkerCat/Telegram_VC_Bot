from __future__ import unicode_literals
import youtube_dl
import asyncio
import aiohttp
import time
import json
import os

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from youtube_search import YoutubeSearch
from config import owner_id, bot_token, radio_link, sudo_chat_id
from functions import (
        kwairi, convert_seconds, time_to_seconds,
        prepare, generate_cover_square,
        generate_cover
        )


app = Client(
    ":memory:",
    bot_token=bot_token,
    api_id=6,
    api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e",
)


# For Blacklist filter
blacks = []
# Global vars
s = None
m = None
current_player = None


# Global vars
s = None  # var for player
m = None  # var for Track art message
d = None  # for stopping interruption of current playing song
current_player = None  # gets current player ID
is_playing = False  # for restricting users while playing!


# Ping and repo


@app.on_message(filters.command("repo") & ~filters.edited)
async def repo(_, message: Message):
    await message.reply_text(
        "[Github](https://github.com/thehamkercat/Telegram_vc_bot)"
        + " | [Group](t.me/TheHamkerChat)",
        disable_web_page_preview=True,
    )


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
        """**Currently These Commands Are Supported.**
/start To Start The bot.
/help To Show This Message.
/ping To Ping All Datacenters Of Telegram.
/end To Stop Any Playing Music (only works for current user playing and to Admins).
/deezer "Song_Name" To Play A Song From Deezer.
/jiosaavn "Song_Name" To Play A Song From Jiosaavn.
/youtube "Song_Name" To Search For A Song And Play The Top-Most Song Or Play With A Link.
/playlist "Youtube_Playlist_Link" To Play A Playlist From Youtube.
/telegram While Taging a Song To Play From Telegram File.
/radio To Play Radio Continuosly.
/users To Get A List Of Blacklisted Users.

**Admin Commands**:
/black To Blacklist A User.
/white To Whitelist A User.

NOTE: Do Not Assign These Commands To Bot Via BotFather"""
    )


# Deezer----------------------------------------------------------------------------------------


@app.on_message(
    filters.command(["deezer"])
    & filters.chat(sudo_chat_id)
    & ~filters.edited
)
async def deezer(_, message: Message):
    global blacks, is_playing, current_player, s, m, d
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    elif is_playing:
        list_of_admins = await getadmins(message.chat.id)
        if message.from_user.id in list_of_admins:
            pass
        else:
            d = await message.reply_text(
                text="stop interrupting while others playing!",
                disable_notification=True,
            )
            await asyncio.sleep(2)  # 2 sec delay before deletion
            await d.delete()
            await message.delete()
            return

    elif len(message.command) < 2:
        await message.reply_text("/deezer requires an argument")
        return
    
    await prepare(s, m, message)
    
    query = kwairi(message)
    current_player = message.from_user.id
    is_playing = True
    m = await message.reply_text(f"Searching for `{query}`on Deezer")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://52.0.6.104:8000/deezer/{query}/1"
            ) as resp:
                r = json.loads(await resp.text())
        title = r[0]["title"]
        duration = convert_seconds(int(r[0]["duration"]))
        thumbnail = r[0]["thumbnail"]
        artist = r[0]["artist"]
        url = r[0]["url"]
    except:
        await m.edit(
            "Found Literally Nothing, You Should Work On Your English!"
        )
        is_playing=False
        return
    await m.edit("Generating Thumbnail")

    await generate_cover_square(message, title, artist, duration, thumbnail)

    await m.delete()
    m = await message.reply_photo(
        caption=f"Playing `{title}` Via Deezer #music\nRequested by {message.from_user.first_name}",
        photo="final.png",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("STOP", callback_data="end")]]
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
    is_playing = False


# Jiosaavn--------------------------------------------------------------------------------------


@app.on_message(
    filters.command(["jiosaavn"])
    & filters.chat(sudo_chat_id)
    & ~filters.edited
)
async def jiosaavn(_, message: Message):
    global blacks, is_playing, current_player, s, m, d

    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    elif is_playing:
        list_of_admins = await getadmins(message.chat.id)
        if message.from_user.id in list_of_admins:
            pass
        else:
            d = await message.reply_text(
                text="stop interrupting while others playing!",
                disable_notification=True,
            )
            await asyncio.sleep(2)  # 2 sec delay before deletion
            await d.delete()
            await message.delete()
            return

    elif len(message.command) < 2:
        await message.reply_text("/jiosaavn requires an argument")
        return

    await prepare(s, m, message)

    query = kwairi(message)
    current_player = message.from_user.id
    is_playing = True

    m = await message.reply_text(f"Searching for `{query}`on JioSaavn")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://jiosaavnapi.bhadoo.uk/result/?query={query}"
            ) as resp:
                r = json.loads(await resp.text())

        sname = r[0]["song"]
        slink = r[0]["media_url"]
        ssingers = r[0]["singers"]
        sthumb = r[0]["image"]
        sduration = r[0]["duration"]
        sduration_converted = convert_seconds(int(sduration))
    except Exception as e:
        await m.edit(
            "Found Literally Nothing!, You Should Work On Your English."
        )
        print(str(e))
        is_playing=False
        return
    await m.edit("Processing Thumbnail.")

    await generate_cover_square(message, sname, ssingers, sduration_converted, sthumb)

    await m.delete()
    m = await message.reply_photo(
        caption=f"Playing `{sname}` Via Jiosaavn #music\nRequested by {message.from_user.first_name}",
        photo="final.png",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("STOP", callback_data="end")]]
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
    is_playing = False


# Youtube Play-----------------------------------------------------------------------------------


@app.on_message(
    filters.command(["youtube"])
    & filters.chat(sudo_chat_id)
    & ~filters.edited
)
async def ytplay(_, message: Message):
    global blacks, is_playing, current_player, s, m, d

    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    elif is_playing:
        list_of_admins = await getadmins(message.chat.id)
        if message.from_user.id in list_of_admins:
            pass
        else:
            d = await message.reply_text(
                text="stop interrupting while others playing!",
                disable_notification=True,
            )
            await asyncio.sleep(2)  # 2 sec delay before deletion
            await d.delete()
            await message.delete()
            return

    elif len(message.command) < 2:
        await message.reply_text("/youtube requires one argument")
        return
    
    await prepare(s, m, message)
    
    ydl_opts = {"format": "bestaudio"}
    query = kwairi(message)
    current_player = message.from_user.id
    is_playing = True

    m = await message.reply_text(f"Searching for `{query}`on YouTube")
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"]
        thumbnail = results[0]["thumbnails"][0]
        duration = results[0]["duration"]
        views = results[0]["views"]
        if time_to_seconds(duration)>=1800: #duration limit
            await m.edit("Bruh! Only songs within 30 Mins")
            is_playing=False
            return    
    except Exception as e:
        await m.edit(
            "Found Literally Nothing!, You Should Work On Your English."
        )
        is_playing=False
        print(str(e))
        return
    await m.edit("Processing Thumbnail.")

    await generate_cover(message, title, views, duration, thumbnail)

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
            [[InlineKeyboardButton("STOP", callback_data="end")]]
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
    is_playing = False


# youtube playlist-------------------------------------------------------------------------------


@app.on_message(
    filters.command(["playlist"])
    & filters.chat(sudo_chat_id)
    & ~filters.edited
)
async def playlist(_, message: Message):
    global blacks, is_playing, current_player, s, m, d

    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    elif is_playing:
        list_of_admins = await getadmins(message.chat.id)
        if message.from_user.id in list_of_admins:
            pass
        else:
            d = await message.reply_text(
                text="stop interrupting while others playing!",
                disable_notification=True,
            )
            await asyncio.sleep(2)  # 2 sec delay before deletion
            await d.delete()
            await message.delete()
            return
    elif message.entities[1]["type"] != "url" or len(message.command) != 2:
        await message.reply_text(
            "/playlist requires one youtube playlist link"
        )

    await prepare(s, m, message)

    link = message.command[1]
    ydl_opts = {"format": "bestaudio"}
    current_player = message.from_user.id
    is_playing = True

    m = await message.reply_text("Processing Playlist...")
    try:
        with youtube_dl.YoutubeDL():
            result = youtube_dl.YoutubeDL().extract_info(
                link, download=False
            )

            if "entries" in result:
                video = result["entries"]
                await m.edit(
                    f"Found {len(result['entries'])} Videos In Playlist, Playing Them All.\n>>>Requested by {message.from_user.first_name}<<<"
                )
                ii = 1
                for i in video:
                    video = result["entries"][i]["webpage_url"]
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        info_dict = ydl.extract_info(video, download=False)
                        audio_file = ydl.prepare_filename(info_dict)
                        ydl.process_info(info_dict)
                        os.rename(audio_file, "audio.webm")
                    await m.edit(
                        f"Playing `{result['entries'][i]['title']}`. \nSong Number `{ii}` In Playlist. \n`{len(result['entries']) - ii}` In Queue. \nRequested by - {message.from_user.mention}"
                    )
                    s = await asyncio.create_subprocess_shell(
                        "mpv audio.webm --no-video",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    await s.wait()
                    ii += 1
                    os.remove("audio.webm")
                await s.wait()
                await m.delete()
                is_playing = False
    except Exception as e:
        await m.edit("Found Literally Nothing, Or YoutubeDl Ded AF")
        print(str(e))
        return


# Telegram Audio--------------------------------------------------------------------------------


@app.on_message(
    filters.command(["telegram"])
    & filters.chat(sudo_chat_id)
    & ~filters.edited
)
async def tgplay(_, message: Message):
    global blacks, is_playing, current_player, s, m, d

    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    elif is_playing:
        list_of_admins = await getadmins(message.chat.id)
        if message.from_user.id in list_of_admins:
            pass
        else:
            d = await message.reply_text(
                text="stop interrupting while others playing!",
                disable_notification=True,
            )
            await asyncio.sleep(2)  # 2 sec delay before deletion
            await d.delete()
            await message.delete()
            return

    elif not message.reply_to_message:
        await message.reply_text("Reply To A Telegram Audio To Play It.")
        return

    await prepare(s, m, message)

    current_player = message.from_user.id
    if message.reply_to_message.audio:
        if int(message.reply_to_message.audio.file_size) >= 104857600:
            await message.reply_text('Bruh! Only songs within 100 MB')
            return
    elif message.reply_to_message.document:
        if int(message.reply_to_message.document.file_size) >= 104857600:
            await message.reply_text('Bruh! Only songs within 100 MB')
            return
    is_playing = True
    m = await message.reply_text("Downloading")
    await app.download_media(
        message.reply_to_message, file_name="audio.webm"
    )
    await m.edit(
        f"Playing `{message.reply_to_message.link}` via Telegram.\n>>>Requested by {message.from_user.first_name}<<<"
    )
    s = await asyncio.create_subprocess_shell(
        "mpv downloads/audio.webm --no-video",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await s.wait()
    await m.delete()
    is_playing = False
    os.remove("downloads/audio.webm")


# Radio-----------------------------------------------------------------------------------------


@app.on_message(
    filters.command(["radio"])
    & filters.chat(sudo_chat_id)
    & ~filters.edited
)
async def radio(_, message: Message):
    global blacks, is_playing, current_player, s, m, d

    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    elif is_playing:
        list_of_admins = await getadmins(message.chat.id)
        if message.from_user.id in list_of_admins:
            pass
        else:
            d = await message.reply_text(
                text="stop interrupting while others playing!",
                disable_notification=True,
            )
            await asyncio.sleep(2)  # 2 sec delay before deletion
            await d.delete()
            await message.delete()
            return

    await prepare(s, m, message)

    current_player = message.from_user.id
    m = await message.reply_text(
        f"Playing Radio\nRequested by - {message.from_user.mention}"
    )
    s = await asyncio.create_subprocess_shell(
        f"mpv --no-cache {radio_link} --no-video",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await s.wait()
    await m.delete()


# End Music-------------------------------------------------------------------------------------


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
    global blacks, m, s, is_playing

    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    list_of_admins = await getadmins(message.chat.id)
    if message.from_user.id not in list_of_admins:
        await message.reply_text(
            "Well, you're not admin or Current Player, SO YOU CAN'T STOP"
            + " ME, LOL"
        )
        return

    await prepare(s, m, message)

    is_playing = False
    await message.reply_text(
        f"{message.from_user.mention} Stopped The Music."
    )


@app.on_callback_query(filters.regex("end"))
async def end_callback(_, CallbackQuery):
    global blacks, m, s, is_playing
    list_of_admins = await getadmins(CallbackQuery.message.chat.id)
    if CallbackQuery.from_user.id not in list_of_admins:
        await app.answer_callback_query(
            CallbackQuery.id,
            "Well, you're not admin or Current Player, SO YOU CAN'T STOP"
            + " ME, LOL",
            show_alert=True,
        )
        return

    chat_id = int(CallbackQuery.message.chat.id)
    if CallbackQuery.from_user.id in blacks:
        return

    await prepare(s, m, Message)

    is_playing = False
    await app.send_message(
        chat_id,
        f"{CallbackQuery.from_user.mention} Stopped The Music.",
    )


# Ban


@app.on_message(
    filters.command(["black"])
    & filters.chat(sudo_chat_id)
    & ~filters.edited
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
    filters.command(["white"])
    & filters.chat(sudo_chat_id)
    & ~filters.edited
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
    filters.command(["users"])
    & filters.chat(sudo_chat_id)
    & ~filters.edited
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


print(
    "\nBot Starting...\nFor Support Join https://t.me/PatheticProgrammers\n"
)
app.run()
