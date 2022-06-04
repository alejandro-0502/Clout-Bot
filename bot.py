# bot.py
import asyncio
import nacl
import os
import datetime
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
client = discord.Client()
bot = commands.Bot(intents=intents, command_prefix="!")


# Events

@client.event
async def on_message(message):
    # Ignore messages made by the bot
    if message.author == client.user:
        return


@bot.event
async def on_error(event, *args):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise


@bot.event
async def on_ready():
    print(bot.guilds)
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(f'{bot.user} is connected to the following guild: {guild}')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    if isinstance(error, commands.errors.CommandOnCooldown):
        cooldown = datetime.timedelta(seconds=int(error.retry_after))
        msg = f'Try again later, you are on cooldown. You have {cooldown} left on your timer.'
        await ctx.send(msg)


# Commands

@bot.command(name="load")
async def load(ctx, extension):
    try:
        bot.load_extension(f"cogs.{extension}")
        ctx.send(f'Loaded extension {extension}')
    except commands.ExtensionAlreadyLoaded:
        await ctx.channel.send("Extension already loaded")


@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()

@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()


@bot.command(name="unload")
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    ctx.send(f'{extension} has been unloaded')


@bot.command(name="dick")
async def have_dick(ctx):
    await ctx.message.delete()
    await ctx.send("Alejandro dont have dick :grey_exclamation: ")


@bot.command(name='create-channel')
@commands.has_role('admin')
async def create_channel(ctx, channel_name='real-python'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)


@bot.command(name="echo")
async def echo(ctx):
    def check(msg):
        return msg.channel == ctx.channel

    msg = await bot.wait_for("message", check=check)
    await ctx.send(msg.content)


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(TOKEN)
