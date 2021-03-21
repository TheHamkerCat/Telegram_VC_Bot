import os
class Config(object):
  API_ID = int(os.getenv("Api ID"))
  API_HASH = os.getenv("Api Hash")
  SUDO_CHAT_ID = int(os.getenv("Chat ID"))
  OWNER_ID = int(os.getenv("Owner ID"))


# Arq Api, don't make changes here
ARQ_API = "https://thearq.tech"
