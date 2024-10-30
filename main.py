import asyncio
import random
import json
import discord
from discord.ext import commands
import yt_dlp

with open("config.json") as f:
    config = json.load(f)

bot = commands.Bot(command_prefix='?', intents=discord.Intents.all())

# Suppress noise about console usage from errors
yt_dlp.utils.bug_reports_message = lambda: ''

ytdl_opts = {
    'default_search': 'ytsearch',
    'format': 'm4a/bestaudio/best',
    'outtmpl': '%(id)s',
    'noplaylist': False,
    'quiet': True,

    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }]
}

yt_dlp = yt_dlp.YoutubeDL(ytdl_opts)


class Ytdlp(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def get_audio_from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = yt_dlp.extract_info(url, download=not stream)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else yt_dlp.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(
            filename,
            before_options="-loglevel fatal -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"),
            data=data
        )

    @classmethod
    async def search_from_url(cls, url):
        try:
            data = yt_dlp.extract_info(url, download=False)
            if 'entries' in data:
                video = data['entries'][0]
                title = video.get('title')
                video_url = video.get('webpage_url')
                print(f"title: {title} url: {video_url}")
                return video
            else:
                return data

        except Exception as e:
            print(f"Error during extraction: {e}")
            return None

@bot.event
async def on_ready():
    print('Bot is ready!')


queue = []
current_song = ""
queue_iterator = -1


