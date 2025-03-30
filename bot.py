from datetime import datetime
from pytz import timezone
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import Config
from aiohttp import web
from route import web_server
import pyrogram.utils
import asyncio
import threading
from flask import Flask

# Set Pyrogram Min IDs
pyrogram.utils.MIN_CHAT_ID = -999999999999
pyrogram.utils.MIN_CHANNEL_ID = -1009999999999

class Bot(Client):

    def __init__(self):
        super().__init__(
            name="renamer",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=15,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username  
        self.uptime = Config.BOT_UPTIME     

        if Config.WEBHOOK:
            try:
                app = web.AppRunner(await web_server())
                await app.setup()       
                await web.TCPSite(app, "0.0.0.0", 8000).start()  # Port 8000 for health checks
            except Exception as e:
                print(f"Webhook failed to start: {e}")

        print(f"{me.first_name} Is Started.....✨️")

        # Notify Admins
        for admin_id in Config.ADMIN:
            try:
                await self.send_message(admin_id, f"**{me.first_name} Is Started.....✨️**")                                
            except:
                pass

        # Log Bot Start
        if Config.LOG_CHANNEL:
            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                date = curr.strftime('%d %B, %Y')
                time = curr.strftime('%I:%M:%S %p')
                await self.send_message(
                    Config.LOG_CHANNEL,
                    f"**{me.mention} Is Restarted !!**\n\n📅 Date : `{date}`\n⏰ Time : `{time}`\n🌐 Timezone : `Asia/Kolkata`\n\n🉐 Version : `v{__version__} (Layer {layer})`"
                )                                
            except:
                print("Please Make Sure This Bot Is Admin In Your Log Channel")

# Keep Bot Alive
async def main():
    bot = Bot()
    await bot.start()
    await asyncio.Event().wait()  # Keeps the bot running

# Simple Flask Web Server (for hosting platforms)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_web():
    app.run(host="0.0.0.0", port=8000)

threading.Thread(target=run_web, daemon=True).start()  # Keep-alive thread

asyncio.run(main())  # ✅ Runs the bot asynchronously
