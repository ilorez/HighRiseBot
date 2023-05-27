import requests

async def get_random_short_joke():
    response = requests.get('https://official-joke-api.appspot.com/random_joke')
    
    if response.status_code == 200:
        joke_data = response.json()
        setup = joke_data['setup']
        punchline = joke_data['punchline']
        joke = f"{setup}\n{punchline}"
        
        if len(joke) <= 150:
            return joke
        else:
            return get_random_short_joke()  # Fetch another joke if it exceeds 150 characters
    else:
        return 'Failed to fetch a joke'
