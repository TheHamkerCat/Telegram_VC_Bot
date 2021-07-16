HEROKU = False  # NOTE Make it false if you're not deploying on heroku.

# NOTE these values are for heroku & Docker.
if HEROKU:
    from os import environ

    from dotenv import load_dotenv

    load_dotenv()  # take environment variables from .env.
    API_ID = int(environ["7250088"])
    API_HASH = environ["daff0c3742747fb7c5e4cffe479c05d9"]
    SESSION_STRING = environ["AQADrxDQYNNwSpfCkidlEMUebbgx6m3KsvPJe9bp0VcSP-EgWo1qtilJj6LwhVihG3n6QxFYCcLhp_6tx-zm4n-athAiuU6ujTr4ffU2q30SY5GdjopVooODYGE_57m50HAY2PHEfbn99ahmAx2qhSxUXxYVXLBzeE4Ou13OiXgY4jc57K1Lu9Y54tBIrMwhB4pwJt8OLVoldJOUg2Gy36OB50ekfQ-jxU8ISY-3udQyrTr3EkbUxfF0-no-zYXurb4z_1rigIyRztdF_HgaJBwohP24TomEpiA9iZ1X-TRzMtxoBF_MKozgDGjtEcb-xfQtbsN6cN02N9-I62bzMdVdZ4BFdQA"]  # Check Readme for session
    ARQ_API_KEY = environ["RGRPZF-ZKROHH-FXANMN-QMRQQJ-ARQ"]
    CHAT_ID = int(environ["-1001161933394"])
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
