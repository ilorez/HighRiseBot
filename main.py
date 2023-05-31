from bot import Bot
from asyncio import run as arun 

# run bot from corrent file 
if __name__ == '__main__':
    path = "../token.txt"
    with open(path,"r") as f:
        token = f.readline().rstrip("\n")
        room_id = f.readline().rstrip("\n")
    arun(Bot().run(room_id, token))