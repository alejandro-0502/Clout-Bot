from discord.ext import commands
from bot import bot


async def get_extras(ctx, lst, has, not_has):
    temp = []
    if has == '-':
        has = ''
    for word in lst:
        if all(letter in word for letter in has) and not any(letter in word for letter in not_has):
            temp.append(word)
    print(temp)
    return temp


class WordleSolver(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.eng_words = set(line.strip() for line in open('words.txt'))

    async def find_matches(self, ctx, given):
        count = len(given) - 1
        temp = [i for i in self.eng_words if (len(i) == len(given))]
        while count >= 0:
            if given[count] == "-":
                count -= 1
            else:
                temp = [i for i in temp if (i[count] == given[count])]
                count -= 1
        return temp

    @commands.command(name='solve')
    async def solve(self, ctx, known, has='', not_has=''):
        await ctx.send(f'Solver Activate for {known}\ncontains:  {has}\ndoes not contain:  {not_has}')

        results = await get_extras(ctx, await self.find_matches(ctx, known), has, not_has)
        await ctx.send(', '.join(results))


def setup(client):
    client.add_cog(WordleSolver(client))
