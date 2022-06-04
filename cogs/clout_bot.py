import asyncio
import json
import os

from art import *
from discord.ext import commands
from discord.utils import get
import time


class CloutBot(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def add_clout(self, ctx, name):
        data = await self.load_data(ctx)
        author = ctx.message.author
        if name[2:-1] == str(author.id):
            await self.remove_clout(ctx, str(author))
            await ctx.send(f'{author} is a sussy baka, minus clout 4 you')
            await self.display_clout(ctx, str(author))
            return
        user_id = int(name[2:-1])
        user_name = str(self.client.get_user(user_id))
        user, index = await self.get_user(ctx, user_name)
        user['clout_count'] += 1
        data['users'][index] = user
        await self.save_data(ctx, data)
        await ctx.send(f'{name} has been awarded 1 clout!')
        await self.display_clout(ctx, user_name)

    async def declout_vote(self, ctx, name):
        user_name = str(self.client.get_user(int(name[2:-1])))
        author = ctx.message.author
        msg = await ctx.send(f'**{author}** has declared a declouting on **{user_name}**! Cast your vote!')
        await msg.add_reaction('💀')

        def check(reaction, user):
            return reaction.count >= 5 and str(reaction.emoji) == '💀'

        try:
            reaction, user = await self.client.wait_for("reaction_add", timeout=600.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send(f'Timeout! {author} is goofy 💀')
            await self.remove_clout(ctx, str(author))
        else:
            await ctx.send("Vote Passed!")
            await self.remove_clout(ctx, user_name)

    async def remove_clout(self, ctx, user_name):
        data = await self.load_data(ctx)
        user, index = await self.get_user(ctx, user_name)
        user['clout_count'] -= 1
        data['users'][index] = user
        await self.save_data(ctx, data)

    async def display_clout(self, ctx, user_name):
        data = await self.load_data(ctx)
        user = await self.get_user(ctx, user_name)
        count = data['users'][user[1]]['clout_count']
        await ctx.send(f"Here\'s {user_name}\'s clout count: {count}")

    async def load_data(self, ctx):
        with open("cogs/clout_collection.JSON", "r") as clout_file:
            data = json.load(clout_file)
            return data

    async def save_data(self, ctx, f):
        with open("cogs/clout_collection.JSON", "w") as clout_file:
            json.dump(f, clout_file, indent=4)

    async def get_user(self, ctx, name) -> tuple:
        data = await self.load_data(ctx)
        user = [(i, i2) for i, i2 in zip(data['users'], range(len(data['users']))) if i['userId'] == name]
        if not user:
            new_var = {'userId': name, 'clout_count': 0}
            data['users'].append(new_var)
            await self.save_data(ctx, data)
            user = [(name, -1)]
        return user[0]

    async def display_board(self, ctx):
        data = await self.load_data(ctx)
        sorted_dict = sorted(data['users'], key=lambda item: item['clout_count'], reverse=True)
        first_place = text2art(sorted_dict[0]['userId'][:-5], font="chunky")
        leaderboard = ''.join([f'%20s' % str(i['userId'])
                               + '%10s' % str(i['clout_count'])
                               + "\n" for i in sorted_dict])
        await ctx.send(f'```{first_place}\n{leaderboard}```')

    # Commands

    @commands.command(name='clout')
    @commands.cooldown(1, 72000, commands.BucketType.user)
    async def clout(self, ctx, name):
        await self.add_clout(ctx, name)

    @commands.command(name='declout')
    async def de_clout(self, ctx, name):
        await self.declout_vote(ctx, name)

    @commands.command(name='cloutboard')
    async def show_board(self, ctx):
        await self.display_board(ctx)

    @commands.command(name='showclout')
    async def show_clout(self, ctx):
        user = str(ctx.message.author)
        await self.display_clout(ctx, user)
    @commands.command(name='bart')
    async def bart(self, ctx):
        m = await ctx.send('bart')
        emote = get(ctx.message.guild.emojis, name='bartweird')
        await m.add_reaction(emote)


def setup(client):
    client.add_cog(CloutBot(client))
