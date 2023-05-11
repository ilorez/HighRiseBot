import discord
import schedule
import time
from datetime import datetime
import pytz

# Set the timezone to UTC
tz = pytz.timezone('UTC')

# Create a new Discord client
client = discord.Client()

# Define a function to be scheduled
def my_function():
    # Code for your function goes here
    print("Function started at", datetime.now(tz))

# Schedule the function to run every Sunday at 7:00 AM UTC
schedule.every().week.at("07:00").on_day_of_week('sun').do(my_function)

# Define an event to run when the bot is ready
@client.event
async def on_ready():
    print('Logged in as', client.user)

# Run the bot with your token
client.run('MTA5MDkxNDU4MzgwNTQyNzc1Mw.GGzj-W.H1oTU4uOfXXtv6OLiUi-MmfSy1wXbfgn-pbJbM')

# Run the scheduled tasks continuously
while True:
    schedule.run_pending()
    time.sleep(60) # Wait for 60 seconds before checking again
