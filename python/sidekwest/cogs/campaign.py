from typing import Self
import discord
from discord.ext import commands

from sidekwest.campaign import Campaign, CampaignState
from sidekwest.storage import StorageEngine


class CampaignCog(commands.Cog):
    campaign = discord.SlashCommandGroup("campaign", "Manage Campaigns and members")

    def __init__(
        self,
        bot: discord.Bot,
        storage_engines: list[StorageEngine],
        state: CampaignState,
    ) -> None:
        self.bot: discord.Bot = bot
        self.storage: list[StorageEngine] = storage_engines
        self._state: CampaignState = state

    @classmethod
    async def create(cls, bot: discord.Bot, storage_engines: list[StorageEngine]) -> Self:
        state = await CampaignState.fetch(storage_engines)
        return cls(bot, storage_engines, state)

    @campaign.command(name="add")
    async def add_campaign(
        self, ctx: discord.ApplicationContext, leader: discord.Member
    ):
        await ctx.defer(ephemeral=True)
        await ctx.edit(content="<a:loading:1118430810928844800> Creating campaign ...")
        cid = self._state.generate_new_id()
        camp = Campaign([], leader.id, cid)
        self._state.add_campaign(camp)
        await self._state.save(self.storage)
        await ctx.edit(content=f"Campaign added: {cid}")
