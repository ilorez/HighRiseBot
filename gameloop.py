from datetime import datetime, timezone
from game import getSettings
from player import playersData, getPlayers

import asyncio
import json

# test if today is sunday return true if it false if not
def isSunday():
    today = datetime.datetime.today()
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
async def stock():
    players = playersData()
    allW = allWinners()
    allPD = allDataPlayers()
    today = get_utc_date()

    allPD[today] = players
    allW[today] = await winnersTemp()

    with open("data/allDataPlayers.json","w") as f:
        json.dump(allPD, f)
    with open("data/winners.json","w") as f:
        json.dump(allW, f)


    
