from discord.ext import commands
from collections import Counter
import random as rand

from bot import bot


class Wordle(commands.Cog):

    def __init__(self, client):
        self.answer = ""
        self.eng_words = set(line.strip() for line in open('words.txt'))
        self.client = client
        self.GREEN = ":green_square:"
        self.YELLOW = ":yellow_square:"
        self.BLACK = ":white_large_square:"

    async def set_answer(self, ans) -> None:
        self.answer = ans

    async def compare(self, given, length):
        #
        word = list(given)
        temp = [""] * length
        c = Counter(list(self.answer))
        for i in range(0, length):
            if (word[i].lower() == self.answer[i]) and (c[word[i].lower()] > 0):
                temp[i] = self.GREEN
            elif (word[i].lower() in self.answer) and (c[word[i].lower()] > 0):
                temp[i] = self.YELLOW
            else:
                temp[i] = self.BLACK
            c[word[i]] -= 1
        return temp

    # Commands
    @commands.command()
    async def display_score(self, ctx, solution: str, attempted: list) -> None:
        # to do
        print(solution)

    @commands.command(name='word')
    async def play(self, ctx, word_length=5):
        if word_length > 1 and word_length < 20:
            await ctx.send(f'{word_length} Letter Game Start!')
            self.eng_words = [i for i in self.eng_words if len(i) == word_length]
            await self.set_answer(self.eng_words[rand.randint(0, len(self.eng_words))])
            self.eng_words = set(line.strip() for line in open('words.txt'))
            print(self.answer)

            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author

            count = 10
            while count > 0:
                msg = await bot.wait_for("message", check=check)
                if len(msg.content) != word_length:
                    await ctx.send(f'Must be {word_length} characters long!')
                    continue
                print(f'Input from user: {msg.content}')
                results = await self.compare(msg.content, len(msg.content))
                await ctx.send('Results:\n'+''.join(results)+'\n ' + '     '.join(list(msg.content)))

                if msg.content.lower() == self.answer:
                    await ctx.send('Winner Winner Chicken Dinner!')
                    break
                count -= 1

            await ctx.send('Game Over!\nAnswer: ' + self.answer)
        else:
            await ctx.send("Number of letters is too small or too big")


def setup(client):
    client.add_cog(Wordle(client))
