import json

with open("data/BotMessages.json","r") as f:
    messagesData = json.load(f)

async def getUserLang():
    pass

async def getMessage(user,name,num):
    lang = "DARIJA"
    return messagesData[name][num][lang]
