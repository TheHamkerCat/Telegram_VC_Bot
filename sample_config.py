HEROKU = True  # NOTE Make it false if you're not deploying on heroku.

# NOTE these values are for heroku & Docker.
if HEROKU:
    from os import environ

    from dotenv import load_dotenv

    load_dotenv()  # take environment variables from .env.
    BOT_TOKEN = environ["BOT_TOKEN"]
    ARQ_API_KEY = environ["ARQ_API_KEY"]
    CHAT_ID = int(environ["CHAT_ID"])
    DEFAULT_SERVICE = environ.get("DEFAULT_SERVICE") or "youtube"
    STREAM_URL = environ["STREAM_URL"]
    STREAM_KEY = environ["STREAM_KEY"]

# NOTE Fill this if you are not deploying on heroku.
if not HEROKU:
    BOT_TOKEN = ""
    ARQ_API_KEY = "Get this from @ARQRobot"
    CHAT_ID = -100546355432
    DEFAULT_SERVICE = "saavn"  # Must be one of "youtube"/"saavn"
    STREAM_URL = "rtmps://dc5-1.rtmp.t.me/s/"  # Must be a valid stream url.
    STREAM_KEY = "Get this by starting a stream in Telegram video chat."

# don't make changes below this line
ARQ_API = "https://arq.hamker.in"
