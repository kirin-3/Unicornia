"""
ModHelper Cog

This module contains the ModHelper class, which provides commands to assist with
moderation tasks in a Discord server.

Commands:
    Find: The find command uses fuzzy matching to search for users by their username
    or display name.
"""

import logging
import discord
from fuzzywuzzy import process
from redbot.core import commands
from redbot.core.bot import Red
from typing import List, Tuple

from . import __version__, __author__, const


class ModHelper(commands.Cog):
    def __init__(self, bot: commands.Bot = Red):
        self.bot: commands.Bot = bot

        self.logger: logging.Logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}"
        )
        self.logger.setLevel(const.LOGGER_LEVEL)

        self.logger.info("-" * 32)
        self.logger.info(f"{self.__class__.__name__} v({__version__}) initialized!")
        self.logger.info("-" * 32)

    @commands.command()
    async def find(
        self,
        ctx: commands.Context,
        name: str,
        score: int = 70,
        results: int = 5,
    ) -> None:
        """
        Find a user by username using fuzzy matching.

        Args:
            ctx (commands.Context): The command context.
            name (str): The user or display name to search for.
            score (int, optional): The minimum score threshold for matching. Defaults to 70.
            results (int, optional): The maximum number of results to display. Defaults to 5.
        """
        members: List[discord.Member] = ctx.guild.members
        member_names: List[Tuple[str, str]] = [
            (member.display_name, member.name) for member in members
        ]
        search_targets: List[str] = [
            f"{display_name} ({name})" for display_name, name in member_names
        ]

        found_users: List[Tuple[str, int]] = process.extract(
            name, search_targets, limit=results
        )
        await self.show_results(ctx, name, found_users, score, members)

    async def show_results(
        self,
        ctx: commands.Context,
        username: str,
        found_users: List[Tuple[str, int]],
        min_score: int,
        members: List[discord.Member],
    ) -> None:
        """
        Display the search results.

        Args:
            ctx (commands.Context): The command context.
            username (str): The username searched for.
            found_users (List[Tuple[str, int]]): List of found users with scores.
            min_score (int): The minimum score threshold for matching.
            members (List[discord.Member]): List of guild members.
        """
        for user, score in found_users:
            # Only include matches that meet the minimum score
            if score < min_score:
                continue

            display_name, name = user.split(" (")
            name = name.rstrip(")")
            member = discord.utils.get(members, name=name)
            if member:
                await ctx.send(f"### {member.display_name} ({member.name}) - {score}%")
                await ctx.send(f"{member.id}")

        if not found_users:
            await ctx.send(
                f"No matches found for '{username}' with the minimum score of {min_score}."
            )
