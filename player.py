import json
import datetime
import pytz
import asyncio




#! working with players.json
# return players data after covert it from json to dict 
def playersData():
    with open('players.json', 'r') as file:
        data = json.load(file)
    return data
# set data in players.json function
def setPlayerData(data):
    with open('players.json', 'w') as file:
            json.dump(data, file)

# return turn if player in json file and flase in other ways 
def isPlayer(id):
    data = playersData()
    return id in list(data.keys())

# give u table that contain players [['id','player1',100],['id','player2',30]] sorted by coins
## Define a function to use as the sorting key
def sort_key(item):
        return item[2]

async def getPlayers():
    players = []
    data = playersData()
    for player in data:
        players.append([player,data[player]['name'],data[player]["resourses"]["coins"]])
        

    # Sort the list based on the second element of each inner list
    players.sort(key=sort_key,reverse=True)
    return players 
# add user to players
def addPlayer(user):
    try:
        delFromTip(user.username)
        data = playersData()
        def_date = datetime.datetime(2023, 1, 1, 1, 0, 0,tzinfo=pytz.utc)
        def_date = def_date.strftime("%Y-%m-%d %H:%M:%S")
        defProf = {
        "name": user.username,
        "lastFish":def_date,
        "lastChop":def_date,
        "tools": {
        "axe": "wood",
        "rod": "wood"
        },
        "resourses": {
        "wood": 0,
        "fish": 0,
        "coins": 0
        }
    } #defualt profile values
        data[user.id] = defProf
        setPlayerData(data)
        print(f"the player {user.username}, {user.id} joined to game ")
    except:print(f"there a probleme when {user.id} want to join to game! (player.py addPlayer())")
# remove polayer by username
def delPlayer(username):
    d = 0
    data = playersData()
    for p in data:
        if data[p]['name'] == username:
            print(f"the player {p},{data[p]['name']} hase removed")
            del data[p]
            d = 1
            break
    with open('players.json', 'w') as file:
            json.dump(data, file)
    return d

# get leaderboard of players
## if user is player it return [len players,best 10 players,playerPos]
## if not return [len players,best 10 players]
async def leaderBorad(id):
    players = await getPlayers() # [[id, name,coins],[id, name,coins]]
    lenP = len(players)
    for i in range(lenP):
        if players[i][0] == id:
            return [lenP,players[:5],i+1]
    return [lenP,players[:5]]



#! working with tipPlayers.json
# return true if player in tipPlayers
def isTip(username):
    with open('tipPlayers.json', 'r') as file:
        data = json.load(file)
    return username in data['tips']
# add user to tipPlayers
def addTipPlayer(username):
    with open('tipPlayers.json', 'r') as file:
        data = json.load(file)
    try:
        data["tips"].append(username)
        with open('tipPlayers.json', 'w') as file:
            json.dump(data, file)
        return True
    except:return False
# remove player from tipPlayer return "done" and "username not found"
def delFromTip(username):
    with open('tipPlayers.json', 'r') as file:
        data = json.load(file)
    try:
        data["tips"].remove(username)
        with open('tipPlayers.json', 'w') as file:
            json.dump(data, file)
        return 1
    except:return 0



        




