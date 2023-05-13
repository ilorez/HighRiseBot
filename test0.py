def leavedRoom(id):
   
    onlines = {"users":[["1","11"],["2","22"],["3","33"]]}
    for u in onlines["users"]:
        if u[1] == id:
            onlines["users"].remove(u)
    print(onlines)


leavedRoom("22")
