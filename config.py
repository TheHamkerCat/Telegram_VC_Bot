
class Config(object):
  Api_id = int(os.getenv("Api ID"))
  Api_hash = os.getenv("Api Hash")
  Sudo_chat_id = int(os.getenv("Chat ID"))
  Owner_id = int(os.getenv("Owner ID"))


# Arq Api, don't make changes here
ARQ_API = "https://thearq.tech"
