HEROKU = False  # NOTE Make it false if you're not deploying on heroku.

# NOTE these values are for heroku & Docker.
if HEROKU:
    from os import environ

    from dotenv import load_dotenv

    load_dotenv()  # take environment variables from .env.
    API_ID = int(environ["7250088"])
    API_HASH = environ["daff0c3742747fb7c5e4cffe479c05d9"]
    SESSION_STRING = environ["AQALSJNQWcjqLLTD6mHVN7PW6swL_St6C3deplHLUzV2tMdmLiJS5TEyxRnqNdzVVa_WdsmLxBBeBbONrZcy0iClwBIqELvkutsO4K5qE-hihWuE_3r90mAmND1TUGeKsAGgGG0YONL8plic5tMlXeJ8LWT_Hn59eiW8AVzZiYYr-MGf5EQxb2bTHoJqXUpKcvv9Tm9e2zFNWpfa-luBgvfPicIQCZmlZtnOWyXC_mq87LOha9sUrULQ0iASVBAFMvxX9fTIquZdub_MWYnUog3ucXoTB1WT_vgjAsXuz7hRC3qNXZuCEhiK2jhKbyg-B8jyzyKpssjcgVrg0g1Ht2uIc7DHFwA"]  # Check Readme for session
    ARQ_API_KEY = environ["DQNILI-XLCYOT-MHOOLF-PTXSAZ-ARQ"]
    CHAT_ID = int(environ["-1001317022158"])
    DEFAULT_SERVICE = environ.get("DEFAULT_SERVICE") or "youtube"

# NOTE Fill this if you are not deploying on heroku.
if not HEROKU:
    API_ID = 7250088
    API_HASH = "daff0c3742747fb7c5e4cffe479c05d9"
    ARQ_API_KEY = "DQNILI-XLCYOT-MHOOLF-PTXSAZ-ARQ"
    CHAT_ID = -1001317022158
    DEFAULT_SERVICE = "youtube"  # Must be one of "youtube"/"deezer"/"saavn"

# don't make changes below this line
ARQ_API = "https://thearq.tech"
