from discord.ext import commands, tasks
import aiohttp
import asyncio
import discord
import typing
import datetime
import humanize

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        humanize.i18n.activate("fr_FR")
        self.mute_reload.start()


    def is_me(self, m):
        return m.author == self.bot.user

    async def send_to_mongo(self, moderation_type, user, duration, date, reason, provider):
        """
        Send data to mongodb
        """
        await self.bot.db.add_log_mod(moderation_type, user, duration, date, reason, provider)
        print("Log registered")

    def embed_constructor(self=None):
        embed = discord.Embed(
            type="rich" ,
            color=discord.Colour.dark_red(),
        )
        embed.set_author(
            name='Ligue Des Trolleurs™' ,
            icon_url="https://cdn.discordapp.com/icons/464745857217200128/a_168e8604add366fc621c4ebec8cbabe5.gif?size=1024"
        )
        return embed

    @tasks.loop(minutes=1.0)
    async def mute_reload(self):
        print("checker")
        loop = asyncio.get_event_loop()
        now = datetime.datetime.now()
        res = await loop.run_in_executor(None, self.db.mod.find, {'type': 'mute', 'date': {'$gte': now-datetime.timedelta(days=1)}})
        for element in res:
            if element['date']+datetime.timedelta(minutes=element['duration'])<now:
                try:
                    member = discord.utils.get(self.bot.ldt_server.members, id=element['user'])
                    await member.remove_roles(self.bot.mute_role)
                except Exception as e:
                    pass






    @commands.command()
    async def ban(self, ctx, members: commands.Greedy[discord.Member], delete_days: typing.Optional[int] = 0, *,
                  reason: str = 'Pas de raisons'):
        """
        Commande de ban.
        Utilisation : `?ban @membre raison`
        Il est possible d ajouter le nombre de jour dont les messages vont etre supprimé (maximum 7) : `?ban @membre 6 raison`
        De plus on peut ban plusieur personnes d'un coup : `?ban @membre1 @membre2 @membre3 raison`
        """
        date = datetime.datetime.now()
        for member in members:
            await member.send(f"Vous avez été banni définitevement du serveur LDT par {ctx.author.name} le {date.day}/{date.month}/{date.year} pour la raison suivante :{reason}")
            embed = self.embed_constructor()
            embed.title = "Log Modération : Ban"
            embed.add_field(name="Nom :", value=member.name)
            embed.add_field(name="Raison :", value=reason)
            embed.add_field(name="Auteur :", value=ctx.author.name)
            embed.add_field(name="Date : ", value=humanize.naturaldate(date))
            await ctx.send(embed=embed)
            await member.ban(delete_message_days=delete_days, reason=reason)
            await self.send_to_mongo("ban", member.id, -1, date, reason, ctx.author.id)

    @commands.command()
    async def tempban(self, ctx, members: commands.Greedy[discord.Member], ban_days: int = 1,
                      delete_days: typing.Optional[int] = 0, *,
                      reason: str = 'Pas de raisons'):
        """
        Commande de ban temporaire.
        Utilisation : `?tempban @membre nombre_de_jour raison`
        Exemple : `?tempban @weeb 365 pour le fun`
        De plus on peut ban plusieur personnes d'un coup : `?tempban @membre1 @membre2 @membre3 nombre_de_jour raison`
        """
        date = datetime.datetime.now()
        for member in members:
            await member.send(f"Vous avez été banni temporairement du serveur LDT par {ctx.author.name} le {date.day}/{date.month}/{date.year} pour la raison suivante : {reason}. Votre bannissement est de {ban_days} jour(s)")
            embed = self.embed_constructor()
            embed.title = "Log Modération : TempBan"
            embed.add_field(name="Nom :", value=member.name)
            embed.add_field(name="Raison :", value=reason)
            embed.add_field(name="Durée (jours) :", value=ban_days)
            embed.add_field(name="Auteur :", value=ctx.author.name)
            embed.add_field(name="Date : ", value=humanize.naturaldate(date))
            await ctx.send(embed=embed)
            await member.ban(delete_message_days=delete_days, reason=reason)
            await self.send_to_mongo("bantemp", member.id, ban_days, date, reason, ctx.author.id)

    @commands.command()
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *,
                   reason: str = 'Pas de raisons'):
        """
        Commande de kick.
        Utilisation : `?kick @membre raison`
        De plus on peut kick plusieur personnes d'un coup : `?kick @membre1 @membre2 @membre3 raison`
        """
        date = datetime.datetime.now()
        for member in members:
            await member.send(f"Vous avez été kick du serveur LDT par {ctx.author.name} le {date.day}/{date.month}/{date.year} pour la raison suivante : {reason}")
            embed = self.embed_constructor()
            embed.title = "Log Modération : Kick"
            embed.add_field(name="Nom :", value=member.name)
            embed.add_field(name="Raison :", value=reason)
            embed.add_field(name="Auteur :", value=ctx.author.name)
            embed.add_field(name="Date : ", value=humanize.naturaldate(date))
            await ctx.send(embed=embed)
            await member.kick(reason=reason)
            await self.send_to_mongo("kick", member.id, 0, date, reason, ctx.author.id)

    @commands.command()
    async def mute(self, ctx, members: commands.Greedy[discord.Member], duration: int = 0, *,
                   reason: str = 'Pas de raisons'):
        """
        Commande de mute.
        Utilisation : `?mute @membre nb_minute raison`
        De plus on peut mute plusieur personnes d'un coup : `?mute @membre1 @membre2 @membre3 nb_minute raison`
        """
        date = datetime.datetime.now()
        for member in members:
            await member.send(f"Vous avez été mute du serveur LDT par {ctx.author.name} pendant {duration} minute(s) le {date.day}/{date.month}/{date.year} pour la raison suivante : {reason}")
            embed = self.embed_constructor()
            embed.title = "Log Modération : Mute"
            embed.add_field(name="Nom :", value=member.name)
            embed.add_field(name="Raison :", value=reason)
            embed.add_field(name="Durée (en minutes) :", value=duration)
            embed.add_field(name="Auteur :", value=ctx.author.name)
            embed.add_field(name="Date : ", value=humanize.naturaldate(date))
            await ctx.send(embed=embed)
            await member.add_roles(self.bot.mute_role)
            await self.send_to_mongo("mute", member.id, duration, date, reason, ctx.author.id)

    @commands.command()
    async def unmute(self, ctx, members: commands.Greedy[discord.Member]):
        """
        Commande de unmute.
        Utilisation : `?unmute @membre`
        De plus on peut mute plusieur personnes d'un coup : `?unmute @membre1 @membre2 @membre3`
        """
        date = datetime.datetime.now()
        for member in members:
            await member.send(
                f"Vous avez été unmute du serveur LDT par {ctx.author.name} ")
            embed = self.embed_constructor()
            embed.title = "Log Modération : Unmute"
            embed.add_field(name="Nom :", value=member.name)
            embed.add_field(name="Auteur :", value=ctx.author.name)
            embed.add_field(name="Date : ", value=humanize.naturaldate(date))
            await ctx.send(embed=embed)
            try:
                await member.remove_roles(self.bot.mute_role)
            except Exception as e:
                pass

    @commands.command()
    async def warn(self, ctx, members: commands.Greedy[discord.Member], *,
                   reason: str = 'Pas de raisons'):
        """
        Commande de warn.
        Utilisation : `?warn @membre raison`
        De plus on peut warn plusieur personnes d'un coup : `?warn @membre1 @membre2 @membre3 nb_minute raison`
        """
        date = datetime.datetime.now()
        for member in members:
            await member.send(f"Vous avez été warn du serveur LDT par {ctx.author.name} le {date.day}/{date.month}/{date.year} pour la raison suivante : {reason}")
            embed = self.embed_constructor()
            embed.title = "Log Modération : Warn"
            embed.add_field(name="Nom :", value=member.name)
            embed.add_field(name="Raison :", value=reason)
            embed.add_field(name="Auteur :", value=ctx.author.name)
            embed.add_field(name="Date : ", value=humanize.naturaldate(date))
            await ctx.send(embed=embed)
            # await member.ban(delete_message_days=delete_days, reason=reason)
            await self.send_to_mongo("warn", member.id, 0, date, reason, ctx.author.id)

    @commands.command()
    async def modremove(self, ctx, user: discord.User, index: int = -1):
        """
        Commande de log delete.
        Utilisation : `?logdelete @membre id`
        """
        modlist = await self.bot.db.get_all_mod_from(user.id)
        await self.bot.db.delete_mod(user.id, modlist[index]['_id'])
        await ctx.send("Entrée supprimé de la base de données")

    @commands.command()
    async def modinfo(self, ctx, user: discord.User):
        """
        nodocnow
        """
        modlist = await self.bot.db.get_all_mod_from(user.id)
        embed = self.embed_constructor()
        embed.title = f"Mod log for {user.name}"
        if len(modlist) > 0:
            textlist = []
            id = 0
            for mod in modlist:
                textlist.append(f"*({id})* **{mod['type'].upper()}** : {humanize.naturaldate(mod['date'])} par {discord.utils.get(ctx.message.guild.members, id=mod['author']).name} pour : `{mod['reason']}`")
                id += 1
            embed.add_field(name="Liste : ", value="\n".join(textlist))
        else:
            embed.add_field(name="Liste : ", value="Pas de sanction trouvée pour cet utilisateur")
        await ctx.send(embed=embed)
