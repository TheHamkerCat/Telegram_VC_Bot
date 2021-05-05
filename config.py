HEROKU = True   # NOTE Make it false if you're not deploying on heroku.

# NOTE these values are for heroku.
if HEROKU:
    from os import environ
    API_ID = int(environ["1414929"])
    API_HASH = environ["fcb063441a589281cd2075fd535b2f9a"]
    SUDO_CHAT_ID = int(environ["-1001238985376"]) # Chat where the bot will play the music.
    SUDOERS = list(int(x) for x in environ.get("941346758", "").split()) # Users which have special control over the bot.
    SESSION_STRING = environ["BQBTT1GDLNbazryvqDoSGAUPt2IRfmIF2WNjZEYqN4Gzed5lqF7CeOGTj3WtjaKqR2npFxLwEBt40f7zEHCrDJIXz3X_Sl6RtgtF_tLlGxCC9yvcqZJUOCwc6KOuLXtahxFKbDKUclYKIAwQLL3PTSGquyv9aactqQS292OVF8DM00KSg8KNEsLoGecmyHbzfXV3wN7xPDaBlgbtUjkgpZvp1klOtitqX7eI2iukaIbsnCw9Mu5XKogRpK9egy2mHPwOtBF60qqctNWLDCTZaeo0Oo3Vuecx5pZcNEGhjb_ObAz5ZUNklsjtHr1oZKFGaspXPGN_PogMlJhni3JXXOg-OBvPxgA"] # Check Readme for session

# NOTE Fill this if you are not deploying on heroku.
if not HEROKU:
    API_ID = 14371
    API_HASH = "e46b6c854d2bf58a0"
    SUDO_CHAT_ID = -1001485876964
    SUDOERS = [1243703097, 13216546]

# don't make changes below this line
ARQ_API = "https://thearq.tech"
