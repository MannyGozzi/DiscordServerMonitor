import aiohttp
import asyncio
import discord
from discord.ext import tasks  # Import the tasks extension
from dotenv import load_dotenv
import os

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
SERVER_URL= os.getenv("SERVER_URL")
intents = discord.Intents.default()
intents.typing = False # don't need to know when someone is typing
intents.presences = False # don't need to know when someone's status changes
client = discord.Client(intents=intents)

class WebMonitor:
    def __init__(self, url):
        self.stateGood = False
        self.url = url

    async def check_website(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    if response.status == 200:
                        if not self.stateGood:
                            print(f"{self.url} is up and running!")
                            self.stateGood = True
                            await send_discord_notification(f"{self.url} is up and running!")
                    elif self.stateGood:
                        self.stateGood = False
                        print(f"{self.url} is down! (Status code: {response.status})")
                        await send_discord_notification(f"{self.url} is down! (Status code: {response.status})")
        except aiohttp.ClientError as e:
            print(f"Error occurred: {e}")
            await send_discord_notification(f"Error occurred: {e}")

    @tasks.loop(minutes=1) 
    async def monitor_website(self):
        await self.check_website()

webMonitor = WebMonitor(SERVER_URL)

@client.event
async def on_ready():
    print(f"{client.user.name} is ready!")
    webMonitor.monitor_website.start()

async def send_discord_notification(message):
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        await channel.send(message)
    else:
        print(f"Invalid channel ID: {DISCORD_CHANNEL_ID}")

async def main():
    await client.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
