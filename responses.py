
def get_response(u_message:str) -> str:
    p_message = u_message.lower()

    match p_message:
        case 'reward':
            return "\nAll the gold will be divided by 3 and given to the top three people in the leaderboard. \nThe first person will receive 50%. \nThe second person will receive 30%. \nThe third person will receive 20%."
        case 'ping':
            return "pong :)"
        case "afin":
            return "ahlan labas"
        case "hello":
            return "\nHey there! do you want help \ntry [\help]"
        case "salam":
            return "3alikom o salam"
        case "atika":
            return "atikawa"
        case "i love u":
            return "f# u shut up"
        case "kanbghik":
            return "chokran"
        case "do you love me":
            return "no ofcours"
        case "sorry":
            return "don't worry, you are my friend"
        case "i am sad" | "i'm sad":
            return "don't be"
    return 'We don\'t know what exactly you need try `/help`'




