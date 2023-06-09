from __future__ import annotations
from collections import defaultdict
import functools
from typing import Iterable, NewType, Self, Union, assert_type, cast

import discord
from discord.ext import commands

from sidekwest.storage import Storable, StorageEngine, fetch_state

UserId = NewType("UserId", int)
IntoUserId = Union[UserId, int]
CampaignId = NewType("CampaignId", str)
IntoCampaignId = Union[CampaignId, str]


class CampaignExists(ValueError):
    pass


class CampaignDecodeError(ValueError):
    pass


class Campaign:
    def __init__(
        self,
        members: Iterable[IntoUserId],
        leader: IntoUserId,
        campaign_id: IntoCampaignId,
    ) -> None:
        self.members = set(map(UserId, members))
        self.leader = UserId(leader)
        self.members.add(self.leader)  # dummy check
        self.campaign_id = CampaignId(campaign_id)

    def __eq__(self, other) -> bool:
        if self is other:
            return True
        if not isinstance(other, Campaign):
            raise TypeError(
                f"Campaign.__eq__ expected Campaign type: found {type(other).name}"
            )
        self_tup = (self.members, self.leader, self.campaign_id)
        other_tup = (other.members, other.leader, self.campaign_id)
        return self_tup == other_tup

    @classmethod
    def from_json(cls, camp_id: str, camp_data: dict) -> Self:
        members = camp_data.get("members")
        leader = camp_data.get("leaders")

        # Validate members field
        if not isinstance(members, list) or not all(
            map(lambda x: isinstance(x, int), members)
        ):
            raise CampaignDecodeError(
                # pylint: disable=line-too-long
                f"Campaign id {camp_id}: 'members' must exist and be a non-empty list of integers"
            )
        # Type checker isn't smart enough to resolve from list[Any] to list[int]
        cast(list[int], members)

        # Validate leader field
        if not isinstance(leader, int):
            raise CampaignDecodeError(
                f"Campaign id {camp_id}: 'leader' must exist and be an integer"
            )
        assert_type(leader, int)
        return cls(members, leader, camp_id)

    def to_json(self) -> dict:
        return {
            self.campaign_id: {
                "members": list(self.members),
                "leader": self.leader,
            }
        }


class CampaignState(Storable):
    def __init__(self) -> None:
        self.campaigns: dict[CampaignId, Campaign] = {}
        self.users: dict[UserId, set[CampaignId]] = defaultdict(set)

    def add_campaign(self, camp: Campaign):
        camp_id = camp.campaign_id
        if camp_id in self.campaigns:
            if self.campaigns[camp_id] != camp:
                raise ValueError("Campaign id already exists")
        self.campaigns[camp_id] = camp
        for user in camp.members:
            self.users[user].add(camp_id)

    @classmethod
    def default(cls) -> Self:
        # new instance is default state
        return cls()

    @classmethod
    def storage_key(cls) -> str:
        return "campaigns"

    @classmethod
    def from_json(cls, data: dict) -> Self:
        self = cls()
        for camp_id, camp_data in data.items():
            if not isinstance(camp_id, str):
                raise CampaignDecodeError(f"Invalid campaign id: {camp_id}")
            camp = Campaign.from_json(camp_id, camp_data)
            self.add_campaign(camp)

        return self

    def to_json(self) -> dict:
        camp_dicts = [d.to_json() for d in self.campaigns.values()]
        return functools.reduce(lambda a, b: a | b, camp_dicts, {})


class CampaignCog(commands.Cog):
    def __init__(self, bot: discord.Bot, storage_engines: list[StorageEngine]) -> None:
        self.bot: discord.Bot = bot
        self.storage: list[StorageEngine] = storage_engines
        self._state: CampaignState = fetch_state(CampaignState, self.storage)
