from __future__ import unicode_literals
import youtube_dl
import asyncio
import ffmpeg
import aiohttp
import time
import json
import os
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.phone import LeaveGroupCall
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from config import owner_id, sudo_chat_id, api_id, api_hash
from pytgcalls import GroupCall
from functions import (
    convert_seconds,
    time_to_seconds,
    generate_cover_square,
    generate_cover,
    kill
)


app = Client(
    "tgvc",
    api_id=api_id,
    api_hash=api_hash
)


# For Blacklist filter
blacks = []
# Global vars
playing = False
queue = []
joined_chats = {}


# Admins list


async def getadmins(chat_id):
    admins = []
    async for i in app.iter_chat_members(chat_id, filter="administrators"):
        admins.append(i.user.id)
    admins.append(owner_id)
    return admins

@app.on_message(filters.command("kill") & filters.user(owner_id))
async def killbot(_, message):
    await message.reply_text("Killed!")
    quit()

# Join Voice Chat


@app.on_message(
    filters.command("joinvc") & filters.chat(sudo_chat_id) & ~filters.edited
    )
async def joinvc(_, message):
    global joined_chats
    if message.chat.id in joined_chats:
        await message.reply_text("Bot Is Already In Voice Chat.")
        return
    if len(message.command) != 2:
        await message.reply_text("/joinvc [CHAT_ID]")
        return
    try:
        chat_id = int(message.text.split(None, 1)[1])
        vc = GroupCall(app, 'input.raw')
        await vc.start(chat_id)
        joined_chats[chat_id] = vc
        await message.reply_text("Joined The Voice Chat.")
    except Exception as e:
        print(str(e))
        await app.send_message(owner_id, text=str(e))



# Leave Voice Chat


@app.on_message(
    filters.command("leavevc") & filters.chat(sudo_chat_id) & ~filters.edited
    )
async def leavevc(_, message):
    global joined_chats
    if message.chat.id not in joined_chats:
        await message.reply_text("Bot Is Not In Voice Chat.")
        return
    if len(message.command) != 2:
        await message.reply_text("/leavevc [CHAT_ID]")
        return
    try:
        chat_id = int(message.text.split(None, 1)[1])
        full_chat = await app.send(GetFullChannel(channel=(await app.resolve_peer(chat_id))))
        await app.send(LeaveGroupCall(call=full_chat.full_chat.call, source=0))
        del joined_chats[chat_id]
        await message.reply_text("Left The Voice Chat.")
    except Exception as e:
        print(str(e))
        await app.send_message(owner_id, text=str(e))


# Stop Playing


@app.on_message(
    filters.command("stop") & filters.chat(sudo_chat_id) & ~filters.edited
    )
async def stopvc(_, message):
    chat_id = message.chat.id
    if chat_id not in joined_chats:
        await message.reply_text("Already Stopped.")
        return
    try:
        (joined_chats[chat_id]).stop_playout() 
        await message.reply_text("Player Stopped!")
    except Exception as e:
        print(str(e))
        await app.send_message(owner_id, text=str(e))


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
                    pass
            elif service == "saavn":
                print(f"Playing {song} via {service}")
                playing = True
                del queue[0]
                try:
                    await jiosaavn(requested_by, song)
                except Exception as e:
                    print(str(e))
                    pass
            elif service == "deezer":
                print(f"Playing {song} via {service}")
                playing = True
                del queue[0]
                try:
                    await deezer(requested_by, song)
                except Exception as e:
                    print(str(e))
                    pass

# Queue Append


@app.on_message(
    filters.command("play") & filters.chat(sudo_chat_id) & ~filters.edited
    )
async def queuer(_, message):
    if message.from_user.id in blacks:
        return
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
        await app.send_message(message.chat.id,
            text="**Usage:**\n/play youtube/saavn/deezer [song_name]"
        )
        return
    queue.append({"service": service, "song": song_name, "requested_by": requested_by})
    m = await app.send_message(message.chat.id, text=f"Added To Queue.")
    await play()
    await asyncio.sleep(3)
    await m.delete()


# Skip command


@app.on_message(
    filters.command("skip") & filters.chat(sudo_chat_id) & ~filters.edited
)
async def skip(_, message):
    global playing
    if message.from_user.id in blacks:
        return
    if message.from_user.id not in await getadmins(sudo_chat_id):
        return
    if len(queue) == 0:
        m = await message.reply_text("Queue Is Empty, Just Like Your Life.")
        await asyncio.sleep(5)
        await m.delete()
        await message.delete()
        return
    playing = False
    try:
        os.system(f"{kill} mpv")
    except:
        pass
    m = await message.reply_text("Skipped!")
    await asyncio.sleep(5)
    await m.delete()
    await message.delete()


