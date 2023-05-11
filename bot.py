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


class Bot(BaseBot):
    
    # start serever
    async def game_end():
        await gameloop.stock()
        # TODO send message that game end to all players
        players = await getPlayers()

        # TODO delete data from players.json and tipPlayers.json
        # TODO replace settings with nextWeekSettings.json

    async def on_start(self, session_metadata: SessionMetadata):
        settings = game.getSettings() 
        await self.highrise.chat("GM players")
        pos = settings["botPosition"]
        await self.highrise.walk_to(Position(pos['x'],pos['z'],pos['y']))
        print('Server is started')
        
    
    # new user join
    async def on_user_join(self, user: User) -> None:
        await self.highrise.send_whisper(user.id, f"Hi {user.username},\nWelcome to Gala World, are you ready to take the advanture!\nfor more info try \'/help\'")
        # game loop test when a member join
        # for understand what is game loop see README file
        if gameloop.isSunday():
            if not gameloop.isStocked():
                await Bot.game_end()

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
                await self.highrise.send_whisper(user.id,f"\nYou need to tip {settings['joinGold']}G first.\nif you have a probleme try Use:\n/p [write your probleme here]")
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
        if message.startswith("p"):
            message = message[1:]
            if len(message) > 100:
                await self.highrise.send_whisper(user.id,"You need to keep your message short then 100 caracter")
                return
            for admin in settings['admins']:
                    #  send problme to admins
                await self.highrise.send_whisper(settings['admins'][admin],f"Hi {admin}!\nusername:{user.username}\nid:{user.id}\nProblme:{message}")
                    #  send to admins other admins
                await self.highrise.send_whisper(settings['admins'][admin],f"this message has sended to {tuple(settings['admins'].keys())}")
                    #  send to user that the message has sended succsfull
                await self.highrise.send_whisper(user.id,"We get you problme, we will contact with you when fix the probleme")
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
