import discord
from discord.ext import commands, tasks
import configparser
import random,re
from cogs.Moderation import Moderation
from cogs.music import Music
from cogs.DbMongo import DbMongo
from cogs.Divers import Divers
import os
import json
import asyncio


config = configparser.ConfigParser()
config.read('config.ini')
TOKEN = config['MAIN']['token']
PROD = eval(config['MAIN']['prod'])
MDB_USER, MDB_PASSWD = config['MDB']['user'], config['MDB']['passwd']
LAVALINK_PASSwORD = config['LAVALINK']['password']


description = '''LDT BOT, an awesome bot'''
bot = commands.AutoShardedBot(command_prefix="?",
                              description=description,
                              help_command=None,
                              case_insensitive=True,
                              fetch_offline_members=False,
                              allowed_mentions=discord.AllowedMentions(everyone=False)
                              )

owner = [177375818635280384, 177394669766836224, 685540778474209327]

bot.add_cog(Moderation(bot))
bot.add_cog(Music(bot, LAVALINK_PASSwORD))
bot.add_cog(Divers(bot))

if PROD:
    bot.db = DbMongo(host="localhost", username=MDB_USER, password=MDB_PASSWD)
else:
    bot.db = DbMongo(host="sheepbot.net", username=MDB_USER, password=MDB_PASSWD)

with open('server.json') as f:
    permissions_config = json.load(f)
    bot.config = permissions_config

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    activity = discord.Activity(name="LDT Bot", type=discord.ActivityType.playing)
    await bot.change_presence(activity=activity)
    bot.ldt_server = discord.utils.get(bot.guilds, id=permissions_config['server_id'])

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("Vous n'avez pas la permission d'exécuter cette commande")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Vous n'avez pas la permission d'exécuter cette commande")
    else:
        print("une erreur c'est produite ici : ",error)

@bot.command()
async def ping(ctx):
    """Return Pong"""
    l = ""
    for i in ctx.bot.latencies:
        l += f"\nShard : {i[0]}, latency : {abs(i[1]*1000)}ms"

    await ctx.send(f"Pong, latencies : {l}")


@bot.command(hidden=True, name='eval')
async def _eval(ctx, ev: str):
    """A supprimer avant la prod"""
    if not ctx.message.author.id in owner:
        return
    try:
        a = eval(ctx.message.content.replace('?eval ',''))
        await ctx.send('Input : `' + ev + '`\nOutput : `' + str(a) + '`')
    except Exception as e:
        await ctx.send('Input : `' + ev + '`\nOutput (error) : `' + str(e) + '`')




@bot.command(hidden=True, aliases=['sht'])
async def shutdown(ctx):
    """shutdown"""
    if not ctx.message.author.id in owner:
        return
    await bot.close()

def generate_doc(bot):
    all_command = {}
    for obj in bot.commands:  # On trie les commandes par cog
        if obj.cog_name is not None and obj.hidden is False:
            if obj.cog_name in all_command:
                all_command[obj.cog_name].append(obj)
            else:
                all_command[obj.cog_name] = [obj]

    for cat, cont in all_command.items():  # On enleve les doublons
        all_command[cat] = list(set(cont))

    all_command = dict(sorted(all_command.items(), key=lambda t: t[0]))  # On trie par ordre alphabetique
    return all_command

COMMAND_LIST = generate_doc(bot)


@bot.command()
async def help(ctx, *args):
    """Give help"""
    com = {}
    for i in bot.commands:
        com[i.name] = i
    suppot = discord.Embed()
    suppot.colour = discord.Colour.dark_red()
    if len(args) < 1:
        suppot.set_author(
            name='Ligue Des Trolleurs™',
            icon_url="https://cdn.discordapp.com/icons/464745857217200128/a_168e8604add366fc621c4ebec8cbabe5.gif?size=1024"
        )
        for categorie, content in COMMAND_LIST.items():
            text = ""
            for commande in content:
                text += "`{0}`, ".format(commande.name)
            text = text[0:len(text) - 2]
            suppot.add_field(name="*{0}* : ".format(categorie), value=text, inline=False)
    else:
        search = args[0]
        if search in com.keys():
            suppot.set_author(
                name='Ligue Des Trolleurs™',
                icon_url="https://cdn.discordapp.com/icons/464745857217200128/a_168e8604add366fc621c4ebec8cbabe5.gif?size=1024"
            )
            helpo = com[search].help
            if helpo == None or helpo == "None":
                helpo = "Pas de description"
            suppot.add_field(name="{0}".format(search), value="{0}".format(helpo))
        else:
            suppot.set_author(
                name='Ligue Des Trolleurs™',
                icon_url="https://cdn.discordapp.com/icons/464745857217200128/a_168e8604add366fc621c4ebec8cbabe5.gif?size=1024"
            )
            suppot.add_field(name="Il n y a pas de commandes qui se nomme `{0}` !".format(search),
                             value="Liste de toutes les commandes : ?help")
    await ctx.send(embed=suppot)

#TASKS

async def mute_task():
    while not bot.is_closed():
        try:
            modcog = bot.get_cog("Moderation")
            await modcog.mute_reload()
            await asyncio.sleep(60)
        except Exception as e:
            print("Warning error in mute tasks")
            print(e)
            await asyncio.sleep(60)

async def ban_task():
    while not bot.is_closed():
        try:
            modcog = bot.get_cog("Moderation")
            await modcog.ban_reload()
            await asyncio.sleep(1800)
        except Exception as e:
            print("Warning error in ban tasks")
            await asyncio.sleep(1800)

try:
    bot.loop.create_task(mute_task())
    bot.loop.create_task(ban_task())

except Exception as e:
    print(e)
    print('Task error')

bot.run(TOKEN)