@app.on_message(
    filters.command("queue") & filters.chat(sudo_chat_id) & ~filters.edited
    )
async def queue_list(_, message):
    if message.from_user.id in blacks:
        return
    if len(queue) != 0:
        i = 1
        text = ""
        for song in queue:
            text += f"**{i}. Platform:** {song['service']} | **Song:** {song['song']}\n"
            i += 1
        m = await message.reply_text(text, disable_web_page_preview=True)
    else:
        m = await message.reply_text("Queue Is Empty, Just Like Your Life.")
    await asyncio.sleep(5)
    await m.delete()
    await message.delete()

# Ping and repo


@app.on_message(filters.command("repo") & ~filters.edited)
async def repo(_, message: Message):
    m = await message.reply_text(
        "[Github](https://github.com/thehamkercat/Telegram_vc_bot)"
        + " | [Group](t.me/TheHamkerChat)",
        disable_web_page_preview=True,
    )
    await asyncio.sleep(5)
    await m.delete()


@app.on_message(
    filters.command("ping") & filters.chat(sudo_chat_id) & ~filters.edited
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
/skip To Skip The Current Playing Music.
/play youtube/saavn/deezer [song_name]
/telegram While Taging a Song To Play From Telegram File.
/users To Get A List Of Blacklisted Users.

**Admin Commands**:
/black To Blacklist A User.
/white To Whitelist A User.

NOTE: Do Not Assign These Commands To Bot Via BotFather"""
    )


# Deezer----------------------------------------------------------------------------------------

async def deezer(requested_by, query):
    global playing
    m = await app.send_message(
        sudo_chat_id, text=f"Searching for `{query}` on Deezer"
    )
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://52.0.6.104:8000/deezer?query={query}&count=1"
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
        playing = False
        return
    await m.edit("Generating Thumbnail")
    await generate_cover_square(requested_by, title, artist, duration, thumbnail)

    await m.delete()
    m = await app.send_photo(
        chat_id=sudo_chat_id,
        photo="final.png",
        caption=f"Playing [{title}]({url}) Via Deezer."
    )

    s = await asyncio.create_subprocess_shell(
        f"mpv {url} --no-video",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await s.wait()
    await m.delete()
    playing = False


# Jiosaavn--------------------------------------------------------------------------------------

async def jiosaavn(requested_by, query):
    global playing
    m = await app.send_message(
        sudo_chat_id, text=f"Searching for `{query}` on JioSaavn"
    )
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
        playing = False
        return
    await m.edit("Processing Thumbnail.")
    await generate_cover_square(requested_by, sname, ssingers, sduration_converted, sthumb)
    await m.delete()
    m = await app.send_photo(
        chat_id=sudo_chat_id,
        caption=f"Playing `{sname}` Via Jiosaavn",
        photo="final.png"
    )

    s = await asyncio.create_subprocess_shell(
        f"mpv {slink} --no-video",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await s.wait()
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
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"]
        thumbnail = results[0]["thumbnails"][0]
        duration = results[0]["duration"]
        views = results[0]["views"]
        if time_to_seconds(duration) >= 1800:  # duration limit
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
    ffmpeg.input("audio.webm").output("input.raw", format='s16le', acodec='pcm_s16le',
        ac=2, ar='48k'
    ).overwrite_output().run()
    os.remove("audio.webm")
    await m.delete()
    m = await app.send_photo(
        chat_id=sudo_chat_id,
        caption=f"Playing [{title}]({link}) Via YouTube",
        photo="final.png"
    )
    os.remove("final.png")
    await asyncio.sleep(time_to_seconds(duration))
    playing = False
    await m.delete()


# Telegram Audio--------------------------------------------------------------------------------


@app.on_message(filters.command("telegram") &
        filters.chat(sudo_chat_id) & ~filters.edited
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
    s = await asyncio.create_subprocess_shell(
        "mpv downloads/audio.webm --no-video",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await s.wait()
    await m.delete()
    playing = False
    os.remove("downloads/audio.webm")


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


print(
    "\nBot Starting...\nFor Support Join https://t.me/PatheticProgrammers\n"
)

try:
    app.run()
except KeyboardInterrupt:
    print("Killed!")
    exit()
