import asyncio
from functools import wraps
from typing import Callable, Optional

import click

from sidekwest.campaign import Campaign, CampaignState
from sidekwest.cli.state import CommandState, LocalStorageOptions


def async_command(f: Callable):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group
def sidekwest_cli():
    """Manage TTRPG discord data"""


@sidekwest_cli.group
@click.option(
    "-l",
    "--enable-local-storage/--no-enable-local-storage",
    help="enable local storage engine",
)
@click.option(
    "-d",
    "--storage-dir",
    help="Use this directory for local storage (no effect if local storage is not enabled)",
)
@click.pass_obj
def campaign(
    state: CommandState,
    enable_local_storage: Optional[bool],
    storage_dir: Optional[str],
):
    """Adjust campaign data"""
    if enable_local_storage:
        state.enable_local = True
        if storage_dir is not None:
            state.local_opts = LocalStorageOptions()
            state.local_opts.storage_dir = storage_dir


@campaign.command()
@click.argument("leader", required=True)
@click.argument("members", nargs=-1)
@click.pass_obj
@async_command
async def add(state: CommandState, leader: int, members: list[int]):
    """Add a campiagn to the existing data"""

    engines = state.to_engines()
    camp_state = await CampaignState.fetch(engines)
    new_campaign = Campaign(members, leader, camp_state.generate_new_id())
    camp_state.add_campaign(new_campaign)
    await camp_state.save(engines)


@sidekwest_cli.command
def bot():
    # pylint: disable=import-outside-toplevel
    from sidekwest.bot import main as bot_main

    bot_main()


def main():
    # pylint: disable=all
    sidekwest_cli(obj=CommandState())


if __name__ == "__main__":
    main()
