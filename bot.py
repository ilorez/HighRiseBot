from highrise import *
from highrise.models import SessionMetadata, User
from highrise import __main__
import asyncio
from asyncio import run as arun 
import random

#files
import responses
from player import *
import game
import gameloop
import users
import pendingM
import owner_admin
import joke
import messages_conrole

class Bot(BaseBot):
    # start serever
    async def send_message(self,user_id,message):
        if await users.inRoom(user_id):
            await self.highrise.send_whisper(user_id,message)
    

    async def game_end(self,user):
        await pendingM.setPendingM() # put allUsers.json in pending_messages
        today = gameloop.get_utc_date() # return today utc on format yyyy/mm/dd
        await gameloop.stock(today) #stock players data and winners data
        settings = game.getSettings() # get settings.json
        players = await getPlayers() # return table of players storted by GALA coins
        winners = gameloop.allWinners()[today] # return all winners of everyweek
        winners_id = [winners["firstP"]["id"],winners["secondP"]["id"],winners["thirdP"]["id"]]
        winners_name = [winners["firstP"]["name"],winners["secondP"]["name"],winners["thirdP"]["name"]]
        winners_gold = [winners["firstP"]["winGolds"],winners["secondP"]["winGolds"],winners["thirdP"]["winGolds"]]
        winners_place = await messages_conrole.getMessage(user,"game_end","04")
        

        await asyncio.sleep(1)
        # send messageto playes that notice them game end
        for p in players:
            # if user is not in room or if user is one of winner don't do anything
            if (not (await users.inRoom(p[0])))or(p[0] in winners_id):
                continue
            botMes = await messages_conrole.getMessage(user,"game_end","01")
            allP_m = [f"{botMes[0]}{p[1]}{botMes[1]}{winners['firstP']['name']}{botMes[2]}{winners['firstP']['winGolds']}{botMes[3]}{winners['secondP']['name']}{botMes[2]}{winners['secondP']['winGolds']}{botMes[3]}{winners['thirdP']['name']}{botMes[2]}{winners['thirdP']['winGolds']}{botMes[3]}",f"{botMes[4]}{settings['joinGold']}{botMes[5]}"]
            for pm in allP_m:
                await self.highrise.send_whisper(p[0],pm)
                await asyncio.sleep(1)
            await pendingM.removePen(p[0])
        #send message to winners
        for i in range(len(winners_id)):
            if not await users.inRoom(winners_id[i]):
                continue
            botMes = await messages_conrole.getMessage(user,"game_end","02")
            win_m = [f"{botMes[0]}{winners_name[i]}{botMes[1]}{winners_place[i]}{botMes[2]}{winners_gold[i]}{botMes[3]}",f"{botMes[4]}{list(settings['owner'])[0]}{botMes[5]}"]
            for mp in win_m:
                await self.highrise.send_whisper(winners_id[i],mp)
                await asyncio.sleep(1)
            await pendingM.removePen(winners_id[i])
        #send message to owenrs to tip to winners
        owner_id = settings['owner'][list(settings['owner'])[0]]
        if await users.inRoom(owner_id):
            owener_me = (await messages_conrole.getMessage(user,"game_end","03"))[0]
            # await self.highrise.send_whisper(owner_id,owener_me)
            await Bot.send_message(self,owner_id,owener_me)
            await pendingM.removePen(owner_id)

        # elete data from players.json and tipPlayers.json
        await gameloop.setDataZero()
        # update last week in next sethings
        await gameloop.setLastWeek(today)
        # replace settings with nextSettings.json
        await gameloop.updateSettings()

    async def on_start(self, session_metadata: SessionMetadata):
        await users.setRoomZero()
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
        settings = game.getSettings() 
        await users.joinedRoom(user)
        botMes = await messages_conrole.getMessage(user,"join_room","01")
        if await users.isOldUser(user.id):
            await Bot.send_message(self,user.id,f"{botMes[0]}{user.username}")
        else:
             await Bot.send_message(self,user.id, f"{botMes[0]}{user.username}{botMes[1]}")
        # game loop test when a member join
        # for understand what is game loop see README file
        # await Bot.game_end(self, user)
        if gameloop.isSunday():
            if not gameloop.isStocked():
                if len(list(playersData()))>=3:
                    # pass
                    await Bot.game_end(self,user)
        if await pendingM.isPending(user.id):
            poses = await messages_conrole.getMessage(user,"game_end","04")
            winners = await gameloop.getWinnersTap(settings["lastWeek"],poses)
            wins_id = [winners[i][0] for i in range(len(winners))]
            if (await owner_admin.isOwner(user)):
                owener_me = (await messages_conrole.getMessage(user,"game_end","03"))[0]
                await Bot.send_message(self,user.id,owener_me)
                
            elif user.id in wins_id:
                for w in winners:
                    if w[0] == user.id:
                        pos = w[2]
                        golds = w[3]
                botMes = await messages_conrole.getMessage(user,"game_end","02")
                win_m = [f"{botMes[0]}{user.username}{botMes[1]}{pos}{botMes[2]}{golds}{botMes[3]}",f"{botMes[4]}{list(settings['owner'])[0]}{botMes[5]}"]
                for mp in win_m:
                    await Bot.send_message(self,user.id,mp)
                    await asyncio.sleep(1)
                
            else:
                botMes = await messages_conrole.getMessage(user,"game_end","01")
                allP_m = [f"{botMes[0]}{user.username}{botMes[1]}{winners[0][1]}{botMes[2]}{winners[0][3]}{botMes[3]}{winners[1][1]}{botMes[2]}{winners[1][3]}{botMes[3]}{winners[2][1]}{botMes[2]}{winners[2][3]}{botMes[3]}",f"{botMes[4]}{settings['joinGold']}{botMes[5]}"]
                for pm in allP_m:
                    await Bot.send_message(self,user.id,pm)
                    await asyncio.sleep(1)
            await pendingM.removePen(user.id)
                
                
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
        # add users to allUsers.json if it not in it 
        if not (await users.isOldUser(user.id)):
            await users.addUser(user)
        message = message[1:]
        settings = game.getSettings() 
        # help or h command
        #! info methods
        if message.startswith('help'):
            botMes = await messages_conrole.getMessage(user,"help","01") 
            resp = [f"{botMes[0]}{settings['joinGold']}{botMes[1]}",botMes[2]]
            for ligne in resp:
                await Bot.send_message(self,user.id,ligne)
                await asyncio.sleep(0.01)
            return
        
        # /lang  command: for show or change language
        if message.startswith("lang"):
            langs_list = settings["languages"]
            parts_m = message.split()
            try:
                if len(parts_m) > 1:
                    new_lang = parts_m[1]
                    if new_lang in langs_list:
                        await users.changeUserLang(user.id,new_lang)
                        botMes = (await messages_conrole.getMessage(user,"lang","01"))[0]
                        m = f"{botMes}{new_lang}"
                    else:
                        botMes = (await messages_conrole.getMessage(user,"lang","02"))[0]
                        m = f"\n{new_lang}{botMes}"
                    
                else:
                    botMes = (await messages_conrole.getMessage(user,"lang","03"))[0]
                    m = botMes
                    for l in langs_list:
                        m+= f"\n  -{l}"
                    botMes = (await messages_conrole.getMessage(user,"lang","04"))[0]
                    m += botMes
                await Bot.send_message(self,user.id,m)
            except:print("there is a error in change lang")
            return
        # start command add player from tip list to game
        if message.startswith("admins"):
            m = (await messages_conrole.getMessage(user,"admins","01"))[0]
            for admin in settings['admins']:
                m+= f"- {admin}"
                if await users.inRoom(settings['admins'][admin]):
                    m+= (await messages_conrole.getMessage(user,"admins","02"))[0]
                m+="\n"
            await Bot.send_message(self,user.id,m)
            return
        if message.startswith("winners"):
            m = (await messages_conrole.getMessage(user,"winners","01"))[0]
            poses = await messages_conrole.getMessage(user,"game_end","04")
            for winner in (await gameloop.getWinnersTap(settings["lastWeek"],poses)):
                m+= f"- {winner[1]}"
                if await users.inRoom(winner[0]):
                    m+= (await messages_conrole.getMessage(user,"winners","02"))[0]
                m+="\n"
            await Bot.send_message(self,user.id,m)
            return
        # leaderboard command
        if message.startswith(("lb","leaderboard")):
            re_tap = await leaderBorad(user.id)
            re_m = ""
            if len(re_tap) == 3:
                botMes = (await messages_conrole.getMessage(user,'leaderboard','01'))[0]
                re_m += f"{botMes}{re_tap[2]}"
            botMes = (await messages_conrole.getMessage(user,'leaderboard','02'))[0]
            re_m += f"{botMes}{re_tap[0]}"
            botMes = (await messages_conrole.getMessage(user,'leaderboard','03'))[0]
            re_m += f"{botMes}"
            
            # re_tap[1].reverse()
            for p in re_tap[1]:
                re_m += f"\n  - {p[1]} [{p[2]}Gala]"
            await Bot.send_message(self,user.id,re_m)
            return
        # time betwenn now to week end
        if message.startswith("end"):
            time = await gameloop.toWeekEnd()
            botMes = (await messages_conrole.getMessage(user,'end','01'))[0]
            m = f"{botMes}{time}"
            await Bot.send_message(self,user.id,m)
            return
        # golds that tipsed
        if message.startswith("prize"):
            golds = await gameloop.tippsed()
            botMes = (await messages_conrole.getMessage(user,'prize','01'))[0]
            m = f"{botMes}{golds} Golds"
            await Bot.send_message(self,user.id,m)
            return

         #! ----------------------
        if message.startswith("start"):
            
            if (isPlayer(user.id)):
                botMes = (await messages_conrole.getMessage(user,'start','01'))[0]
                await Bot.send_message(self,user.id,botMes)
                return
            if isTip(user.username):
               addPlayer(user)
               botMes = (await messages_conrole.getMessage(user,'start','02'))[0]
               await Bot.send_message(self,user.id,botMes)
            else:
                botMes = await messages_conrole.getMessage(user,'start','03')
                await Bot.send_message(self,user.id,f"{botMes[0]}{settings['joinGold']}{botMes[1]}")
            return
        
        #! admin
        # admin manging players 
        if message.startswith('admin'):
            if not user.username in list(settings["admins"].keys()):
                botMes = (await messages_conrole.getMessage(user,'admin','01'))[0]
                await Bot.send_message(self,user.id,botMes)
                return

            parts_m = message.split()
            if not len(parts_m) == 3:
                botMes = (await messages_conrole.getMessage(user,'admin','02'))[0]
                await Bot.send_message(self,user.id,botMes)
                return
            try:
                if (parts_m[1]=="add"):
                    addTipPlayer(parts_m[2])
                    botMes = (await messages_conrole.getMessage(user,'admin','03'))[0]
                    done_m = f"\n{parts_m[2]}{botMes}"
                    await Bot.send_message(self,user.id,done_m)
                elif (parts_m[1]=="remove"):
                    r1 = delPlayer(parts_m[2])
                    r2 = delFromTip(parts_m[2])
                    if r1 == 1 or r2 == 1:
                        botMes = await messages_conrole.getMessage(user,'admin','04')
                        r_m = f"\n{botMes[0]}{parts_m[2]}{botMes[1]}"
                    else:
                        botMes = (await messages_conrole.getMessage(user,'admin','05'))[0]
                        r_m = f"\n{botMes}{parts_m[2]}"
                    await Bot.send_message(self,user.id,r_m)
            except:
                botMes = (await messages_conrole.getMessage(user,'admin','06'))[0]
                await Bot.send_message(self,user.id,botMes)
            return
        #! -----
        #! owner
        if message.startswith("owner"):
            if not await owner_admin.isOwner(user):
                botMes = (await messages_conrole.getMessage(user,'owner','01'))[0]
                await Bot.send_message(self,user.id,botMes)
                return
            parts_m = message.split()
            if not len(parts_m) == 3:
                botMes = (await messages_conrole.getMessage(user,'owner','02'))[0]
                await Bot.send_message(self,user.id,botMes)
                return
            try:
                
                if(parts_m[1]=="addAdmin"):
                    foundUser = await users.getIdOldUser(parts_m[2])
                    if not foundUser:
                        botMes = (await messages_conrole.getMessage(user,'owner','03'))[0]
                        await Bot.send_message(self,user.id,botMes)
                        return
                    await owner_admin.addAdmin(parts_m[2],foundUser)
                    botMes = (await messages_conrole.getMessage(user,'owner','04'))[0]
                    await Bot.send_message(self,user.id,f"\n{parts_m[2]}{botMes}")
                    return
                elif(parts_m[1]=="removeAdmin"):
                    if not parts_m[2] in list(settings["admins"].keys()):
                        botMes = (await messages_conrole.getMessage(user,'owner','05'))[0]
                        await Bot.send_message(self,user.id,f"\n{parts_m[2]}{botMes}")
                        return
                    await owner_admin.removeAdmin(parts_m[2])
                    botMes = (await messages_conrole.getMessage(user,'owner','06'))[0]
                    await Bot.send_message(self,user.id,f"\n{parts_m[2]}{botMes}")
                    return
            except:pass
            botMes = (await messages_conrole.getMessage(user,'owner','07'))[0]
            await Bot.send_message(self,user.id,botMes)
            return
            
        #! ------
        # /p problme command
        if message.startswith("probleme"):
            m = (await messages_conrole.getMessage(user,'probleme','01'))[0]
            for admin in settings['admins']:
                m+= f"-{admin}"
                if await users.inRoom(settings['admins'][admin]):
                    m+= (await messages_conrole.getMessage(user,'probleme','02'))[0]
                m+="\n"
            await Bot.send_message(self,user.id,m)
            return


        # game play command
        if message.startswith(('inventory','buy','chop','sell','fish')):
            if (isPlayer(user.id)):
                pass
            else:
                botMes = await messages_conrole.getMessage(user,'not_player','01')
                await Bot.send_message(self,user.id,f"{botMes[0]}{user.username}{botMes[1]}")
                return
            
        

        #! player command 
       
        # inventroy command 
        ## chop wood command
        if message.startswith("chop"):
            re = await game.chop(user.id)
            if type(re) == int:
                botMes = await messages_conrole.getMessage(user,"chop","01")
                re = f"{botMes[0]}{re}{botMes[1]}{settings['chopToolSleep']+1}{botMes[2]}"
                await Bot.send_message(self,user.id,re)
                return
            botMes = await messages_conrole.getMessage(user,"chop","02")
            await Bot.send_message(self,user.id,f"{botMes[0]}{re}{botMes[1]}")
            return
        ## fishing command
        if message.startswith("fish"):
            re = await game.fish(user.id)
            if type(re) == int:
                botMes = await messages_conrole.getMessage(user,"fish","01")
                re = f"{botMes[0]}{re}{botMes[1]}{settings['fishToolSleep']+1}{botMes[2]}"
                await Bot.send_message(self,user.id,re)
                return
            botMes = await messages_conrole.getMessage(user,"fish","02")
            await Bot.send_message(self,user.id,f"{botMes[0]}{re}{botMes[1]}")
            return

        if message.startswith("inventory"):
            data = playersData()
            player = data[user.id]
            botMes = await messages_conrole.getMessage(user,"inventory","01")
            ret_m = f"{botMes[0]}{player['resourses']['coins']}{botMes[1]}"
            ret_m += f"{botMes[2]}{player['tools']['axe']}{botMes[3]}{player['tools']['rod']}{botMes[4]}"
            ret_m += f"{botMes[5]}{player['resourses']['wood']}{botMes[6]}{player['resourses']['fish']}{botMes[7]}"
            ret_m += botMes[8]
            await Bot.send_message(self,user.id,ret_m)
            return
        # buy command
        if message.startswith('buy'):
            parts_m = message.split()
            if len(parts_m) == 1:
                a_prixs = settings['toolsPrix']['axe'] 
                r_prixs = settings['toolsPrix']['rod'] 
                a_toolRange = settings['toolRange']['axe']
                r_toolRange = settings['toolRange']['rod']
                botMes = await messages_conrole.getMessage(user,"buy","01")
                resp = [f"{botMes[0]}{a_prixs['wood']}{botMes[-2]}{a_toolRange['wood'][0]}{botMes[-1]}{a_toolRange['wood'][1]}{botMes[1]}{a_prixs['iron']}{botMes[-2]}{a_toolRange['iron'][0]}{botMes[-1]}{a_toolRange['iron'][1]}{botMes[2]}{ a_prixs['gold']}{botMes[-2]}{a_toolRange['gold'][0]}{botMes[-1]}{a_toolRange['gold'][1]}{botMes[3]}{a_prixs['diamond']}{botMes[-2]}{a_toolRange['diamond'][0]}{botMes[-1]}{a_toolRange['diamond'][1]}"]
                resp.append(f"{botMes[4]}{r_prixs['wood']}{botMes[-2]}{r_toolRange['wood'][0]}{botMes[-1]}{r_toolRange['wood'][1]}{botMes[5]}{r_prixs['iron']}{botMes[-2]}{r_toolRange['iron'][0]}{botMes[-1]}{r_toolRange['iron'][1]}{botMes[6]}{ r_prixs['gold']}{botMes[-2]}{r_toolRange['gold'][0]}{botMes[-1]}{r_toolRange['gold'][1]}{botMes[7]}{r_prixs['diamond']}{botMes[-2]}{r_toolRange['diamond'][0]}{botMes[-1]}{r_toolRange['diamond'][1]}{botMes[8]}")
                # resp +="\n[+]Use /buy [number of item 1-8]"
                for m in resp:
                    await Bot.send_message(self,user.id,m)
            else:
                # when buy tool
                try:
                    num = int(parts_m[1])
                    if num <=8 and num >=1:
                        b_result = await game.buyItem(user.id,num)
                        if b_result[0]:
                            botMes = await messages_conrole.getMessage(user,"buy","02")
                            m = f"{botMes[0]}{b_result[0]}{botMes[1]}{b_result[1]}{botMes[2]}{b_result[2]}{botMes[3]}{b_result[3]}{botMes[4]}"
                        else:
                            botMes = await messages_conrole.getMessage(user,"buy","03")
                            m = f"{botMes[0]}{b_result[1]}{botMes[1]}"
                        await Bot.send_message(self,user.id,m)
                        return
                except:pass
                botMes = (await messages_conrole.getMessage(user,"buy","04"))[0]
                await Bot.send_message(self,user.id,botMes)
                
            return
        if message.startswith("sell"):
            # await game.sellItems(user.id)
            botMes = await messages_conrole.getMessage(user,"sell","01")
            await Bot.send_message(self,user.id,f"{botMes[0]}{await game.sellItems(user.id)}{botMes[1]}")
            return
        #! ---------------
        #! other commands that for fun in room
        # emote command
        if message.startswith("emote"):
            emotes = ["emote-kiss","emote-no","emote-sad","emote-yes","emote-laughing","emote-hello","emote-wave","emote-shy","emote-tired","emoji-angry","idle-loop-sitfloor","emoji-thumbsup","emote-lust","emoji-cursing","emote-greedy","emoji-flex","emoji-gagging","emoji-celebrate","dance-macarena","dance-tiktok8","dance-blackpink","emote-model","dance-tiktok2","dance-pennywise","emote-bow","dance-russian","emote-curtsy","emote-snowball","emote-hot","emote-snowangel","emote-charging","dance-shoppingcart","emote-confused","idle-enthusiastic","emote-telekinesis","emote-float","emote-teleporting","emote-swordfight","emote-maniac","emote-energyball","emote-snake","idle_singing","emote-frog","emote-superpose","emote-cute","dance-tiktok9","dance-weird","dance-tiktok10","emote-pose7","emote-pose8","idle-dance-casual","emote-pose1","emote-pose3","emote-pose5","emote-cutey"]
            parts_m = message.split()
            try:
                if len(parts_m) >= 2:
                    if parts_m[1] in emotes:
                        await self.highrise.send_emote(parts_m[1], user.id)
                        return
                    botMes = (await messages_conrole.getMessage(user,"emote","01"))[0]
                    await Bot.send_message(self,user.id,botMes)
                    return
                botMes = (await messages_conrole.getMessage(user,"emote","02"))[0]
                await Bot.send_message(self,user.id,botMes)
                return
            except:print("error in emotes")
        # dance command
        if message.startswith("dance"):
            dances = ['dance-macarena', 'dance-tiktok8', 'dance-blackpink', 'dance-tiktok2', 'dance-pennywise', 'dance-russian', 'dance-shoppingcart', 'dance-tiktok9', 'dance-weird', 'dance-tiktok10', 'idle-dance-casual']
            dance = random.choice(dances)
            parts_m = message.split()
            try:
                if len(parts_m) >= 2:
                    if parts_m[1] == "all":
                        #only players ,admins and onwer can make all users dance
                        if isPlayer(user.id) or await owner_admin.isAdmin(user) or await owner_admin.isOwner(user):
                            roomUsers = (await self.highrise.get_room_users()).content
                            for roomUser, _ in roomUsers:
                                await self.highrise.send_emote(dance, roomUser.id)
                            return
                        else:
                            botMes = (await messages_conrole.getMessage(user,"dance","01"))[0]
                            await Bot.send_message(self,user.id,botMes)
                            return
                    if parts_m[1] in dances:
                        await self.highrise.send_emote(parts_m[1], user.id)
                        return
                await self.highrise.send_emote(dance, user.id)
                return
            except:print("error in user dance maybe because user not in room")
            return
        
        # joke command
        if message.startswith("joke"):
            try:
                ran_joke = await joke.get_random_short_joke()
                await Bot.send_message(self,user.id,f"\n{ran_joke}")
            except:
                botMes = (await messages_conrole.getMessage(user,"joke","01"))[0]
                await Bot.send_message(self,user.id,botMes)
                print("there is a error in api of joke")
            return
        
        #! ---------------
        
        
        # get respone from respons.py
        await Bot.send_message(self,user.id,responses.get_response(message))
        


    
    

    # run bot method
    async def run(self, room_id, token):
        await __main__.main(self, room_id, token)
