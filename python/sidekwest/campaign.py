from __future__ import annotations
from collections import defaultdict
import functools
from typing import DefaultDict, Iterable, NewType, Optional, Self, Union


from sidekwest.storage import Storable

CampaignId = NewType("CampaignId", int)
CampaignName = NewType("CampaignName", str)
UserId = NewType("UserId", int)

IntoCampaignId = Union[CampaignId, int]
IntoCampaignName = Union[CampaignName, str]
IntoUserId = Union[UserId, int]


class MultiMissingLeader(ValueError):
    def __init__(
        self, member: UserId, campaigns: list[CampaignId], *args: object
    ) -> None:
        mesg = f"Member {member} cannot be removed from {len(campaigns)} campaigns;"
        super().__init__(mesg, *args)
        self.member = member
        self.campaigns = campaigns


class MissingLeader(ValueError):
    pass


class CampaignExists(ValueError):
    pass


class CampaignDecodeError(ValueError):
    pass


class Campaign:
    def __init__(
        self,
        name: IntoCampaignName,
        leader: IntoUserId,
        campaign_id: IntoCampaignId,
    ) -> None:
        self.leader = UserId(leader)
        self.members = set([self.leader])
        self.campaign_id = CampaignId(campaign_id)
        self.name = CampaignName(name)

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
    def from_json(cls, camp_id: int, camp_data: dict) -> Self:
        leader = camp_data.get("leader")
        name = camp_data.get("name")
        members = camp_data.get("members")
        inner_id = camp_data.get("id")

        # Validate id field
        if not isinstance(inner_id, int) or inner_id != camp_id:
            raise CampaignDecodeError(
                f"Campaign id {camp_id}: id must exist and match the parent key"
            )

        # Validate name field
        if not isinstance(name, str) or not name:
            raise CampaignDecodeError(
                # pylint: disable=line-too-long
                f"Campaign id {camp_id}: 'name' must exist and be a non-empty string"
            )

        # Validate leader field
        if not isinstance(leader, int):
            raise CampaignDecodeError(
                f"Campaign id {camp_id}: 'leader' must exist and be an integer"
            )
        camp = cls(name, leader, camp_id)

        # Validate members field
        if not isinstance(members, list) or not all(
            map(lambda x: isinstance(x, int), members)
        ):
            raise CampaignDecodeError(
                f"Campaign id {camp_id}: members must be a list of integers if not empty"
            )
        camp.add_members(members)

        return camp

    def add_members(self, members: Iterable[IntoUserId]):
        self.members.union(members)

    def remove_member(self, member: UserId):
        if self.leader == member:
            raise MissingLeader(member, self.campaign_id)
        self.members.discard(member)

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
        self.users: DefaultDict[UserId, set[CampaignId]] = defaultdict(set)
        self.names: dict[CampaignName, CampaignId] = {}
        self._stale = False

    @property
    def stale(self):
        return self._stale

    def add_campaign(self, camp: Campaign):
        # Preserves table integrity
        camp_id = camp.campaign_id
        if camp_id in self.campaigns:
            if self.campaigns[camp_id] != camp:
                raise ValueError("Campaign id already exists")
        self.campaigns[camp_id] = camp
        if not self.stale:
            self._add_campaign_to_cache(camp)

    def _add_campaign_to_cache(self, camp: Campaign):
        for user in camp.members:
            self.users[user].add(camp.campaign_id)
        self.names[camp.name] = camp.campaign_id

    def rebuild_if_stale(self):
        if self.stale:
            self.rebuild_tables()

    def rebuild_tables(self):
        campaigns = list(self.campaigns.values())
        self.campaigns.clear()
        self.users.clear()
        self.names.clear()

        for camp in campaigns:
            self.add_campaign(camp)
        self._stale = False

    # this function will invalidate our caches
    def delete_member(self, member: IntoUserId):
        member = UserId(member)
        camps = self._get_member_campaigns(member)
        # getting the campaigns is helped by the caches,
        # so we wait to mark the caches stale until after the get operation
        self._stale = True
        leader_camps = []
        for camp in camps:
            try:
                camp.remove_member(member)
            except MissingLeader:
                leader_camps.append(camp.campaign_id)
        if leader_camps:
            raise MultiMissingLeader(member, leader_camps)

    def _get_member_campaigns(self, member: UserId) -> list[Campaign]:
        member = UserId(member)
        if self.stale:
            # Cache is invalid
            return self._get_uncached_member_campaigns(member)
        # Cache is valid
        return self._get_cached_member_campaigns(member)

    def _get_uncached_member_campaigns(self, member: UserId) -> list[Campaign]:
        return [camp for camp in self.campaigns.values() if member in camp.members]

    def _get_cached_member_campaigns(self, member: UserId) -> list[Campaign]:
        assert not self.stale
        camps = []
        for cid in self.users.get(member, []):
            camp: Optional[Campaign] = self.campaigns.get(cid)
            if not camp:
                # We found an integrity error
                self._stale = True
                return self._get_uncached_member_campaigns(member)
            camps.append(camp)
        return camps

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
            if not isinstance(camp_id, int):
                raise CampaignDecodeError(f"Invalid campaign id: {camp_id}")
            camp = Campaign.from_json(camp_id, camp_data)
            self.add_campaign(camp)

        return self

    def to_json(self) -> dict:
        camp_dicts = [d.to_json() for d in self.campaigns.values()]
        return functools.reduce(lambda a, b: a | b, camp_dicts, {})
