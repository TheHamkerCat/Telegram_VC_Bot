HEROKU = True  # NOTE Make it false if you're not deploying on heroku.

# NOTE these values are for heroku & Docker.
if HEROKU:
    from os import environ

    from dotenv import load_dotenv

    load_dotenv()  # take environment variables from .env.
    API_ID = int(environ["12526930"])
    API_HASH = environ["87f898d3a86896d009772cb2582febc7"]
    SESSION_STRING = environ[
        "AQAzy44a0hDd4mKd6SNPM71sCNuYXkBAQk85MquvxIn5V3XbQiw5ICUF8FgzQRmW_idF8ja1LiOKnA-8FfguGPSuPF8TkLFePmQH-KWFdyUoVGrkToq4uTZRi5Uu5f2aWeQ1jeKfCwxOx-SW4oIWZj_GEGrEyvrSXgiet_AyWqKr5FtzTVwz_c0w0WhJrcBJjmBZXnjJbADN2LQvfcXasVOxhSU0YMe4LC1p7U6rYlhzAL9BBE5EsS7m3F-kOCc5A59axtAe4rcS_zGzmxbcQSR24JUrE-EIZbkhT4cWaWkZsjUua4is2NiLACqjxA8TVLuKqwN6FdcfR2Bb3g-vGVkwf9M0fQA"
    ]  # Check Readme for session
    ARQ_API_KEY = environ["YEALKC-FHCONU-KXOJTN-UAWLXD-ARQ"]
    CHAT_ID = int(environ["-1001431787572"])
    DEFAULT_SERVICE = environ.get("DEFAULT_SERVICE") or "youtube"
    BITRATE = int(environ["512"])

# NOTE Fill this if you are not deploying on heroku.
if not HEROKU:
    API_ID = 14371
    API_HASH = "e46b6c854d2bf58a0"
    ARQ_API_KEY = "Get this from @ARQRobot"
    CHAT_ID = -100546355432
    DEFAULT_SERVICE = "saavn"  # Must be one of "youtube"/"saavn"
    BITRATE = 512 # Must be 512/320

# don't make changes below this line
ARQ_API = "https://thearq.tech"
