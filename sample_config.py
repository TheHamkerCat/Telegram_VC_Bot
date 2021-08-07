HEROKU = True  # NOTE Make it false if you're not deploying on heroku.

# NOTE these values are for heroku & Docker.
if HEROKU:
    from os import environ

    from dotenv import load_dotenv

    load_dotenv()  # take environment variables from .env.
    API_ID = int(environ["7353928"])
    API_HASH = environ["c7a30161995acf9a0ba6037fe8a7788f"]
    SESSION_STRING = environ[
        "AQCPnZhs9EViCSWJKCFlwQMn7pCs6v30oP2q2VE37qU8782ehBWklEcx_JcWEKAEyTYk8TC9OMX9DMDR0rey55T1X1eKd01ri4LMOLHlL1jv-g6CmZ0N_Xz07E9AHsr_9jXHTAFUMUlHHodEIL7fgNDtEVqDdNbo7mM0mWUMDr7RBQZufCm7EuQW0Sq6o1lfXg7Hp_fQTcCCBLkYeO39W-AYQ9iuTsJTIihirrKlf_AJH408gVPc2gtGJKUBfzx0A29QWpn6bRt945VoISAWzUtPIJb1jRW4ScOERyKqqIakTES25FNFPQTjSJrSJRN5qfdBSleTdgO-MJzdaBQsznsNcVW_CAA"
    ]  # Check Readme for session
    ARQ_API_KEY = environ["OVSRAZ-RXBFHP-WGPVSN-WUZXIO-ARQ"]
    CHAT_ID = int(environ["-1001501310293"])
    DEFAULT_SERVICE = environ.get("DEFAULT_SERVICE") or "youtube"

# NOTE Fill this if you are not deploying on heroku.
if not HEROKU:
    API_ID = 14371
    API_HASH = "e46b6c854d2bf58a0"
    ARQ_API_KEY = "Get this from @ARQRobot"
    CHAT_ID = -100546355432
    DEFAULT_SERVICE = "saavn"  # Must be one of "youtube"/"saavn"

# don't make changes below this line
ARQ_API = "https://thearq.tech"
