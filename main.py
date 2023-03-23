# Created by restricted7331

import asyncio
import random
import time
import json

import discord
from discord.ext import commands
import yt_dlp

with open("config.json") as f:
    config = json.load(f)

bot = commands.Bot(command_prefix='?')

# Suppress noise about console usage from errors
yt_dlp.utils.bug_reports_message = lambda: ''

ytdl_opts = {
    'format': 'm4a/bestaudio/best',
    'outtmpl': '%(id)s',        
    'noplaylist' : True,
    
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }]
}

yt_dlp = yt_dlp.YoutubeDL(ytdl_opts)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: yt_dlp.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else yt_dlp.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, before_options="-loglevel fatal -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"), data=data)


@bot.event
async def on_ready():
    print('Bot is ready!')

queue = []
queue_iterator = -1

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            return await ctx.send('You need to be in a voice channel to use this command')

        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            vc = await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.command()
    async def leave(self, ctx):
        if (ctx.voice_client):
            await ctx.guild.voice_client.disconnect()
            await ctx.send('Left voice channel')
        else:
            await ctx.send("I'm not in a voice channel")

    @commands.command()
    async def add(self, ctx, *, url: str):
         queue.append(url)
         await ctx.send('Queued ``'+url+'``')

    @commands.command()
    async def rm(self, ctx, index: int):
         item = queue.pop(index)
         await ctx.send('Item ``'+item+'`` removed from queue')

    @commands.command()
    async def clear(self, ctx):
         queue.clear()
         await ctx.send('Queue cleared')

    @commands.command(aliases=['q'])
    async def queue(self, ctx):
        global queue

        if len(queue) < 1:
            await ctx.send('Queue is empty')
            return

        for count, value in enumerate(queue):
            await ctx.send('``'+str(count)+'`` ``'+value+'``')

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, url: str = None):
        global queue

        if ctx.author.voice is None or ctx.author.voice.channel is None:
            return await ctx.send('You need to be in a voice channel to use this command!')

        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            vc = await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

        async def start_player(ctx):
            if len(queue) == 0:
                return

            async with ctx.typing():
                player = await YTDLSource.from_url(queue.pop(0), loop=self.bot.loop, stream = True)
                ctx.voice_client.play(player, after = lambda e: asyncio.run_coroutine_threadsafe(start_player(ctx), self.bot.loop))
            await ctx.send('***Now playing:*** {}'.format(player.title))


        if ctx.voice_client.is_playing():
            queue.append(url)
            await ctx.send('Queued')
            return
        else:
            if(url == None and len(queue) == 0):
                await ctx.send('No url and nothing queued')
                return
            elif(url == None):
                await ctx.send('Playing from queue')
                await start_player(ctx)
            else:
                queue.append(url)
                await start_player(ctx)

    @commands.command(aliases=['s'])
    async def skip(self, ctx):
        if (ctx.voice_client):
            ctx.voice_client.stop()
        else:
            await ctx.send('No voice client')

    @commands.command(aliases=['stop'])
    async def pause(self, ctx):
        if (ctx.voice_client):
            ctx.guild.voice_client.pause()
        else:
            await ctx.send('No voice client')

    @commands.command()
    async def resume(self, ctx):
        if (ctx.voice_client):
            ctx.guild.voice_client.resume()
        else:
            await ctx.send('No voice client')


class Other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'**Pong!** Latency: {round(bot.latency * 1000)}ms')

    @commands.command(aliases=['hi'])
    async def coinflip(self, ctx):
        coin = ['heads', 'tails']
        await ctx.send(random.choice(coin))


bot.add_cog(Other(bot))
bot.add_cog(Music(bot))
bot.run(config['token'])