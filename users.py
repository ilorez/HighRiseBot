import json

# import and convert data/allUsers.json to dict
async def getAllUsers():
    with open("data/allUsers.json","r") as f:
        users = json.load(f)
    return users

# test if user old old new
async def isOldUser(id):
    users = await getAllUsers()
    for user in users["users"]:
        if user[0] == id:
            return True
    return False
# new user
async def addUser(user):
    users = await getAllUsers()
    users['users'].append([user.id,user.username])
    with open("data/allUsers.json","w") as f:
        json.dump(users,f)

#get data from inRoom.json
async def getInRoom():
    with open("data/inRoom.json","r") as f:
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

async def setRoomZero():
    with open("data/inRoom.json","w") as f:
        json.dump({"users": []},f)





