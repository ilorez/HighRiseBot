import json
from users import getAllUsers
# get pending messages from pendig_messages.json
async def getPindings():
    with open("data/pending_messages.json","r") as f:
        ms = json.load(f)
    return ms

# set data into pending_messages
async def setDataP(data):
    with open("data/pending_messages.json","w") as f:
        json.dump(data,f)
 
# put allUsers.json in pending_messages
async def setPendingM():
    users = await getAllUsers()
    pendings = {}
    for u in users["users"]:
        pendings[u[0]] = u[1]
    await setDataP(pendings)

# remove from pending
async def removePen(id):
    pendings = await getPindings()
    if id in pendings:
        pendings.pop(id)
        await setDataP(pendings)

async def isPending(id):
    pendings = await getPindings()
    if id in pendings:
        return True
    return False