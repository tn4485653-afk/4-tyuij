import discord
from discord.ext import commands
import aiohttp
import asyncio
import os
from flask import Flask
from threading import Thread

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot running"

def run_web():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

API = "https://v-it.onrender.com/visit?region=vn&uid="

TOTAL_VISITS = 1500
BATCH_SIZE = 50

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def visits(ctx, uid: str):

    if isinstance(ctx.channel, discord.DMChannel):
        return

    msg = await ctx.send(
        f"⏳ Chuẩn bị spam 1500 visits tới UID `{uid}`\nChờ 15 giây..."
    )

    await asyncio.sleep(15)

    sent = 0

    async with aiohttp.ClientSession() as session:

        while sent < TOTAL_VISITS:

            tasks = []

            for _ in range(BATCH_SIZE):
                if sent >= TOTAL_VISITS:
                    break

                tasks.append(session.get(API + uid))
                sent += 1

            await asyncio.gather(*tasks, return_exceptions=True)

            progress = int((sent / TOTAL_VISITS) * 100)

            await msg.edit(
                content=f"🚀 Progress: {progress}% ({sent}/{TOTAL_VISITS})"
            )

            await asyncio.sleep(0.3)

    await msg.edit(content=f"✅ Hoàn tất spam 1500 visits cho UID `{uid}`")

@visits.error
async def visits_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Chờ {round(error.retry_after)}s rồi dùng lại.")

keep_alive()
bot.run(TOKEN)