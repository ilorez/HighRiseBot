import json

# import and convert data/allUsersHasJoined.json to dict
async def getAllUsers():
    with open("data/allUsersHasJoined.json","r") as f:
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
    with open("data/allUsersHasJoined.json","w") as f:
        json.dump(users,f)




