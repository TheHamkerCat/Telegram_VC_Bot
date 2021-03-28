HEROKU = True   # NOTE Make it false if you're not deploying on heroku.

# NOTE these values are for heroku.
if HEROKU:
    from os import environ
    API_ID = int(environ["API_ID"])
    API_HASH = environ["API_HASH"]
    SUDO_CHAT_ID = int(environ["SUDO_CHAT_ID"])
    OWNER_ID = int(environ["OWNER_ID"])
    SESSION_STRING = environ["SESSION_STRING"]

# NOTE Fill this if you are not deploying on heroku.
if not HEROKU:
    API_ID = 14371
    API_HASH = "e46b6c854d2bf58a0"
    SUDO_CHAT_ID = -1001485876964
    OWNER_ID = 1243703097


# don't make changes below this line
ARQ_API = "http://35.240.133.234:8000"