class Music(commands.Cog):
    def __init__(self, _bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice and ctx.author.voice.channel:
            # voice_channel
            destination = ctx.author.voice.channel
            if ctx.voice_client:
                try:
                    await ctx.voice_client.move_to(destination)
                    # await ctx.send(f"Moved to {destination}")
                    # embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
                    # embed1.add_field(name='', value=f"Moved to {destination}")
                    # await ctx.send(embed=embed1)
                except Exception as e:
                    print(repr(e))
            else:
                try:
                    await destination.connect()
                    # await ctx.send(f"Connected to {destination}")
                    # embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
                    # embed1.add_field(name='', value=f"Connected to {destination}")
                    # await ctx.send(embed=embed1)
                except Exception as e:
                    print(repr(e))
        else:
            # return await ctx.send("You need to be in a voice channel to use this command!")
            embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
            embed1.add_field(name='', value="You need to be in a voice channel to use this command!")
            return await ctx.send(embed=embed1)

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            # await ctx.send('Left voice channel')
            embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
            embed1.add_field(name='', value="Left voice channel")
            await ctx.send(embed=embed1)
        else:
            # await ctx.send("I'm not in a voice channel")
            embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
            embed1.add_field(name='', value="I'm not in a voice channel")
            return await ctx.send(embed=embed1)

    @commands.command()
    async def search(self, ctx, *, url: str):  # test search
        async with ctx.typing():
            data = await Ytdlp.search_from_url(url)
            title = data.get('title')
            # video_url = data.get('webpage_url')
            await ctx.send(f"Title: {title} Url: {url}")

    @commands.command()
    async def add(self, ctx, *, url: str):
        async with ctx.typing():
            queue.append(url)
            # await ctx.send('Queued ``' + url + '``')
            embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
            embed1.add_field(name='', value='Queued ``' + url + '``')
            return await ctx.send(embed=embed1)

    @commands.command()
    async def rm(self, ctx, index: int):
        item = queue.pop(index)
        # await ctx.send('Item ``' + item + '`` removed from queue')
        embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
        embed1.add_field(name='', value='Item ``' + item + '`` removed from queue')
        await ctx.send(embed=embed1)

    @commands.command()
    async def clear(self, ctx):
        queue.clear()
        # await ctx.send('Queue cleared')
        embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
        embed1.add_field(name='', value="Queue cleared")
        await ctx.send(embed=embed1)

    @commands.command(aliases=['q'])
    async def queue(self, ctx):
        global queue

        current_song_data = await Ytdlp.search_from_url(current_song)  # this could be slow or smth
        current_title = current_song_data.get("title")
        current_author = current_song_data.get("uploader")

        if len(queue) < 1:
            if ctx.voice_client.is_playing():
                embed1 = discord.Embed(title="Queue", color=discord.Color.from_rgb(255, 94, 51))
                embed1.add_field(
                    name=current_title+" - "+current_author, value='``♫``  '+current_song, inline=False
                )
                return await ctx.send(embed=embed1)
            else:
                # await ctx.send('Queue is empty')
                embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
                embed1.add_field(name='', value="Queue is empty:")
                return await ctx.send(embed=embed1)

        embed2 = discord.Embed(title="Queue", color=discord.Color.from_rgb(255, 94, 51))
        embed2.add_field(
            name=current_title+" - "+current_author, value='``♫``  '+current_song, inline=False
        )
        for count, value in enumerate(queue):
            # await ctx.send('``' + str(count) + '`` ``' + value + '``')
            try:
                data = await Ytdlp.search_from_url(value)  # this could be slow or smth
                title = data.get("title")
                author = data.get("uploader")

                embed2.add_field(name=author+" - "+title, value='``'+str(count)+'`` '+value+' ', inline=False)
            except Exception as e:
                await ctx.send("An error occurred while fetching the video title.")
                print(f"Error: {e}")

        await ctx.send(embed=embed2)

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, url: str = None):
        # join
        if ctx.author.voice and ctx.author.voice.channel:
            # voice_channel
            destination = ctx.author.voice.channel
            if ctx.voice_client:
                try:
                    await ctx.voice_client.move_to(destination)
                    # await ctx.send(f"Moved to {destination}")
                    # embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
                    # embed1.add_field(name='', value=f"Moved to {destination}")
                    # await ctx.send(embed=embed1)
                except Exception as e:
                    print(repr(e))
            else:
                try:
                    await destination.connect()
                    # await ctx.send(f"Connected to {destination}")
                    # embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
                    # embed1.add_field(name='', value=f"Connected to {destination}")
                    # await ctx.send(embed=embed1)
                except Exception as e:
                    print(repr(e))
        else:
            # return await ctx.send("You need to be in a voice channel to use this command!")
            embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
            embed1.add_field(name='', value="You need to be in a voice channel to use this command!")
            return await ctx.send(embed=embed1)

        async def start_player(_ctx):
            global current_song

            async with ctx.typing():
                local_url = queue.pop(0)
                current_song = local_url
                try:
                    player = await Ytdlp.get_audio_from_url(local_url, loop=self.bot.loop, stream=True)
                except Exception as e2:
                    print(repr(e2))
                    embed2 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
                    embed2.add_field(name='', value="Error")
                    await ctx.send(embed=embed2)

                ctx.voice_client.play(
                    player,
                    after=lambda error: asyncio.run_coroutine_threadsafe(start_player(ctx), self.bot.loop)
                )

            # await ctx.send('***Now playing:*** {}'.format(player.title))
            embed2 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
            embed2.add_field(name='', value='***Now playing:*** {}'.format(player.title))
            await ctx.send(embed=embed2)

        # async def search_for_video(_ctx, _url: str):
        #     async with ctx.typing():
        #         data = await Ytdlp.search_from_url(url)
        #         title = data.get('title')
        #         # video_url = data.get('webpage_url')
        #         await ctx.send(f"Title: {title} Url: {url}")

        # async def search_url(_ctx, _url):  # test search
        #     # Create an instance of yt-dlp.YoutubeDL with the options
        #     with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        #         try:
        #             # Extract information from the search URL
        #             info = ydl.extract_info(search_url, download=False)
        #
        #             if 'entries' in info:
        #                 # Get the first result from the search
        #                 video = info['entries'][0]
        #                 title = video.get('title')
        #                 # url = video.get('webpage_url')
        #                 return await ctx.send(f"title {title} url: {_url}")
        #             else:
        #                 return None
        #         except Exception as e2:
        #             print(f"Error during search: {e2}")
        #             return None
        #
        #     # async with ctx.typing():
        #     #     search_results = yt_dlp.extract_info(f'ytsearch: {url}', download=False)['entries'][:3]
        #     #     if search_results:
        #     #         for i, result in enumerate(search_results):
        #     #             await ctx.send(f"Found: {result['title']}")
        #     #             # await ctx.send(f" URL: {result['url']}")
        #     #             return result['url']
        #     #     else:
        #     #         # await ctx.send("Can't find any search result for this query")
        #     #         embed2 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
        #     #         embed2.add_field(name='', value="Can't find any search result for this query")
        #     #         await ctx.send(embed=embed2)
        #     #         return False

        if ctx.voice_client.is_playing():
            queue.append(url)
            # await ctx.send('Queued')
            embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
            embed1.add_field(name='', value="Queued")
            return await ctx.send(embed=embed1)
        else:
            if url is None and len(queue) == 0:
                # await ctx.send('No url and nothing queued')
                embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
                embed1.add_field(name='', value="No url and nothing queued")
                return await ctx.send(embed=embed1)
            elif url is None:
                # await ctx.send('Playing from queue')
                embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
                embed1.add_field(name='', value="Playing from queue")
                await ctx.send(embed=embed1)
                await start_player(ctx)
            else:
                queue.append(url)
                await start_player(ctx)

    @commands.command(aliases=['s'])
    async def skip(self, ctx):
        if ctx.voice_client:
            ctx.voice_client.stop()
        else:
            # await ctx.send('No voice client')
            embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
            embed1.add_field(name='', value="No voice client")
            await ctx.send(embed=embed1)

    @commands.command(aliases=['stop'])
    async def pause(self, ctx):
        if ctx.voice_client:
            ctx.guild.voice_client.pause()
        else:
            # await ctx.send('No voice client')
            embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
            embed1.add_field(name='', value="No voice client")
            await ctx.send(embed=embed1)

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client:
            ctx.guild.voice_client.resume()
        else:
            # await ctx.send('No voice client')
            embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
            embed1.add_field(name='', value="No voice client")
            await ctx.send(embed=embed1)


class Other(commands.Cog):
    def __init__(self, _bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        # await ctx.send(f'**Pong!** Latency: {round(bot.latency * 1000)}ms')
        embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
        embed1.add_field(name='', value=f"**Pong!** Latency: {round(bot.latency * 1000)}ms")
        await ctx.send(embed=embed1)

    @commands.command(aliases=['hi'])
    async def coinflip(self, ctx):
        coin = ['heads', 'tails']
        # await ctx.send(random.choice(coin))
        embed1 = discord.Embed(color=discord.Color.from_rgb(255, 94, 51))
        embed1.add_field(name='', value=random.choice(coin))
        await ctx.send(embed=embed1)


async def main():
    await bot.add_cog(Music(bot))
    await bot.add_cog(Other(bot))

    async with bot:
        await bot.start(config["token"])

asyncio.run(main())
