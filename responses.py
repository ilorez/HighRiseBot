
def get_response(u_message:str) -> str:
    p_message = u_message.lower()

    match p_message:
        case 'reward':
            return "\nAll the gold will be divided by 3 and given to the top three people in the leaderboard. \nThe first person will receive 50%. \nThe second person will receive 30%. \nThe third person will receive 20%."
        case 'ping':
            return "pong :)"
    
    return 'We don\'t know what exactly you need try `/help`'



