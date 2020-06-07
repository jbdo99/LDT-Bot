import random
import asyncio
import datetime
import time
import discord
import humanize
import itertools
import re
import sys
import traceback
import wavelink
from discord.ext import commands
from typing import Union
from collections import deque
import os

RURL = re.compile('https?:\/\/(?:www\.)?.+')


class MusicController:

    def __init__(self , bot , guild_id):
        self.bot = bot
        self.guild_id = guild_id
        self.channel = None

        self.next = asyncio.Event()
        self.queue = deque()

        self.volume = 40
        self.now_playing = None

        self.bot.loop.create_task(self.controller_loop())

    async def controller_loop(self):
        await self.bot.wait_until_ready()

        player = self.bot.wavelink.get_player(self.guild_id)
        await player.set_volume(self.volume)

        while True:
            if self.now_playing:
                try:
                    await self.now_playing.delete()
                except Exception:
                    pass

            self.next.clear()

            song = None
            while not song:
                try:
                    song = self.queue.popleft()
                except IndexError:
                    await asyncio.sleep(0.5)

            await player.play(song)
            try:
                track = song
                embed = Music.embed_constructor()
                embed.add_field(name='Musique en cour :' , value=track.title)
                embed.add_field(name='Autheur : ' , value=track.author)
                embed.add_field(name='Duree : ' ,
                                value='{0}m{1}s'.format(int(track.duration) // 60000 , int(track.duration / 1000) % 60))
                if track.thumb:
                    embed.set_thumbnail(url=track.thumb)
                self.now_playing = await self.channel.send(embed=embed)
            except:
                pass

            await self.next.wait()


class Music(commands.Cog):

    def __init__(self , bot, lavalink_password):
        self.bot = bot
        self.lavalink_password = lavalink_password
        self.controllers = {}
        self.autoP = {}
        self.playtime = {}
        self.natural = {}
        self.lastskip = {}
        self.lasterror = {}

        if not hasattr(bot , 'wavelink'):
            self.bot.wavelink = wavelink.Client(bot=self.bot)

        self.bot.loop.create_task(self.start_nodes())

    async def start_nodes(self):
        await self.bot.wait_until_ready()
        try:
            node = await self.bot.wavelink.initiate_node(host='127.0.0.1' ,
                                                         port=2333 ,
                                                         rest_uri='http://127.0.0.1:2333' ,
                                                         password=self.lavalink_password,
                                                         identifier='LavaPlayer' ,
                                                         region='europe')
        except Exception as e:
            print('Erreur de connexion au serveur vocal :')
            print(e)

        node.set_hook(self.on_event_hook)

    async def on_event_hook(self , event):
        if isinstance(event , (wavelink.TrackEnd , wavelink.TrackException)):
            controller = self.get_controller(event.player)
            if hasattr(event , 'error'):
                print(event.error)
                try:
                    if self.lasterror.get(controller.guild_id , 0) >= time.time():
                        print('bye')
                        del self.controllers[int(controller.guild_id)]
                        await event.player.destroy()
                        return
                except Exception as e:
                    print(e)
                self.lasterror[controller.guild_id] = time.time() + 5
            controller.next.set()

    def embed_constructor(self=None):
        embed = discord.Embed(
            type="rich" ,
            color=discord.Colour.dark_red() ,
        )
        embed.set_author(
            name='Ligue Des Trolleurs™' ,
            icon_url="https://cdn.discordapp.com/icons/464745857217200128/a_168e8604add366fc621c4ebec8cbabe5.gif?size=1024"
        )
        return embed

    def get_controller(self , value: Union[commands.Context , wavelink.Player]):
        if isinstance(value , commands.Context):
            gid = value.guild.id
        else:
            gid = value.guild_id

        try:
            controller = self.controllers[gid]
        except KeyError:
            controller = MusicController(self.bot , gid)
            self.controllers[gid] = controller

        return controller

    async def cog_check(self , ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def cog_command_error(self , ctx , error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error , commands.NoPrivateMessage):
            try:
                return await ctx.send("D'ou tu me parle ?")  # quand on envoie une commande en MP
            except discord.HTTPException:
                pass

        print('Ignoring exception in command {}:'.format(ctx.command) , file=sys.stderr)
        traceback.print_exception(type(error) , error , error.__traceback__ , file=sys.stderr)

    async def sam_chan(self , ctx):
        try:
            player = self.bot.wavelink.get_player(ctx.guild.id)
            if ctx.message.author.voice:
                if ctx.message.author.voice.channel.id != int(player.channel_id):
                    # print(ctx.message.author.voice.channel.id,' : ',player.channel_id)
                    await ctx.send("T'es pas dans mon chan.")
                    return False
                return True
            await ctx.send("T'es pas dans le meme chan fdp")
            return False
        except Exception as e:
            print(e)
            return True

    @commands.command(name='join' , aliases=['connect'])
    async def connect_(self , ctx , * , channel: discord.VoiceChannel = None):
        """Connect to a voice channel."""
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                await ctx.send("Vas dans un chan d'abord")

        player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.send(f'Connexion a **`{channel.name}`**' , delete_after=10)
        await player.connect(channel.id)

        controller = self.get_controller(ctx)
        controller.channel = ctx.channel



    @commands.command(aliases=['sb' , 'sound'])
    async def soundbox(self , ctx , * , query: str = None):
        """Soundbox"""
        print('Hey')
        box = os.listdir('music/soundbox')
        list_box = [i.replace('.mp3','') for i in box if i.endswith('mp3')]
        
        if not query:
            embed = discord.Embed(color=discord.Colour.dark_red())
            cmd2 = '`' + ("`, `".join(sorted(list_box))) + '`'
            embed.add_field(name='SoundBox :' , value=cmd2 , inline=True)
            await ctx.send(embed=embed)
            return


        if not query.startswith('soundbox/'):
            query = 'soundbox/'+query

        if not query.endswith('.mp3') and not query.endswith('.opus'):
            query += '.mp3'

        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await ctx.invoke(self.connect_)
        tracks = await self.bot.wavelink.get_tracks(f'{query}')
        if not tracks:
            await ctx.send(f'Impossible de trouver : {query}')
            return
        controller = self.get_controller(ctx)
        controller.queue.appendleft(tracks[0])
        if player.is_playing:
            await player.stop()





    @commands.command(aliases=['p' , 'song'])
    async def play(self , ctx , * , query: str = None):
        """Search for and add a song to the Queue."""

        if not query:
            await ctx.send('Usage : ?play *nom/lien*')
            return

        if not RURL.match(query):
            query = f'ytsearch:{query}'

        tracks = await self.bot.wavelink.get_tracks(f'{query}')

        if not tracks and '&list=' in query:
            query = query.split('&')[0]
            tracks = await self.bot.wavelink.get_tracks(f'{query}')

        if not tracks:
            tracks = await self.bot.wavelink.get_tracks(f'{query}')
            if not tracks:
                return await ctx.send("dsl je n'ai rien trouver.")

        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await ctx.invoke(self.connect_)

        if type(tracks) == wavelink.player.TrackPlaylist:
            for i in tracks.tracks:
                controller = self.get_controller(ctx)
                controller.queue.append(i)
            await ctx.send('Playlist ajouter!')
            return

        track = tracks[0]

        controller = self.get_controller(ctx)
        controller.queue.append(track)

        embed = self.embed_constructor()
        embed.add_field(name='Musique ajouter :' , value=track.title)
        embed.add_field(name='Autheur : ' , value=track.author)
        embed.add_field(name='Duree : ' ,
                        value='{0}m{1}s'.format(int(track.duration) // 60000 , int(track.duration / 1000) % 60))
        if track.thumb:
            embed.set_thumbnail(url=track.thumb)

        await ctx.send(embed=embed)

    @commands.command()
    async def pause(self , ctx):
        """Pause the player."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('je ne suis pas entrain de jouer de la musique!' , delete_after=10)

        if not await self.sam_chan(ctx):
            return

        await ctx.send('En pause')
        await player.set_pause(True)

    @commands.command(aliases=['res'])
    async def resume(self , ctx):
        """Resume the player."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.paused:
            return await ctx.send('je suis pas pauser la' , delete_after=10)

        if not await self.sam_chan(ctx):
            return

        await ctx.send('Musique resumer!')
        await player.set_pause(False)

    @commands.command(aliases=['next'])
    async def skip(self , ctx):
        """Skip the currently playing song."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('Je joue pas de musique' , delete_after=15)

        if not await self.sam_chan(ctx):
            return

        await ctx.send('Musique passer!' , delete_after=15)
        await player.stop()

    @commands.command(aliases=['vol'])
    async def volume(self , ctx , * , vol: int):
        """Set the player volume."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        controller = self.get_controller(ctx)
        if not await self.sam_chan(ctx):
            return

        vol = max(min(vol , 10000) , 0)
        controller.volume = vol

        await ctx.send(f'Volume : `{vol}`')
        await player.set_volume(vol)

    @commands.command(aliases=['eq'])
    async def equalizer(self , ctx: commands.Context , * , equalizer: str = 'None'):
        """Change the player equalizer."""

        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.is_connected:
            return

        eqs = {'flat': wavelink.Equalizer.flat() ,
               'boost': wavelink.Equalizer.boost() ,
               'metal': wavelink.Equalizer.metal() ,
               'piano': wavelink.Equalizer.piano() ,
               }

        eq = eqs.get(equalizer.lower() , None)

        if not eq:
            joined = "\n-".join(eqs.keys())
            return await ctx.send(f'EQ invalide. liste des EQs:\n-{joined}')

        await player.set_eq(eq)
        await ctx.send(f'Equalizer definie sur {equalizer}')

    @commands.command(aliases=['bass'])
    async def BassBoost(self , ctx: commands.Context , * , boost: int = 1):
        """Bass Boost"""

        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.is_connected:
            await ctx.send('Pas en voc.')
            return

        await player.set_eq(wavelink.Equalizer(
            ([(0 , .0 * boost) , (1 , .125 * boost) , (2 , .125 * boost) , (3 , .1 * boost) , (4 , .1 * boost) ,
              (5 , .012 * boost) , (6 , 0.015 * boost) , (7 , .0) , (8 , .0) , (9 , .0) ,
              (10 , .0) , (11 , .0) , (12 , .125) , (13 , .15) , (14 , .05)])))

        await ctx.send(f'Bass Booster! x{str(boost)}')

    @commands.command(aliases=['np' , 'current' , 'nowplaying' , 'now_playing'])
    async def playing(self , ctx):
        """Retrieve the currently playing song."""
        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.current:
            return await ctx.send('je ne joue pas de musique pour le moment.')

        controller = self.get_controller(ctx)
        try:
            await controller.now_playing.delete()
        except:
            pass
        track = player.current
        embed = self.embed_constructor()
        embed.add_field(name='En train de jouer :' , value=track.title)
        embed.add_field(name='Autheur : ' , value=track.author)
        embed.add_field(name='Durée : ' ,
                        value='{0}m{1}s'.format(int(track.duration) // 60000 , int(track.duration / 1000) % 60))
        embed.add_field(name='url : ' , value=track.uri)
        if track.thumb:
            embed.set_thumbnail(url=track.thumb)
        controller.now_playing = await ctx.send(embed=embed)

    @commands.command(aliases=['q'])
    async def queue(self , ctx):
        """Retrieve information on the next songs from the queue."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        controller = self.get_controller(ctx)

        if not player.current or not len(controller.queue):
            return await ctx.send('ya rien dans la queue.' , delete_after=20)

        upcoming = list(itertools.islice(controller.queue , 0 , 15))

        fmt = '\n'.join(f'**`{str(song)}`**' for song in upcoming)
        embed = discord.Embed(title=f'{len(upcoming)} Prochaines musiques' , description=fmt ,
                              color=discord.Colour.dark_red())

        await ctx.send(embed=embed)


    @commands.command(aliases=['disconnect' , 'dc' , 'leave'])
    async def stop(self , ctx):
        """Stop and disconnect the player and controller."""
        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not await self.sam_chan(ctx):
            return

        try:
            del self.controllers[ctx.guild.id]
        except KeyError:
            try:
                await player.stop()
                await player.destroy()
            except:
                pass
            await player.disconnect()
            return await ctx.send('Ok, next')

        await player.stop()
        await player.disconnect()
        await player.destroy()
        await ctx.send('Déconnecté.' , delete_after=10)

    @commands.command(hidden=True)
    async def player_info(self , ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        node = player.node
        used = humanize.naturalsize(node.stats.memory_used)
        total = humanize.naturalsize(node.stats.memory_allocated)
        free = humanize.naturalsize(node.stats.memory_free)
        cpu = node.stats.cpu_cores

        fmt = f'**WaveLink:** `{wavelink.__version__}`\n\n' \
              f'Connected to `{len(self.bot.wavelink.nodes)}` nodes.\n' \
              f'Best available Node `{self.bot.wavelink.get_best_node().__repr__()}`\n' \
              f'`{len(self.bot.wavelink.players)}` players are distributed on nodes.\n' \
              f'`{node.stats.players}` players are distributed on server.\n' \
              f'`{node.stats.playing_players}` players are playing on server.\n\n' \
              f'Server Memory: `{used}/{total}` | `({free} free)`\n' \
              f'Server CPU: `{cpu}`\n\n' \
              f'Server Uptime: `{datetime.timedelta(milliseconds=node.stats.uptime)}`'
        await ctx.send(fmt)
