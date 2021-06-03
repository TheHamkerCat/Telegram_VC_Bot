HEROKU = True  # NOTE Make it false if you're not deploying on heroku.

# NOTE these values are for heroku & Docker.
if HEROKU:
    from os import environ
    from dotenv import load_dotenv
    
    load_dotenv()  # take environment variables from .env.
    API_ID = int(environ["API_ID"])
    API_HASH = environ["API_HASH"]
    SESSION_STRING = environ["SESSION_STRING"]  # Check Readme for session
    ARQ_API_KEY = environ["ARQ_API_KEY"]

# NOTE Fill this if you are not deploying on heroku.
if not HEROKU:
    API_ID = 14371
    API_HASH = "e46b6c854d2bf58a0"
    ARQ_API_KEY = "Get this from @ARQRobot"
# don't make changes below this line
ARQ_API = "https://thearq.tech"
