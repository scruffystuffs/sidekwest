import os

import discord
import dotenv

from sidekwest.cogs.campaign import CampaignCog
from sidekwest.storage import DEFAULT_ENGINES

dotenv.load_dotenv()
GUILD_ID = int(os.environ['GUILD_ID'])


bot = discord.Bot(debug_guilds=[GUILD_ID])
verify = discord.SlashCommandGroup("verify", "verify slash command groups")


@bot.listen()
async def on_ready(*_args):
    print("bot started")


@verify.command(name="help1", guild_ids=[GUILD_ID])
async def help1(ctx):
    await ctx.respond("help verified")


@verify.command(name="help2", guild_ids=[GUILD_ID])
async def help2(ctx):
    await ctx.respond("help verified 2: electric boogaloo")


@bot.slash_command(name="ping", guild_ids=[GUILD_ID])
async def ping(ctx):
    await ctx.respond("PONG", ephemeral=True)


def main():
    bot.add_application_command(verify)
    bot.add_cog(CampaignCog(bot), engines=DEFAULT_ENGINES)
    bot.run(os.environ["DISCORD_TOKEN"])


if __name__ == "__main__":
    main()
