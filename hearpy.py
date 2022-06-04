from discord.ext import commands
from discord.utils import get as disc_get
from youtube_dl import YoutubeDL
from requests import get as req_get
from discord import FFmpegPCMAudio as ffmpeg
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import random
import bot
import discord
import os
from collections import Counter


def heardle_next(ctx):
    ctx.voice_client.stop()


class Hearpy(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.queue = []
        self.song_list = []
        self.curr_channel = None
        self.curr_title = ''
        self.curr_artist = ''
        self.scores = []

    def append_url(self, ctx, query, heardle=False):
        ydl_opts = {'format': 'bestaudio',
                    'cookiefile': 'youtube.com_cookies.txt',
                    'noplaylist': 'True'
                    }
        if heardle:
            query = str(query)+'lyrics'
        else:
            query = query + 'lyrics'
        with YoutubeDL(ydl_opts) as ydl:
            try:
                req_get(query)
            except:
                info = ydl.extract_info(f'ytsearch:{query}', download=False)['entries'][0]
            else:
                info = ydl.extract_info(query, download=False)
                print("files obtained")
            if 'entries' in info:
                for i in info['entries']:
                    self.queue.append((i['title'], i['formats'][0]['url']))
            else:
                self.queue.append((info['title'], info['formats'][0]['url']))
            if heardle:
                self.curr_title = self.song_list[0][1]
                self.curr_artist = self.song_list[0][0]
                del self.song_list[0]
                self.play_song(ctx, True)

    def play_next(self, ctx):
        if len(self.queue) >= 1:
            self.play_song(ctx)

    def play_song(self, ctx, heardle=False):
        ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                       'options': '-vn'}
        vc = disc_get(ctx.bot.voice_clients, guild=ctx.guild)
        if vc:
            source = ffmpeg(self.queue[0][1], **ffmpeg_opts)
            if heardle:
                vc.play(source, after=lambda x: self.append_url(ctx, self.song_list[0], True))
            else:
                vc.play(source, after=lambda x: self.play_next(ctx))
                self.client.loop.create_task(self.curr_channel.send(self.queue[0][0]))
            del self.queue[0]
        print("done")

    async def get_songs(self, link):
        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        playlist = sp.playlist_items(link,
                                     additional_types=('track',))
        tracks = playlist['items']
        while playlist['next']:
            playlist = sp.next(playlist)
            tracks.extend(playlist['items'])
        for i in tracks:
            artist = i['track']['artists'][0]['name']
            title = i['track']['name']
            self.song_list.append((artist, title))
        random.shuffle(self.song_list)

    def get_queue_titles(self):
        temp = []
        for i in self.queue:
            temp.append(i[1])
        return temp

    async def heardle_game(self, ctx):

        def check(msg):
            return msg.channel == ctx.channel

        vc = disc_get(ctx.bot.voice_clients, guild=ctx.guild)
        while vc:
            msg = await self.client.wait_for("message", check=check)
            #print(f'user input: {msg.content}')
            if msg.content.lower() == self.curr_title.lower() or msg.content.lower() == self.curr_artist.lower():
                await ctx.send(f'YAY! {msg.author} got it\n{self.curr_title} by {self.curr_artist}')
                self.scores.append(msg.author)
                heardle_next(ctx)
                await self.heardle_game(ctx)


    # Commands

    @commands.command(name='heardle')
    async def heardle(self, ctx, link='https://open.spotify.com/playlist/34oSswItNzAwHAlT8slJrX?si=98cfaea8e6314291'):
        self.song_list = []
        self.queue = []
        await self.get_songs(link)
        self.curr_channel = ctx.message.channel
        vc = disc_get(ctx.bot.voice_clients, guild=ctx.guild)
        if not vc:
            await bot.join(ctx)
        self.append_url(ctx, self.song_list[0], True)
        await self.heardle_game(ctx)


    @commands.command(name='play')
    async def play(self, ctx, *search):
        self.curr_channel = ctx.message.channel
        query = ''
        for word in search:
            query += word
        self.append_url(ctx, query)
        vc = disc_get(ctx.bot.voice_clients, guild=ctx.guild)
        if not vc:
            await bot.join(ctx)
        self.play_song(ctx)

    @commands.command(name='stop')
    async def stop(self, ctx):
        await bot.leave(ctx)
        self.queue.clear()
        await ctx.send('Queue has been cleared!')

    @commands.command(name='end')
    async def end_game(self, ctx):
        await bot.leave(ctx)
        self.queue.clear()
        c = Counter(self.scores)
        board = ''.join(str(i)+"\t"+str(x) for i, x in c.items())
        await ctx.send(f'Game has been Stopped!\nFinal Score: \n{board}')



    @commands.command(name='next')
    async def next(self, ctx):
        print("NEXT")
        await ctx.send('Skipping')
        await ctx.voice_client.stop()

    @commands.command(name='pause')
    async def pause(self, ctx):
        await ctx.send('Paused')
        await ctx.voice_client.pause()

    @commands.command(name='pqueue')
    async def print_queue(self, ctx):
        await ctx.send(self.get_queue_titles())

    @commands.command(name='title')
    async def send_title(self, ctx):
        await ctx.send(self.curr_title)

    @commands.command(name='artist')
    async def send_artist(self, ctx):
        await ctx.send(self.curr_artist)

    @commands.command(name='resume')
    async def resume(self, ctx):
        await ctx.send('Resumed')
        await ctx.voice_client.resume()

    # @commands.command(name='qnext')
    # async def next_first(self, ctx, link):
    #     self.append_url(link)
    #     await ctx.send(f'Added {self.queue[0][0]} to the front of the queue.')

    @commands.command(name='shuffle')
    async def shuffle(self, ctx):
        await ctx.send('Shuffling....')
        random.shuffle(self.queue)
        await ctx.send('Done!')


def setup(client):
    client.add_cog(Hearpy(client))
