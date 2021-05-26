HEROKU = True  # NOTE Make it false if you're not deploying on heroku.

# NOTE these values are for heroku.
if HEROKU:
    from os import environ

    COVER_THEME = environ["COVER_THEME"]
    API_ID = int(environ["API_ID"])
    API_HASH = environ["API_HASH"]
    SUDO_CHAT_ID = int(
        environ["SUDO_CHAT_ID"]
    )  # Chat where the bot will play the music.
    SUDOERS = list(
        int(x) for x in environ.get("SUDOERS", "").split()
    )  # Users which have special control over the bot.
    SESSION_STRING = environ["SESSION_STRING"]  # Check Readme for session
    ARQ_API_KEY = environ["ARQ_API_KEY"]

# NOTE Fill this if you are not deploying on heroku.
if not HEROKU:
    COVER_THEME = "red"  # This can be red or green, red by default
    API_ID = 14371
    API_HASH = "e46b6c854d2bf58a0"
    SUDO_CHAT_ID = -1001485876964
    SUDOERS = [1243703097, 13216546]
    ARQ_API_KEY = "Get this from @ARQRobot"
# don't make changes below this line
ARQ_API = "https://thearq.tech"
