HEROKU = False  # NOTE Make it false if you're not deploying on heroku.

# NOTE these values are for heroku & Docker.
if HEROKU:
    from os import environ

    from dotenv import load_dotenv

    load_dotenv()  # take environment variables from .env.
    API_ID = int(environ["API_ID"])
    API_HASH = environ["API_HASH"]
    SESSION_STRING = environ["SESSION_STRING"]  # Check Readme for session
    ARQ_API_KEY = environ["ARQ_API_KEY"]
    CHAT_ID = int(environ["CHAT_ID"])
    DEFAULT_SERVICE = environ.get("DEFAULT_SERVICE") or "youtube"

# NOTE Fill this if you are not deploying on heroku.
if not HEROKU:
    API_ID = 7250088
    API_HASH = "daff0c3742747fb7c5e4cffe479c05d9"
    ARQ_API_KEY = "RGRPZF-ZKROHH-FXANMN-QMRQQJ-ARQ"
    CHAT_ID = -1001161933394
    DEFAULT_SERVICE = "youtube"  # Must be one of "youtube"/"deezer"/"saavn"

# don't make changes below this line
ARQ_API = "https://thearq.tech"
