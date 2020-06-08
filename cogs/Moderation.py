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


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        humanize.i18n.activate("fr_FR")

    @commands.Cog.listener()
    async def on_ready(self):
        self.mute_role = self.bot.ldt_server.get_role(permissions_config['mod']['mute_role'])
        self.blhsf_role = self.bot.ldt_server.get_role(permissions_config['bl']['blhsf_role'])
        self.bltds_role = self.bot.ldt_server.get_role(permissions_config['bl']['bltds_role'])
        self.bld_role = self.bot.ldt_server.get_role(permissions_config['bl']['bld_role'])

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
            type="rich",
            color=discord.Colour.dark_red(),
        )
        embed.set_author(
            name='Ligue Des Trolleurs™',
            icon_url="https://cdn.discordapp.com/icons/464745857217200128/a_168e8604add366fc621c4ebec8cbabe5.gif?size=1024"
        )
        return embed

    def duration_parser(self, text):
        try:
            if "s" in text:
                return int(text.replace("s", ""))
            elif "m" in text:
                return int(text.replace("m", "")) * 60
            elif "h" in text:
                return int(text.replace("h", "")) * 3600
            elif "d" in text:
                return int(text.replace("d", "")) * 86400
            elif "mo" in text:
                return int(text.replace("mo", "")) * 2592000
            elif "y" in text:
                return int(text.replace("y", "")) * 31536000
            else:
                return None
        except:
            return None

    async def mute_reload(self):
        loop = asyncio.get_event_loop()
        now = datetime.datetime.now()
        res = await loop.run_in_executor(None, self.bot.db.db.mod.find,
                                         {'type': 'mute', 'date': {'$gte': now - datetime.timedelta(days=7)}})
        for element in res:
            if element['date'] + datetime.timedelta(seconds=element['duration']) < now:
                try:
                    member = discord.utils.get(self.bot.ldt_server.members, id=element['user'])
                    await member.remove_roles(self.mute_role)
                except Exception as e:
                    pass

    async def ban_reload(self):
        loop = asyncio.get_event_loop()
        now = datetime.datetime.now()
        res = await loop.run_in_executor(None, self.bot.db.db.mod.find,
                                         {'type': 'tempban'})
        for element in res:
            if element['date'] + datetime.timedelta(seconds=element['duration']) < now:
                try:
                    user = await self.bot.fetch_user(element['user'])
                    await self.bot.ldt_server.unban(user)
                except Exception as e:
                    pass

    @commands.command()
    @commands.has_permissions(ban_members=True)
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
            await member.send(
                f"Vous avez été banni définitevement du serveur LDT par {ctx.author.name} le {date.day}/{date.month}/{date.year} pour la raison suivante :{reason}")
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
    @commands.has_permissions(ban_members=True)
    async def tempban(self, ctx, members: commands.Greedy[discord.Member], ban_days: str = "30d",
                      delete_days: typing.Optional[int] = 0, *,
                      reason: str = 'Pas de raisons'):
        """
        Commande de ban temporaire.
        Utilisation : `?tempban @membre nombre_de_jour raison`
        Exemple : `?tempban @weeb 365 pour le fun`
        De plus on peut ban plusieur personnes d'un coup : `?tempban @membre1 @membre2 @membre3 nombre_de_jour raison`
        """
        ban_days = int(self.duration_parser(ban_days))
        if ban_days is None:
            ctx.send("Format non valide")
        date = datetime.datetime.now()
        for member in members:
            await member.send(
                f"Vous avez été banni temporairement du serveur LDT par {ctx.author.name} le {date.day}/{date.month}/{date.year} pour la raison suivante : {reason}. Votre bannissement est de {humanize.naturaldelta(datetime.timedelta(seconds=ban_days))}")
            embed = self.embed_constructor()
            embed.title = "Log Modération : TempBan"
            embed.add_field(name="Nom :", value=member.name)
            embed.add_field(name="Raison :", value=reason)
            embed.add_field(name="Durée :", value=humanize.naturaldelta(datetime.timedelta(seconds=ban_days)))
            embed.add_field(name="Auteur :", value=ctx.author.name)
            embed.add_field(name="Date : ", value=humanize.naturaldate(date))
            await ctx.send(embed=embed)
            await member.ban(delete_message_days=delete_days, reason=reason)
            await self.send_to_mongo("tempban", member.id, ban_days, date, reason, ctx.author.id)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *,
                   reason: str = 'Pas de raisons'):
        """
        Commande de kick.
        Utilisation : `?kick @membre raison`
        De plus on peut kick plusieur personnes d'un coup : `?kick @membre1 @membre2 @membre3 raison`
        """
        date = datetime.datetime.now()
        for member in members:
            await member.send(
                f"Vous avez été kick du serveur LDT par {ctx.author.name} le {date.day}/{date.month}/{date.year} pour la raison suivante : {reason}")
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
    @commands.has_role(permissions_config['mod']['mute_perms'])
    async def mute(self, ctx, members: commands.Greedy[discord.Member], duration: str = "60m", *,
                   reason: str = 'Pas de raisons'):
        """
        Commande de mute.
        Utilisation : `?mute @membre duree raison`
        De plus on peut mute plusieur personnes d'un coup : `?mute @membre1 @membre2 @membre3 duree raison`
        """
        duration = int(self.duration_parser(duration))
        if duration is None:
            ctx.send("Format non valide")
        date = datetime.datetime.now()
        for member in members:
            await member.send(
                f"Vous avez été mute du serveur LDT par {ctx.author.name} pendant {duration} minute(s) le {date.day}/{date.month}/{date.year} pour la raison suivante : {reason}")
            embed = self.embed_constructor()
            embed.title = "Log Modération : Mute"
            embed.add_field(name="Nom :", value=member.name)
            embed.add_field(name="Raison :", value=reason)
            embed.add_field(name="Durée :", value=humanize.naturaldelta(datetime.timedelta(seconds=duration)))
            embed.add_field(name="Auteur :", value=ctx.author.name)
            embed.add_field(name="Date : ", value=humanize.naturaldate(date))
            await ctx.send(embed=embed)
            await member.add_roles(self.mute_role)
            await self.send_to_mongo("mute", member.id, duration, date, reason, ctx.author.id)

    @commands.command()
    @commands.has_role(permissions_config['mod']['mute_perms'])
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
    @commands.has_role(permissions_config['mod']['warn_perms'])
    async def warn(self, ctx, members: commands.Greedy[discord.Member], *,
                   reason: str = 'Pas de raisons'):
        """
        Commande de warn.
        Utilisation : `?warn @membre raison`
        De plus on peut warn plusieur personnes d'un coup : `?warn @membre1 @membre2 @membre3 nb_minute raison`
        """
        date = datetime.datetime.now()
        for member in members:
            await member.send(
                f"Vous avez été warn du serveur LDT par {ctx.author.name} le {date.day}/{date.month}/{date.year} pour la raison suivante : {reason}")
            embed = self.embed_constructor()
            embed.title = "Log Modération : Warn"
            embed.add_field(name="Nom :", value=member.name)
            embed.add_field(name="Raison :", value=reason)
            embed.add_field(name="Auteur :", value=ctx.author.name)
            embed.add_field(name="Date : ", value=humanize.naturaldate(date))
            await ctx.send(embed=embed)
            # await member.ban(delete_message_days=delete_days, reason=reason)
            await self.send_to_mongo("warn", member.id, 0, date, reason, ctx.author.id)

    @commands.command(aliases=['logdelete', 'moddelete', 'mremove', 'modrm'])
    @commands.has_role(permissions_config['mod']['management_perms'])
    async def modremove(self, ctx, user: discord.User, index: int = -1):
        """
        Commande de log delete.
        Utilisation : `?logdelete @membre id`
        """
        modlist = await self.bot.db.get_all_mod_from(user.id)
        await self.bot.db.delete_mod(user.id, modlist[index]['_id'])
        await ctx.send("Entrée supprimé de la base de données")

    @commands.command(aliases=['loginfo', 'minfo', 'mod', 'info'])
    @commands.has_role(permissions_config['mod']['management_perms'])
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
                textlist.append(
                    f"*({id})* **{mod['type'].upper()}** : {humanize.naturaldate(mod['date'])} par {discord.utils.get(ctx.message.guild.members, id=mod['author']).name} pour : `{mod['reason']}`")
                id += 1
            embed.add_field(name="Liste : ", value="\n".join(textlist))
        else:
            embed.add_field(name="Liste : ", value="Pas de sanction trouvée pour cet utilisateur")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role(permissions_config['bl']['blhsf_perms'])
    async def blhsf(self, ctx, member: discord.Member):
        """
        Blhsf
        Utilisation : `?blhsf @membre `
        """
        try:
            await member.add_roles(self.blhsf_role)
            await ctx.send(f"{member.name} a été ajouté a la blacklist `hsf`")
        except:
            pass

    @commands.command()
    @commands.has_role(permissions_config['bl']['bltds_perms'])
    async def bltds(self, ctx, member: discord.Member):
        """
        Bltds
        Utilisation : `?bltds @membre `
        """
        try:
            await member.add_roles(self.bltds_role)
            await ctx.send(f"{member.name} a été ajouté a la blacklist `tds`")
        except:
            pass

    @commands.command()
    @commands.has_role(permissions_config['bl']['bld_perms'])
    async def bld(self, ctx, member: discord.Member):
        """
        Bld
        Utilisation : `?bld @membre `
        """
        try:
            await member.add_roles(self.bld_role)
            await ctx.send(f"{member.name} a été ajouté a la blacklist `d`")
        except:
            pass
