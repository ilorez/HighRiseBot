import json
from player import playersData,setPlayerData
# import asyncio
import datetime
import pytz
import random
# settings json
def getSettings():
    with open("settings.json",'r') as f:
        return json.load(f) 

# set rousours (coins, woods, fishs) to player by id
def setResour(id,coins,wood,fish):
    data = playersData()
    data[id]['resourses']["coins"] = coins
    data[id]['resourses']["wood"] = wood
    data[id]['resourses']["fish"] = fish
    setPlayerData(data)

# sell wood and fish for coins
## number wood = 1gold
## number fish = 1gold
## number = sttings['item']
async def sellItems(id):
    data = playersData()
    settings = getSettings() 
    coins = data[id]['resourses']["coins"]
    wood = data[id]['resourses']["wood"]
    fish = data[id]['resourses']["fish"]
    c_add = wood//settings['wood'] + fish//settings['fish']
    coins += c_add 
    wood = wood % settings['wood']
    fish = fish % settings['fish']
    setResour(id,coins,wood,fish)
    return c_add

# buy item axe[1-4] or fishing-rod[5-8]
## return True when the baught complete
## return false if user does't have enough coins
async def buyItem(id,num):
    data = playersData()
    settings = getSettings()
    player = data[id]
    coins = player["resourses"]["coins"]
    if num >=1 and num<=4:
        num -= 1 
        tool = "axe"
        tooln = "Axe"
    if num >=5 and num <= 8:
        num -= 5
        tool = "rod"
        tooln = "Fishing Rod"

    tType = list(settings["toolsPrix"][tool])[num]
    prix = settings["toolsPrix"][tool][tType]
    if prix <= coins:
        coins -= prix
        player["resourses"]["coins"] = coins
        player["tools"][tool] = tType
        data[id] = player
        setPlayerData(data)
        
        return f"\nYou have get {tType} {tooln} by {prix}\nYou still have {coins}Gala"
    
    return f"You need {-(coins-prix)} Gala to get this tool"

async def chop(id):
    data = playersData()
    settings = getSettings()
    player = data[id]
    lastChop = datetime.datetime.strptime(player["lastChop"], "%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
    diff = now - lastChop
    tseconds =int(diff.total_seconds())
    minutes = tseconds // 60
    seconds = tseconds % 60
    if minutes >= settings["chopToolSleep"]:
        tool_type = player["tools"]["axe"]
        range = settings["toolRange"]["axe"][tool_type]
        getWood = random.randint(range[0],range[1])
        player["resourses"]["wood"] += getWood 
        player["lastChop"] = now.strftime("%Y-%m-%d %H:%M:%S")
        data[id] = player
        setPlayerData(data)
        return getWood
    # format time
    wait_m = settings["chopToolSleep"] - minutes
    wait_s = 60 - seconds
    time_str = "{:02d}:{:02d}".format(wait_m, wait_s)
    return time_str
    
    

async def fish(id):
    data = playersData()
    settings = getSettings()
    player = data[id]
    lastChop = datetime.datetime.strptime(player["lastFish"], "%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
    diff = now - lastChop
    tseconds =int(diff.total_seconds())
    minutes = tseconds // 60
    seconds = tseconds % 60
    if minutes >= settings["fishToolSleep"]:
        tool_type = player["tools"]["rod"]
        range = settings["toolRange"]["rod"][tool_type]
        getWood = random.randint(range[0],range[1])
        player["resourses"]["fish"] += getWood 
        player["lastFish"] = now.strftime("%Y-%m-%d %H:%M:%S")
        data[id] = player
        setPlayerData(data)
        return getWood
    # format time
    wait_m = settings["fishToolSleep"] - minutes
    wait_s = 60 - seconds
    time_str = "{:02d}:{:02d}".format(wait_m, wait_s)
    return time_str







