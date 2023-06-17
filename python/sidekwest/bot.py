import asyncio
from datetime import datetime
import math
import os
import time
from typing import Optional

import discord
from discord import ApplicationContext, CategoryChannel
import dotenv

from sidekwest.cogs.campaign import CampaignCog
from sidekwest.storage import DEFAULT_ENGINES

PADDING_CHANNEL_ID = 1117479742162083940

bot = discord.Bot(intents=discord.Intents.default())
# verify = discord.SlashCommandGroup("verify", "verify slash command groups")

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


@bot.slash_command()
async def pad(ctx: ApplicationContext, num: int):
    await ctx.defer()
    category: CategoryChannel = ctx.guild.get_channel(PADDING_CHANNEL_ID)
    async with asyncio.TaskGroup() as tgrp:
        for i in range(num):
            tgrp.create_task(category.create_text_channel(f"pad-{i + 1}"))
    await ctx.delete()


@bot.slash_command()
async def unpad(ctx: ApplicationContext):
    await ctx.defer()
    category: CategoryChannel = ctx.guild.get_channel(PADDING_CHANNEL_ID)
    async with asyncio.TaskGroup() as tgrp:
        for channel in category.channels:
            tgrp.create_task(channel.delete(reason="unpadding"))
    await ctx.delete()


DEMO_CATEGORY_NAME = "test-category"


@bot.slash_command()
async def demo(ctx: ApplicationContext, force_fail: bool = False):
    await ctx.defer(ephemeral=True)
    await ctx.edit(content="creating...")

    category = await ctx.guild.create_category(DEMO_CATEGORY_NAME)
    forum = await category.create_forum_channel("forum")
    await forum.create_thread("thread", "initial-content")
    await category.create_voice_channel("Voice")
    await category.create_text_channel("text")
    await category.create_stage_channel("stage", topic="demo topic")

    if force_fail:
        await ctx.edit(content="intentionally failed")
        return

    sleep_time = 5
    coro = asyncio.sleep(sleep_time)
    awake_time = math.floor(time.time()) + sleep_time
    await ctx.edit(content=f"pausing, will begin deletion <t:{awake_time}:R>...")
    await coro

    await ctx.edit(content="deleting...")
    await cleanup_demo(ctx, category)
    await ctx.edit(content="done")


@bot.slash_command()
async def democlean(ctx: ApplicationContext):
    await ctx.defer(ephemeral=True)
    await cleanup_demo(ctx)
    await ctx.edit(content="finished")


async def cleanup_demo(
    ctx: ApplicationContext, category: Optional[CategoryChannel] = None
):
    if category is not None:
        cat_chans = [category]
    else:
        cat_chans = [
            c
            for c in ctx.guild.channels
            if c.type == discord.ChannelType.category and c.name == DEMO_CATEGORY_NAME
        ]

    chans: list[discord.abc.GuildChannel] = []
    for cat in cat_chans:
        for channel in cat.channels:
            chans.append(channel)

    async with asyncio.TaskGroup() as tgrp:
        for chan in chans:
            tgrp.create_task(chan.delete(reason="test channel creation and deletion"))
    async with asyncio.TaskGroup() as tgrp:
        for cat in cat_chans:
            tgrp.create_task(cat.delete(reason="test category creation and deletion"))


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
