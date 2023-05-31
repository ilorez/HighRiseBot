import json
from users import getUserLang

#load BotMessages.json that contain all message bot say
with open("data/BotMessages.json","r") as f:
    messagesData = json.load(f)

# return message message from botMessages by using name and num of language and lang that come from user profile
async def getMessage(user,name,num):
    lang = (await getUserLang(user.id))
    if not lang:
        lang = "ENG"

    return messagesData[name][num][lang]
