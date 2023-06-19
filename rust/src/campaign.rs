use std::collections::hash_map::Entry;

use fnv::{FnvHashMap, FnvHashSet};
use nutype::nutype;
use poise::serenity_prelude::{ChannelId, UserId};
use serde::{Deserialize, Serialize};

#[nutype(
    sanitize(trim)
    validate(min_len=5, max_len=30, with=str::is_ascii)
)]
#[derive(*, Serialize, Deserialize)]
struct CampaignName(String);

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
struct MemberId(UserId);

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
struct CampaignId(ChannelId);

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Campaign {
    name: CampaignName,
    members: FnvHashSet<MemberId>,
    leader: MemberId,
    id: CampaignId,
}

impl Campaign {
    pub fn new(name: CampaignName, leader: MemberId, id: CampaignId) -> Self {
        let mut members = fnv::FnvHashSet::default();
        members.insert(leader);
        Campaign {
            name,
            members,
            leader,
            id,
        }
    }

    pub fn add_member(&mut self, user: MemberId) {
        self.members.insert(user);
    }

    pub fn add_members(&mut self, users: impl Iterator<Item = MemberId>) {
        self.members.extend(users)
    }
}

#[derive(Debug, Clone, Default)]
struct CampaignState {
    campaign_table: FnvHashMap<CampaignId, Campaign>,
    user_table: FnvHashMap<MemberId, FnvHashSet<CampaignId>>,
    campaign_names_table: FnvHashMap<CampaignName, CampaignId>,
}

impl CampaignState {
    pub fn upsert_campaign(&mut self, campaign: Campaign) {
        let id = campaign.id;
        if let Some(camp) = self.campaign_table.insert(id, campaign) {
            self.remove_links(&camp);
        }
        self.sync_links(id)
    }

    fn remove_links(&mut self, campaign: &Campaign) {
        let id = campaign.id;
        for member in &campaign.members {
            self.user_table.entry(*member).and_modify(|camps| {
                camps.remove(&id);
            });
        }
        self.campaign_names_table.remove(&campaign.name);
    }

    fn sync_links(&mut self, id: CampaignId) {
        
    }

    fn add_links(&mut self, campaign: &Campaign) {}
}
