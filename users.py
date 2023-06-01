import json
from game import getSettings

# import and convert data/allUsers.json to dict
async def getAllUsers():
    with open("data/allUsers.json","r",encoding='utf-8') as f:
        users = json.load(f)
    return users

# test if user old old new
async def isOldUser(search,index=0):
    users = await getAllUsers()
    for user in users["users"]:
        if user[index] == search:
            return True
    return False
# re_write allUsers.json with new value
async def setAllUsersData(data):
     with open("data/allUsers.json","w") as f:
        json.dump(data,f)
# new user
async def addUser(user):
    users = await getAllUsers()
    # get first lang in settings as default language for all users
    defaultLang = getSettings()["languages"][0]
    users['users'].append([user.id,user.username,defaultLang])
    await setAllUsersData(users)

#get data from inRoom.json
async def getInRoom():
    with open("data/inRoom.json","r",encoding='utf-8') as f:
        data = json.load(f)
    return data


# return True if user in room and false if not
async def inRoom(id):
    onlines = await getInRoom()
    for u in onlines["users"]:
        if u[1] == id:
            return True
    return False

# add user that joined Room to inRoom.json
async def joinedRoom(user):
    if await inRoom(user.id):
        return
    onlines = await getInRoom()
    onlines['users'].append([user.username,user.id])
    with open("data/inRoom.json","w") as f:
        json.dump(onlines,f)
# remove user if leaved room from inRoom.json
async def leavedRoom(id):
    if not await inRoom(id):
        return
    onlines = await getInRoom()
    for u in onlines["users"]:
        if u[1] == id:
            onlines["users"].remove(u)
    with open("data/inRoom.json","w") as f:
        json.dump(onlines,f)
# set inRoom.json in deault state no data on it
async def setRoomZero():
    with open("data/inRoom.json","w") as f:
        json.dump({"users": []},f)

# return id of user using username
async def getIdOldUser(username):
    users = await getAllUsers()
    for user in users["users"]:
        if user[1] == username:
            return user[0]
    return False

# return user lang from user profile
async def getUserLang(user_id):
    users = (await getAllUsers())["users"]
    for u in users:
        if u[0] == user_id:
            return u[2]
    return False

# change language of user
async def changeUserLang(user_id,lang):
    users = await getAllUsers()
    for u in users["users"]:
        if u[0] == user_id:
            if u[2] == lang:
                return
            u[2] = lang
    await setAllUsersData(users)


