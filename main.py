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
        self.states = {}

    async def response_logger(self, response, url):
        if response.status == 200 and self.states.get(url, False) == False:
            print(f"[{url}] is up and running!")
            await send_discord_notification(f"[{url}] is up and running!")
            self.states[url] = True
        elif response.status != 200 and self.states.get(url, False) == True:
            print(f"[{url}] is down! (Status code: {response.status})")
            await send_discord_notification(f"{[url]} is down! (Status code: {response.status})")
            self.states[url] = False
    
    async def post(self, url, headers, data):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=data) as response:
                    return await self.response_logger(response, url)
        except aiohttp.ClientError as e:
            await self.handle_exception(url, e)

    async def get(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await self.response_logger(response, url)
        except aiohttp.ClientError as e:
            await self.handle_exception(url, e)

    async def handle_exception(self, url, e):
        if self.states.get(url, False):
            await send_discord_notification(f"[{url}] is down! (Error: {e})")
        self.states[url] = False
        print(e)

    async def check_index(self):
        return await self.get('https://team1.csc429.io/')


    async def submit_data(self):
        url = "https://team1.csc429.io/submit.php"
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7,fr-FR;q=0.6,fr;q=0.5",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "Referer": "https://team1.csc429.io/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        data = {
            "firstName": "abc",
            "lastName": "def",
            "phoneNumber": "ghi",
            "item": "Owl"
        }
        return await self.post(url, headers, data)

        

    @tasks.loop(seconds=5) 
    async def monitor_website(self):
        await self.check_index()
        await self.submit_data()
        

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
