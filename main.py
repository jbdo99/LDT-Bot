import discord
from discord.ext import commands, tasks
import configparser
import random,re
from cogs.Moderation import Moderation
from cogs.music import Music


config = configparser.ConfigParser()
config.read('config.ini')
TOKEN = config['MAIN']['token']
PROD = eval(config['MAIN']['prod'])
MDB_USER, MDB_PASSWD = config['MDB']['user'], config['MDB']['passwd']


description = '''LDT BOT, an awesome bot'''
bot = commands.AutoShardedBot(command_prefix="?",
                              description=description,
                              help_command=None,
                              case_insensitive=True,
                              fetch_offline_members=False,
                              allowed_mentions=discord.AllowedMentions(everyone=False)
                              )

owner = [177375818635280384, 177394669766836224]

bot.add_cog(Moderation(bot))
bot.add_cog(Music(bot))

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    activity = discord.Activity(name="LDT Bot", type=discord.ActivityType.playing)
    await bot.change_presence(activity=activity)



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
        a = eval(ctx.message.content.replace('!!eval ',''))
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
    suppot.colour = random.randint(0, 0xFFFFFF)
    if len(args) < 1:
        suppot.set_author(name="Title", url="https://discord.gg/24f6aWF",
                          icon_url="https://sheepbot.net/static/css/rS.png")
        suppot.add_field(name="Un message supplémentaire",
                         value="[Website](http://sheepbot.net/)\n[Discord Server](https://discord.gg/24f6aWF)\n",
                         inline=False)
        for categorie, content in COMMAND_LIST.items():
            text = ""
            for commande in content:
                text += "`{0}`, ".format(commande.name)
            text = text[0:len(text) - 2]
            suppot.add_field(name="*{0}* : ".format(categorie), value=text, inline=False)
        suppot.add_field(name="Bottom line",
                         value="[link](https://www.patreon.com/SheepBot)", inline=False)
    else:
        search = args[0]
        if search in com.keys():
            suppot.set_author(name="I've found it !", url="http://discord.gg/KbXqEVe",
                              icon_url="https://sheepbot.net/static/css/rS.png")
            helpo = com[search].help
            if helpo == None or helpo == "None":
                helpo = "No description found"
            suppot.add_field(name="{0}".format(search), value="{0}".format(helpo))
        else:
            suppot.set_author(name="Sorry !", url="https://discord.gg/24f6aWF",
                              icon_url="https://sheepbot.net/static/css/rS.png")
            suppot.add_field(name="There is no command named `{0}` !".format(search),
                             value="Check the list of command with !!help or visite the [full documentation](http://sheepbot.net/doc/)")
    await ctx.send(embed=suppot)




bot.run(TOKEN)
