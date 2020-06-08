from discord.ext import commands, tasks
import aiohttp
import asyncio
import discord
import typing
import datetime
import humanize
import json
import os.path

with open(os.path.dirname(__file__)[:-4] + 'server.json') as f:
    permissions_config = json.load(f)


class Divers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.confess_chan = discord.utils.get(self.bot.ldt_server.channels, id=permissions_config['divers']['confession_chan_post'])

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.bot.config['divers']['confession_chan_get']:
            now = datetime.datetime.now()
            await self.confess_chan.send(f"Confession envoyée le {now.day}/{now.month}/{now.year} : \n"+str(message.content))
            await message.delete()


    @commands.command()
    @commands.has_role(permissions_config['divers']['gode_perms'])
    async def gode(self, ctx):
        """
        Ajoute un gode. Disponible une fois par semaine
        """
        r = await self.bot.db.add_gode(ctx.author.id)
        if r:
            await ctx.send("Votre gode journalier a bien été ajouté")
        else:
            await ctx.send("Vous avez deja reçu votre gode journalier")

    @commands.command(aliases=['getgode', 'godeof'])
    @commands.has_role(permissions_config['divers']['gode_perms'])
    async def mygode(self, ctx, member: discord.Member = None):
        """
        Recupere les godes
        """
        if member is None:
            r = await self.bot.db.get_gode(ctx.author.id)
            if r is not None:
                await ctx.send(f"Vous avez {r['gode']} gode(s)")
            else:
                await ctx.send(f"Vous n'avez pas de gode")
        else:
            r = await self.bot.db.get_gode(member.id)
            if r is not None:
                await ctx.send(f"{member.name} a {r['gode']} gode(s)")
            else:
                await ctx.send(f"{member.name} n'a pas de gode")

    @commands.command()
    @commands.has_role(permissions_config['divers']['gode_perms'])
    async def topgode(self, ctx):
        """
        Top 5 gode
        """
        embed = discord.Embed(
            type="rich",
            color=discord.Colour.dark_red(),
        )
        embed.set_author(
            name='Ligue Des Trolleurs™',
            icon_url="https://cdn.discordapp.com/icons/464745857217200128/a_168e8604add366fc621c4ebec8cbabe5.gif?size=1024"
        )
        r = await self.bot.db.get_gode_top(5)
        i = 1
        for member in r:
            membre = discord.utils.get(self.bot.ldt_server.members, id=member['user'])
            embed.add_field(name=f"#{i}", value=f"{membre.name} : {member['gode']} godes")
            i += 1
        await ctx.send(embed=embed)



    @commands.command()
    async def social(self, ctx):
        """
        Affiche les réseaux sociaux de Belia
        """
        embed = discord.Embed(
            type="rich",
            color=discord.Colour.dark_red(),
        )
        embed.set_author(
            name='Ligue Des Trolleurs™',
            icon_url="https://cdn.discordapp.com/icons/464745857217200128/a_168e8604add366fc621c4ebec8cbabe5.gif?size=1024"
        )
        embed.title = "Réseaux sociaux de Belia"
        embed.description =""":movie_camera: Youtube : https://youtube.fr/c/beliaroth
:camera_with_flash: Instagram : https://www.instagram.com/beliaroth_/
:video_game: Twitch : https://twitch.tv/beliaroth
:dove:Twitter : https://twitter.com/Beliaroth_
:musical_keyboard: Soundcloud : https://soundcloud.com/beliaroth
:map: Patreon : https://www.patreon.com/liguedestrolleurs
        """
        await ctx.send(embed=embed)