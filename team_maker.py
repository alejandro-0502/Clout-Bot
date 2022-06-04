import random

import discord
from discord.ext import commands
from collections import Counter
import random as rand

from discord.utils import get

from bot import bot


class TeamMaker(commands.Cog):

    def __init__(self, client):
        self.client = client


    async def make_team(self, ctx, usr_lst):
        rand.shuffle(usr_lst)
        team_A = usr_lst[:len(usr_lst) // 2]
        team_B = usr_lst[len(usr_lst) // 2:]
        await ctx.send(f'Team A: {[i.name for i in team_A]}')
        await ctx.send(f'Team B: {[i.name for i in team_B]}')
        return team_A, team_B

    # Commands
    @commands.command(name='team')
    async def team(self, ctx):
        m = await ctx.send("Pre-Game teams:")
        emote = get(ctx.message.guild.emojis, name='posted')
        await m.add_reaction(emote)
        author = ctx.message.author
        channel = ctx.message.author.voice.channel
        usr_lst = channel.members
        team_a, team_b = await self.make_team(ctx, usr_lst)

        channel_a = await ctx.guild.create_voice_channel('Team A')
        channel_b = await ctx.guild.create_voice_channel('Team B')
        msg = await ctx.send("React to begin!")
        await msg.add_reaction('🟢')
        # for member in team_a:
        #     await member.move_to(channel_a)
        # for member in team_b:
        #     await member.move_to(channel_b)

        await channel_a.delete()
        await channel_b.delete()


def setup(client):
    client.add_cog(TeamMaker(client))

