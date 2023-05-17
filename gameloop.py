from datetime import datetime, timezone
from game import getSettings
from player import playersData, getPlayers

import asyncio
import json

# test if today is sunday return true if it false if not
def isSunday():
    today = datetime.today()
    if today.weekday() == 6:
        return True
    return False

# return today utc on format yyyy/mm/dd
def get_utc_date():
    # Get the current datetime in UTC
    now_utc = datetime.now(timezone.utc)
    # Format the datetime to yyyy/mm/dd format
    return now_utc.strftime("%Y/%m/%d")

# import and return all data players form data/allDataPlayers.json 
def allDataPlayers():
    with open("data/allDataPlayers.json","r") as f:
        allData = json.load(f)
    return allData

# import and return all winners form data/winners.json 
def allWinners():
    with open("data/winners.json","r") as f:
        winners = json.load(f)
    return winners

# test if data of this week has socked before
def isStocked():
    today = get_utc_date()
    winners = allWinners()
    if today in winners:
        return True
    return False

# calucle rewards
'''
[+]: calcule all sides reward room first/second/third players
'''
async def rewardCalcul():
    plNum = len(playersData())
    settings = getSettings()
    rewards = settings["reward"]
    allGold = plNum * settings["joinGold"]
    roomR = (allGold * rewards["room"])//100
    playersR = allGold - roomR
    firstP = (playersR * rewards["firstP"]) // 100
    secondP = (playersR * rewards["secondP"]) // 100
    thirdP = (playersR * rewards["thirdP"]) // 100
    roomR += playersR - (firstP+secondP+thirdP)

    return [allGold, roomR, firstP, secondP, thirdP]

# make dict of all rewards of this week
async def winnersTemp():
    winners = await getPlayers()
    winners = winners[:3]
    tapR = await rewardCalcul()
    temp = {
        "allGolds":tapR[0],
        "roomReward":tapR[1],
        "firstP":{
            "id":winners[0][0],
            "name":winners[0][1],
            "gala":winners[0][2],
            "winGolds":tapR[2]
        },
        "secondP":{
            "id":winners[1][0],
            "name":winners[1][1],
            "gala":winners[1][2],
            "winGolds":tapR[3]
        },
        "thirdP":{
            "id":winners[2][0],
            "name":winners[2][1],
            "gala":winners[2][2],
            "winGolds":tapR[4]
        }
    }
    return temp
# stock
'''
stock:
--> players.json in allDataPlayers.json
--> winners from players.json in winners.json
'''
async def stock(today):
    players = playersData()
    allW = allWinners()
    allPD = allDataPlayers()
    # today = get_utc_date()

    allPD[today] = players
    allW[today] = await winnersTemp()

    with open("data/allDataPlayers.json","w") as f:
        json.dump(allPD, f)
    with open("data/winners.json","w") as f:
        json.dump(allW, f)
# set data in players.json and tipPayers.json if default state
async def setDataZero():
    with open("players.json","w") as f:
        json.dump({},f)

    with open("tipPlayers.json","w") as f:
        json.dump({"tips": []},f)

async def getNextSettings():
    with open("data/nextSettings.json","r") as f:
        data = json.load(f)
    return data

# update seetings by copie settings from nextSeeting.json to settings.json
async def updateSettings():
    newSettings = await getNextSettings()
    with open("settings.json","w") as f:
        json.dump(newSettings,f)

# this function setLastweek in nxetSetting.json
async def setLastWeek(date):
    data = getNextSettings()
    data["lastWeek"] = date
    with open("data/nextSettings.json","w") as f:
        json.dump(data,f)

# this functio return winners of last week [[id,name,postion,gold],[id,name,postion,gold],[id,name,postion,gold]]
async def getWinnersTap(date):
    wins = allWinners()[date]
    tabN = ["firstP","secondP","thirdP"]
    pos = ["1st","2nd","3rd"]
    Tab = []
    for i in range (len(tabN)):
        Tab.append([wins[tabN[i]]["id"],wins[tabN[i]]["name"],pos[i],wins[tabN[i]]["winGolds"]])
    return Tab

# return days:hours:min:seconds that to week end
async def toWeekEnd():
    today = datetime.now(timezone.utc)
    if isSunday():
        days = 6
    else:
        days = 6 - today.weekday()
    hours = 22 - today.hour
    minutes = 59 - today.minute
    seconds = 59 - today.second
    time_str = f"{days} days {hours:02d}:{minutes:02d}:{seconds:02d}"
    return time_str
    

# return tippesd golds (reward golds)
async def tippsed():
    settings = getSettings()
    allGolds = len(playersData()) * settings["joinGold"]
    return allGolds

