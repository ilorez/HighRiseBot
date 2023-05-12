from highrise import *
from highrise.models import SessionMetadata, User
from highrise import __main__
import asyncio
from asyncio import run as arun 



#files
import responses
from player import *
import game
import gameloop
import users


class Bot(BaseBot):
    # start serever
    async def send_message(self,user_id,message):
        if await users.inRoom(user_id):
            await self.highrise.send_whisper(user_id,message)
        
    async def game_end(self):
        
        await gameloop.stock()
        # send message that game end to all players
        settings = game.getSettings()
        players = await getPlayers()
        today = gameloop.get_utc_date()
        winners = gameloop.allWinners()[today]
        settings = game.getSettings() 
        winners_id = [winners["firstP"]["id"],winners["secondP"]["id"],winners["thirdP"]["id"]]
        winners_name = [winners["firstP"]["name"],winners["secondP"]["name"],winners["thirdP"]["name"]]
        winners_gold = [winners["firstP"]["winGolds"],winners["secondP"]["winGolds"],winners["thirdP"]["winGolds"]]
        winners_place = ["first","second","third"]
        await asyncio.sleep(0.2)
        # send messageto playes that notice them game end
        for p in players:
            # if user is not in room or if user is one of winner don't do anything
            if (not await users.inRoom(p[0]))or(p[0] in winners_id):
                continue
            
            allP_m = [f"\nHey {p[1]}!\n\nLast week's game has ended and we have the winners:\n\n{winners['firstP']['name']} won {winners['firstP']['winGolds']} Golds!\n{winners['secondP']['name']} won {winners['secondP']['winGolds']} Golds!\n{winners['thirdP']['name']} won {winners['thirdP']['winGolds']} Golds!",f"\nThis week's game has just started and you can join us by tipping {settings['joinGold']} Golds. Hurry up to secure your spot among the top three!\n\nTip fast to get your chance at the top.\n\nBest of luck and have fun!"]

            if p[0] in winners_id:
                continue
            for pm in allP_m:
                await self.highrise.send_whisper(p[0],pm)
                await asyncio.sleep(0.2)
        #send message to winners
        for i in range(len(winners_id)):
            if not await users.inRoom(winners_id[i]):
                continue
            win_m = [f"Hey {winners_name[i]}!\n\nCongratulations on winning {winners_place[i]} place in last week's game! You've won {winners_gold[i]} golds, and the owner will be tipping you today.\n",f"\nIf you haven't received your golds after 5:00PM, please send a message to {list(settings['owner'])[0]} and let them know.\n\nKeep up the great work, and we hope to see you in the next game!\n\nBest regards."]
            for mp in win_m:
                await self.highrise.send_whisper(winners_id[i],mp)
                await asyncio.sleep(0.2)
        #send message to owenrs to tip to winners
        if await users.inRoom(settings['owner'][list(settings['owner'])[0]]):
            owener_me = "\nHi owner tip to winners use [/winners] to see usernames of winners"
            # await self.highrise.send_whisper(settings['owner'][list(settings['owner'])[0]],owener_me)
            Bot.send_message(self,settings['owner'][list(settings['owner'])[0]],owener_me)

        # elete data from players.json and tipPlayers.json
        await gameloop.setDataZero()
        # replace settings with nextSettings.json
        await gameloop.updateSettings()

    async def on_start(self, session_metadata: SessionMetadata):
        settings = game.getSettings() 
        await self.highrise.chat("GM players")
        pos = settings["botPosition"]
        await self.highrise.walk_to(Position(pos['x'],pos['z'],pos['y']))
        print('Server is started')
        # add users that in room to inRoom.json
        users_r = await self.highrise.get_room_users()
        for u in users_r.content:
            await users.joinedRoom(u[0])
        
        
    
    # new user join
    async def on_user_join(self, user: User) -> None:
        print(f"{user.username} has joined room !")
        await users.joinedRoom(user)
        if await users.isOldUser(user.id):
            await self.highrise.send_whisper(user.id, f"\nWelcome {user.username}")
        else:
            await users.addUser(user)
            await self.highrise.send_whisper(user.id, f"\nWelcome {user.username},\nWelcome to Gala World, are you ready to take the advanture!\nfor more info try \'/help\'")
        # game loop test when a member join
        # for understand what is game loop see README file
        # await Bot.game_end(self)
        if gameloop.isSunday():
            if not gameloop.isStocked():
                if len(list(playersData()))>=3:
                    await Bot.game_end(self)
    # on user leave
    async def on_user_leave(self, user: User) :
        print(f"{user.username} has leaved room !")
        await users.leavedRoom(user.id)

    # when user send a msg
    async def on_chat(self, user, message:str):

        # print what user say
        print(f"INFO:\n\tUsername: {user.username}\n\tId: {user.id}\n\tsay: {message} ")

        # when command not start with "/" the bot will not read it
        if not message[0] == '/':
            return
        message = message[1:]
        settings = game.getSettings() 
        # help or h command
        if message.startswith(('h','help')):
            resp = [f"\nInfo:\n 1. The game restart every sunday at 7:00 UTC \n 2. you need to collect wood and fishe and sell them for coins.\n 3. The player sorts in the leaderboard depense on coins.\n4. Tip {settings['joinGold']}G to join game\n5. [/reward] for reward info.","\nCommands:\n [/start]: for join game after tip\n [/inventory]: show inventory\n [/buy]: for buy new tools\n [/chop]: to collect woods\n [/fish]: to collect fishes\n [/sell]: to sell wood and fish for coins\n [/lb]: for show leaderboard"]
            for ligne in resp:
                await self.highrise.send_whisper(user.id,ligne)
                await asyncio.sleep(0.01)
            return
        # start command add player from tip list to game
        
        if message.startswith("start"):
            print(1)
            if (isPlayer(user.id)):
                await self.highrise.send_whisper(user.id,"you are already start!")
                return
            if isTip(user.username):
               addPlayer(user)
               await self.highrise.send_whisper(user.id,"Welcome, You can start playing now:)")
            else:
                await self.highrise.send_whisper(user.id,f"\nYou need to tip {settings['joinGold']}G first.\nif you have a probleme try Use: [/probleme]")
            return
        # leaderboard command
        if message.startswith("lb"):
            re_tap = await leaderBorad(user.id)
            re_m = ""
            if len(re_tap) == 3:
                re_m += f"\n[+]Your Position: {re_tap[2]}"
            re_m += f"\n[+]Players: {re_tap[0]}"
            re_m += f"\n[+]Best Players:"
            
            # re_tap[1].reverse()
            for p in re_tap[1]:
                re_m += f"\n  - {p[1]} [{p[2]}Gala]"
            await self.highrise.send_whisper(user.id,re_m)
            return
        #! admin
        # admin manging players 
        if message.startswith('admin'):
            if not user.username in list(settings["admins"].keys()):
                await self.highrise.send_whisper(user.id,"You are not an admin")
                return

            parts_m = message.split()
            if not len(parts_m) == 3:
                await self.highrise.send_whisper(user.id,"admin commands is:\n-/admin add [player usrname]\n-/admin remove [player usrname]")
            try:
                if (parts_m[1]=="add"):
                    addTipPlayer(parts_m[2])
                    done_m = f"{parts_m[2]} has added to tip list\nfor remove a player try /admin remove username"
                    await self.highrise.send_whisper(user.id,done_m)
                elif (parts_m[1]=="remove"):
                    r1 = delPlayer(parts_m[2])
                    r2 = delFromTip(parts_m[2])
                    if r1 == 1 or r2 == 1:
                        r_m = f"the {parts_m[2]} hase removed"
                    else:
                        r_m = f"there no player with username:{parts_m[2]}"
                    await self.highrise.send_whisper(user.id,r_m)
            except:await self.highrise.send_whisper(user.id,"no command found")
            return
        #! -----

        # /p problme command
        if message.startswith(("p","probleme")):
            m = "\nIf you have a probleme send to one of admins message and let him know.\n\nAdmins:\n"
            for admin in settings['admins']:
                m+= f"-{admin}"
                if await users.inRoom(settings['admins'][admin]):
                    m+= " [In Room]"
                
                m+="\n"
            await self.highrise.send_whisper(user.id,m)
            return


        # game play command
        if message.startswith(('inventory','buy','chop','sell','fish')):
            if (isPlayer(user.id)):
                pass
            else:
                await self.highrise.send_whisper(user.id,f"Hi {user.username} you didn't join game yet.\nTry /start")
                return
            
        

        #! player command 
       
        # inventroy command 
        ## chop wood command
        if message.startswith("chop"):
            re = await game.chop(user.id)
            if type(re) == int:
                re = f"You got {re} Woods\nYou can chop wood again after {settings['chopToolSleep']+1} min"
            
            await self.highrise.send_whisper(user.id,re)
            return
        ## fishing command
        if message.startswith("fish"):
            re = await game.fish(user.id)
            if type(re) == int:
                re = f"You got {re} fishs\nYou can fishing again after {settings['fishToolSleep']+1} min"
            
            await self.highrise.send_whisper(user.id,re)
            return

        if message.startswith("inventory"):
            data = playersData()
            player = data[user.id]
            ret_m = f"\nInventory\n[+]Coins = {player['resourses']['coins']} Gala\n"
            ret_m += f"[+]Tools:\n  -{player['tools']['axe']} Axe\n  -{player['tools']['rod']} fishing rod\n"
            ret_m += f"[+]Resources:\n  -Woods: {player['resourses']['wood']}\n  -Fishs: {player['resourses']['fish']}\n"
            ret_m += "Note: use [/sell] to sell resourses"
            await self.highrise.send_whisper(user.id,ret_m)
            return
        # buy command
        if message.startswith('buy'):
            parts_m = message.split()
            if len(parts_m) == 1:
                a_prixs = settings['toolsPrix']['axe'] 
                r_prixs = settings['toolsPrix']['rod'] 
                resp = f"\n\U0001FA93 Axe:\n\t1.Wood -{a_prixs['wood']}Gala\n\t2.Iron -{a_prixs['iron']}Gala\n\t3.Gold -{ a_prixs['gold']}Gala\n\t4.Diamond -{a_prixs['diamond']}Gala"
                resp += f"\n\U0001F3A3 Fishing rod:\n\t5.Wood -{r_prixs['wood']}Gala\n\t6.Iron -{r_prixs['iron']}Gala\n\t7.Gold -{ r_prixs['gold']}Gala\n\t8.Diamond -{r_prixs['diamond']}Gala"
                resp +="\n[+]Use /buy [number of item 1-8]"
                await self.highrise.send_whisper(user.id,resp)
            else:
                # when buy tool
                try:
                    num = int(parts_m[1])
                    if num <=8 and num >=1:
                        await self.highrise.send_whisper(user.id,await game.buyItem(user.id,num))
                    else:await self.highrise.send_whisper(user.id,'item not found! \nyou need to select number for item from list ,try:[/buy]')
                except:await self.highrise.send_whisper(user.id,'item not found! try:[/buy]')
                
            return
        if message.startswith("sell"):
            # await game.sellItems(user.id)
            await self.highrise.send_whisper(user.id,f"You get {await game.sellItems(user.id)}Gala")
            return
        #! ---------------
        
        
        # get respone from respons.py
        await self.highrise.send_whisper(user.id,responses.get_response(message))
        


    
    

    # run bot method
    async def run(self, room_id, token):
        await __main__.main(self, room_id, token)
