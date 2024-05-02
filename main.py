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
        self.stateGood = True
        self.url = url

    async def response_logger(self, response, routeName):
        if response.status == 200:
            if not self.stateGood:
                print(f"[{routeName}] {self.url} is up and running!")
                self.stateGood = True
                await send_discord_notification(f"{self.url} is up and running!")
        elif self.stateGood:
            if self.stateGood:
                self.stateGood = False
                print(f"[{routeName}] {self.url} is down! (Status code: {response.status})")
                await send_discord_notification(f"{self.url} is down! (Status code: {response.status})")


    async def check_website(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    await self.response_logger(response, '/')
        except aiohttp.ClientError as e:
            if self.stateGood:
                self.stateGood = False
                await send_discord_notification(e)
                print(e)

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

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=data) as response:
                    await self.response_logger(response, '/submit.php')
        except aiohttp.ClientError as e:
            if self.stateGood:
                self.stateGood = False
                await send_discord_notification(e)
                print(e)

    @tasks.loop(minutes=1) 
    async def monitor_website(self):
        await self.check_website()
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
