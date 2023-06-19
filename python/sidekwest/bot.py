import asyncio
from datetime import datetime
import math
import os
import time

import discord
from discord import ApplicationContext 
import dotenv

from sidekwest.cogs.campaign import CampaignCog
from sidekwest.storage import DEFAULT_ENGINES

PADDING_CHANNEL_ID = 1117479742162083940

bot = discord.Bot(intents=discord.Intents.default())

start_time: int = 0


@bot.listen()
async def on_ready(*_args):
    # pylint: disable=global-statement
    global start_time
    start_time = math.floor(time.time())
    now = datetime.now()
    print(f"Bot started at: {now}")


@bot.slash_command()
async def uptime(ctx: ApplicationContext):
    await ctx.respond(f"Bot started <t:{start_time}:R>", ephemeral=True)


async def async_main():
    dotenv.load_dotenv()
    guild_id = int(os.environ["GUILD_ID"])
    bot.debug_guilds = [guild_id]
    # bot.add_application_command(verify)
    bot.add_cog(await CampaignCog.create(bot, DEFAULT_ENGINES))
    await bot.start(os.environ["DISCORD_TOKEN"])


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
