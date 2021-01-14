from __future__ import unicode_literals
import requests
import youtube_dl
import asyncio
import time
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from config import owner_id, bot_token, radio_link, sudo_chat_id

app = Client(":memory:", bot_token=bot_token, api_id=6, api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e")


# Get User Input
def kwairi(message):
    query = ""
    for i in message.command[1:]:
        query += f"{i} "
    return query
# For Blacklist filter
blacks = []


# Ping

@app.on_message(filters.command(["ping"]) & filters.chat(sudo_chat_id) & ~filters.edited)
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
    await message.reply_text("Hi I'm Telegram Voice Chat Bot. Join @TheHamkerChat For Support.")

# Help

@app.on_message(filters.command(["help"]) & filters.chat(sudo_chat_id) & ~filters.edited)
async def help(_, message: Message):
    global blacks
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    await message.reply_text('''Currently These Commands Are Supported.
/start To Start The bot.
/help To Show This Message.
/ping To Ping All Datacenters Of Telegram.
/end To Stop Any Playing Music.
"/jiosaavn <song_name>" To Play A Song From Jiosaavn.
"/ytsearch <song_name>" To Search For A Song On Youtube.
"/youtube <song_link>" To Play A Song From Youtube.
"/playlist <youtube_playlist_url> To Play A Playlist From Youtube".
/radio To Play Radio Continuosly.
/black To Blacklist A User.
/white To Whitelist A User.
/users To Get A List Of Blacklisted Users.

NOTE: Do Not Assign These Commands To Bot Via BotFather''')

# Jiosaavn
#Global vars
s = None
m = None
@app.on_message(filters.command(["jiosaavn"]) & filters.chat(sudo_chat_id) & ~filters.edited)
async def jiosaavn(_, message: Message):
    global blacks
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    global s
    global m
    
    if len(message.command) < 2:
        await message.reply_text("/jiosaavn requires an argument")
        return
    try:
        os.system("killall -9 mpv")
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

    m = await message.reply_text(f"Searching for `{query}` on JioSaavn")
    r = requests.get(f"https://jiosaavnapi.bhadoo.uk/result/?query={query}")


    sname = r.json()[0]['song']
    slink = r.json()[0]['media_url']
    ssingers = r.json()[0]['singers']

    await m.edit(f"Playing `{sname}-{ssingers}`\nRequested by - {message.from_user.mention}")
    s = await asyncio.create_subprocess_shell(f"mpv {slink} --no-video", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await s.wait()
    await m.delete()

# Youtube Searching

@app.on_message(filters.command(["ytsearch"]) & filters.chat(sudo_chat_id) & ~filters.edited)
async def youtube_search(_, message: Message):
    global blacks
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    try:
        await message.delete()
    except:
        pass
    
    if len(message.command) < 2:
        await message.reply_text("/ytsearch requires one argument")
        return

    query = kwairi(message)
    m = await message.reply_text(f"Searching for `{query}` on YouTube")
    results = YoutubeSearch(query, max_results=4).to_dict()
    i = 0
    text = ""
    while i < 4:
        text += f"Title - {results[i]['title']}\n"
        text += f"Duration - {results[i]['duration']}\n"
        text += f"Views - {results[i]['views']}\n"
        text += f"Channel - {results[i]['channel']}\n"
        text += f"https://youtube.com{results[i]['url_suffix']}\n\n"
        i += 1
    await m.edit(text, disable_web_page_preview=True)
    await asyncio.sleep(15)
    await m.delete()

# Youtube Playing

@app.on_message(filters.command(["youtube"]) & filters.chat(sudo_chat_id) & ~filters.edited)
async def youtube(_, message: Message):
    global blacks
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    global m
    global s


    if len(message.command) != 2:
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
        os.system("killall -9 mpv")
    except:
        pass
    try:
        os.remove("audio.mp3")
    except:
        pass 
    ydl_opts = {
        'format': 'bestaudio'
    }

    link = message.command[1]
    m = await message.reply_text("Parsing link...")
    try:
        response = requests.get(link)
    except:
        await m.edit("Link not found, or your internet is ded af")
        return
    await m.edit("Downloading....")
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        audio_file = ydl.prepare_filename(info_dict)
        ydl.process_info(info_dict)
        os.rename(audio_file, "audio.webm")
    await m.edit(f"Playing `{audio_file}`\nRequested by - {message.from_user.mention}")
    s = await asyncio.create_subprocess_shell(f"mpv audio.webm --no-video", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await s.wait()
    await m.delete()

# youtube playlist


@app.on_message(filters.command(["playlist"]) & filters.chat(sudo_chat_id) & ~filters.edited)
async def playlist(_, message: Message):
    global blacks
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return   
    global m
    global s


    if len(message.command) != 2:
        await message.reply_text("/playlist requires one youtube playlist link")
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
        os.system("killall -9 mpv")
    except:
        pass
    try:
        os.remove("audio.mp3")
    except:
        pass 

    link = message.command[1]
    ydl_opts = {
        'format': 'bestaudio'
    }

    m = await message.reply_text("Processing Playlist...")
    with youtube_dl.YoutubeDL():
        result = youtube_dl.YoutubeDL().extract_info(link, download=False)
    
        if 'entries' in result:
            video = result['entries']
            await m.edit(f"Found {len(result['entries'])} Videos In Playlist, Playing Them All.")
            ii = 1
            for i, item in enumerate(video):
                video = result['entries'][i]['webpage_url']
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(video, download=False)
                    audio_file = ydl.prepare_filename(info_dict)
                    ydl.process_info(info_dict)
                    os.rename(audio_file, "audio.webm")
                await m.edit(f"Playing `{result['entries'][i]['title']}`, Song Number `{ii}` In Playlist, `{len(result['entries']) - ii}` In Queue. \nRequested by - {message.from_user.mention}")
                s = await asyncio.create_subprocess_shell(f"mpv audio.webm --no-video", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                await s.wait()
                ii += 1
                os.system("rm audio.webm")
   



# Radio

@app.on_message(filters.command(["radio"]) & filters.chat(sudo_chat_id) & ~filters.edited)
async def radio(_, message: Message):
    global blacks
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    global m
    global s

    try:
        os.system("killall -9 mpv")
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
        os.remove("audio.mp3")
    except:
        pass
    m = await message.reply_text(f"Playing Radio\nRequested by - {message.from_user.mention}")
    s = await asyncio.create_subprocess_shell(f"mpv {radio_link} --no-video", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await s.wait()
    await m.delete()



# End Music

@app.on_message(filters.command(["end"]) & filters.chat(sudo_chat_id) & ~filters.edited)
async def end(_, message: Message):
    global blacks
    if message.from_user.id in blacks:
        await message.reply_text("You're Blacklisted, So Stop Spamming.")
        return
    try:
        os.remove("audio.mp3")
    except:
        pass

    try:
        await message.delete()
    except:
        pass
    try:
        os.system("killall -9 mpv")
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

    await message.reply_text(f"{message.from_user.mention} Stopped The Music.")



# Ban


@app.on_message(filters.command(["black"]) & filters.chat(sudo_chat_id) & ~filters.edited)
async def blacklist(_, message: Message):
    global blacks
    if message.from_user.id != owner_id:
        await message.reply_text("Only owner can blacklist users.")
        return
    if not message.reply_to_message:
        await message.reply_text("Reply to a message with /black to blacklist a user.")
        return
    if message.reply_to_message.from_user.id in blacks:
        await message.reply_text("This user is already blacklisted.")
        return
    blacks.append(message.reply_to_message.from_user.id)
    await message.reply_text(f"Blacklisted {message.reply_to_message.from_user.mention}")

# Unban

@app.on_message(filters.command(["white"]) & filters.chat(sudo_chat_id) & ~filters.edited)
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
        await message.reply_text(f"Whitelisted {message.reply_to_message.from_user.mention}")
    else:
        await message.reply_text("This user is already whitelisted.")

# Blacklisted users


@app.on_message(filters.command(["users"]) & filters.chat(sudo_chat_id) & ~filters.edited)
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

print("Bot Started!")
app.run()
