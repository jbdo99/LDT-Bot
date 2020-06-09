from discord.ext import commands
import aiohttp
import discord
import socket
from lxml import html
import random
import io
from PIL import Image, ImageDraw, ImageFont
import re
import asyncio
import functools
from wand.image import Image as IMAGE
from wand.resource import limits
import numpy as np
import traceback
import urllib.parse
import httpx
from PIL import ImageChops
import textwrap

limits['memory'] = 2048 * 2048 * 100
limits['width'] = 3000
limits['height'] = 3000
limits['thread'] = 1
limits['time'] = 6
limits['throttle'] = 50




conn = aiohttp.TCPConnector(
            family=socket.AF_INET,
            ssl=False,
        )


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_lmg(ctx):
        chan = ctx.message.channel
        try:
            if ctx.message.mentions:
                return ctx.message.mentions[0].avatar_url
        except:
            pass
        pattern = re.compile(r'https?://\S*\.(jpeg|jpg|png|webp)([?]\S*)?')
        v = pattern.search(ctx.message.content)
        if v:
            return v.group(0)

        async for message in chan.history(limit=4):
            v = pattern.search(message.content)
            if v:
                return v.group(0)

            if message.attachments:
                if int(message.attachments[0].size) < 5000000:
                    return message.attachments[0].url

            for emb in message.embeds:
                if emb.image.url:
                    return emb.image.url

        if ctx.message.author.avatar_url:
            return ctx.message.author.avatar_url
        return ctx.message.author.default_avatar_url

    async def get_apic(ctx):
        pic_url = await Images.get_lmg(ctx)
        img = io.BytesIO()
        conn = aiohttp.TCPConnector(
            family=socket.AF_INET,
            verify_ssl=False,
        )
        async with aiohttp.ClientSession(connector=conn) as session:
            async with session.get(str(pic_url)) as resp:
                img.write(await resp.read())

        return img



    def shitt(img):
        im1 = Image.open("content/img/b19.png")
        im2 = Image.open(img)
        im2 = im2.resize((128, 128))
        box = 190, 640
        im2 = im2.convert('RGBA')
        im2 = im2.rotate(-40, expand=True)
        im1.paste(im2, box=box, mask=im2)
        lol = io.BytesIO()
        im1.convert('RGB').save(lol, 'PNG', optimize=True)
        lol.name = 'shit.png'
        lol.seek(0)
        return lol

    def shit2(txt):
        im1 = Image.open("content/img/b19.png")
        im2 = Image.new('RGBA', (400, 330))
        draw = ImageDraw.Draw(im2)
        xy = 0, 0
        if txt.lower() == 'sheepbot':
            txt = 'Fuck you ;)'

        if len(txt) > 28:
            txt = textwrap.wrap(txt, width=30)
            txt = "\n".join(txt)

        if len(txt) > 10:
            F = ImageFont.truetype(font="content/ttf/arimo.ttf", size=25)
            draw.multiline_text(xy, txt, fill=(0, 0, 0, 250), font=F, anchor=None, direction=None,
                                features=None)
            im2 = im2.rotate(47, expand=True)
            im1.paste(im2, box=(170, 550), mask=im2)
        else:
            F = ImageFont.truetype(font="content/ttf/arimo.ttf", size=45)
            draw.multiline_text(xy, txt, fill=(0, 0, 0, 250), font=F, anchor=None, direction=None,
                                features=None)
            im2 = im2.rotate(47, expand=True)
            im1.paste(im2, box=(170, 550), mask=im2)
        lol = io.BytesIO()
        im1.convert('RGB').save(lol, 'PNG', optimize=True)
        lol.name = 'shit.png'
        lol.seek(0)
        return lol

    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(2, 4, type=commands.BucketType.channel)
    async def shit(self, ctx, *, userD: str = None):
        """Shit some thing"""
        try:
            await ctx.trigger_typing()
            url = False
            if userD:
                if userD.startswith('http'):
                    img_url = userD
                    url = True
                else:
                    url = False
                pass
            else:
                ctx.message.mentions.append(ctx.message.author)
            loop = asyncio.get_event_loop()
            if True:
                if len(ctx.message.mentions) > 0 or url:
                    if not url:
                        userD = ctx.message.mentions[0]
                        img_url = userD.avatar_url
                    else:
                        pass
                    img = io.BytesIO()
                    conn = aiohttp.TCPConnector(
                        family=socket.AF_INET,
                        verify_ssl=False,
                    )
                    async with aiohttp.ClientSession(connector=conn) as session:
                        async with session.get(str(img_url), allow_redirects=True) as resp:
                            img.write(await resp.read())

                    lol = await loop.run_in_executor(None,functools.partial(Images.shitt,img))

                    await ctx.send(file=discord.File(lol, filename=None))
                    return None
                else:
                    lol = await loop.run_in_executor(None, functools.partial(Images.shit2,userD))
                    await ctx.send(file=discord.File(lol, filename=None))
                    return
            else:
                pass
        except Exception as e:
            await ctx.send("error : ```" + str(e) + "```")
            raise e


    def dicki(txt):
        im1 = Image.open("content/img/prblm.jpg")
        im2 = Image.new('RGBA', (300, 100))
        draw = ImageDraw.Draw(im2)
        xy = 0, 0
        top = 40
        size = 30
        if len(txt) < 7:
            size = 40
        if len(txt) > 10:
            txt = txt[:10] + '\n' + txt[10:]
        if len(txt) > 24:
            txt = txt[:24] + '\n' + txt[24:]
            top = 10
        if txt.lower() == 'sheepbot':
            txt = ctx.message.author.name
        F = ImageFont.truetype(font="content/ttf/arimo.ttf", size=size)
        draw.multiline_text(xy, txt, fill=(0, 0, 0, 250), font=F, anchor=None, direction=None,
                            features=None)
        box = 550, top
        im1.paste(im2, box=box, mask=im2)
        lol = io.BytesIO()
        im1.convert('RGB').save(lol, 'PNG', optimize=True)
        lol.name = 'DiCk.png'
        lol.seek(0)
        return lol




    @commands.command(pass_context=True, no_pm=True, rest_is_raw=True)
    @commands.cooldown(2, 4, type=commands.BucketType.channel)
    async def dick(self, ctx, *, userD: str = None):
        """Make something suck ..."""
        try:
            await ctx.trigger_typing()
            url = False
            if userD:
                pass
            else:
                ctx.message.mentions.append(ctx.message.author)
            if True:
                if True:
                    loop = asyncio.get_event_loop()
                    txt = userD or ctx.message.author.name
                    lol = await loop.run_in_executor(None, functools.partial(Images.dicki, txt))
                    await ctx.send(file=discord.File(lol, filename=None))
                    return
        except Exception as e:
            await ctx.send("error : ```" + str(e) + "```")


    def sonn(txt):
        im1 = Image.open("content/img/opi.jpg")
        im2 = Image.new('RGBA', (300, 100))
        draw = ImageDraw.Draw(im2)
        xy = 0, 0
        top = 340
        size = 30
        cot = 50
        if len(txt) > 17:
            size = 24
            cot = 20
        if len(txt) > 24:
            txt = txt[:24] + '\n' + txt[24:]
            top = 330
        F = ImageFont.truetype(font="content/ttf/arimo.ttf", size=size)
        draw.multiline_text(xy, txt, fill=(0, 0, 0, 250), font=F, anchor=None, direction=None,
                            features=None)
        box = cot, top
        im1.paste(im2, box=box, mask=im2)
        lol = io.BytesIO()
        im1.convert('RGB').save(lol, 'PNG', optimize=True)
        lol.name = 'DiCk.png'
        lol.seek(0)
        return lol




    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(3, 4, type=commands.BucketType.channel)
    async def son(self, ctx, *, userD: str = None):
        try:
            await ctx.trigger_typing()
            url = False
            if userD:
                pass
            else:
                ctx.message.mentions.append(ctx.message.author)
            if True:
                if True:
                    loop = asyncio.get_event_loop()
                    txt = userD or ctx.message.author.name + " is my friend"
                    lol = await loop.run_in_executor(None, functools.partial(Images.sonn, txt))
                    await ctx.send(file=discord.File(lol, filename=None))
                    return
        except Exception as e:
            await ctx.send("error : ```" + str(e) + "```")
            raise e



    def trut(txt):
        im1 = Image.open("content/img/trut.jpg")
        im2 = Image.new('RGBA', (300, 100))
        draw = ImageDraw.Draw(im2)
        xy = 0, 0
        top = 300
        size = 13
        txt = textwrap.wrap(txt, width=15)
        txt = "\n".join(txt)

        if len(txt) < 10:
            size = 20
            top = 330

        if len(txt)>60:
            top = 275

        print(txt)
        F = ImageFont.truetype(font="content/ttf/arimo.ttf", size=size)
        draw.multiline_text(xy, txt, fill=(0, 0, 0, 250), font=F, anchor=None, direction=None,
                            features=None, spacing=2, align="center")
        box = 90, top
        im1.paste(im2, box=box, mask=im2)
        lol = io.BytesIO()
        im1.convert('RGB').save(lol, 'PNG', optimize=True)
        lol.name = 'DiCk.png'
        lol.seek(0)
        return lol



    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(2, 4, type=commands.BucketType.channel)
    async def truth(self, ctx, *, userD: str = 'sample text'):
        try:
            await ctx.trigger_typing()
            url = False
            if userD:
                pass
            else:
                ctx.message.mentions.append(ctx.message.author)
            if True:
                if True:
                    loop = asyncio.get_event_loop()
                    txt = " " + userD or str(ctx.message.author.name)
                    lol = await loop.run_in_executor(None, functools.partial(Images.trut, txt))
                    await ctx.send(file=discord.File(lol, filename=None))
                    return
        except Exception as e:
            await ctx.send("error : ```" + str(e) + "```")
            raise e
            # await ctx.send("you need to put a text")

    def quad_as_rect(quad):
        if quad[0] != quad[2]: return False
        if quad[1] != quad[7]: return False
        if quad[4] != quad[6]: return False
        if quad[3] != quad[5]: return False
        return True

    def quad_to_rect(quad):
        assert (len(quad) == 8)
        # assert(quad_as_rect(quad))
        return (quad[0], quad[1], quad[4], quad[3])

    def rect_to_quad(rect):
        assert (len(rect) == 4)
        return (rect[0], rect[1], rect[0], rect[3], rect[2], rect[3], rect[2], rect[1])

    def shape_to_rect(shape):
        assert (len(shape) == 2)
        return (0, 0, shape[0], shape[1])

    def griddify(rect, w_div, h_div):
        w = rect[2] - rect[0]
        h = rect[3] - rect[1]
        x_step = w / float(w_div)
        y_step = h / float(h_div)
        y = rect[1]
        grid_vertex_matrix = []
        for _ in range(h_div + 1):
            grid_vertex_matrix.append([])
            x = rect[0]
            for _ in range(w_div + 1):
                grid_vertex_matrix[-1].append([int(x), int(y)])
                x += x_step
            y += y_step
        grid = np.array(grid_vertex_matrix)
        return grid

    def distort_grid(org_grid, max_shift):
        new_grid = np.copy(org_grid)
        x_min = np.min(new_grid[:, :, 0])
        y_min = np.min(new_grid[:, :, 1])
        x_max = np.max(new_grid[:, :, 0])
        y_max = np.max(new_grid[:, :, 1])
        new_grid += np.random.randint(- max_shift, max_shift + 1, new_grid.shape)
        new_grid[:, :, 0] = np.maximum(x_min, new_grid[:, :, 0])
        new_grid[:, :, 1] = np.maximum(y_min, new_grid[:, :, 1])
        new_grid[:, :, 0] = np.minimum(x_max, new_grid[:, :, 0])
        new_grid[:, :, 1] = np.minimum(y_max, new_grid[:, :, 1])
        return new_grid

    def grid_to_mesh(src_grid, dst_grid):
        assert (src_grid.shape == dst_grid.shape)
        mesh = []
        for i in range(src_grid.shape[0] - 1):
            for j in range(src_grid.shape[1] - 1):
                src_quad = [src_grid[i, j, 0], src_grid[i, j, 1],
                            src_grid[i + 1, j, 0], src_grid[i + 1, j, 1],
                            src_grid[i + 1, j + 1, 0], src_grid[i + 1, j + 1, 1],
                            src_grid[i, j + 1, 0], src_grid[i, j + 1, 1]]
                dst_quad = [dst_grid[i, j, 0], dst_grid[i, j, 1],
                            dst_grid[i + 1, j, 0], dst_grid[i + 1, j, 1],
                            dst_grid[i + 1, j + 1, 0], dst_grid[i + 1, j + 1, 1],
                            dst_grid[i, j + 1, 0], dst_grid[i, j + 1, 1]]
                dst_rect = Images.quad_to_rect(dst_quad)
                mesh.append([dst_rect, src_quad])
        return mesh


    def magi(img):
        im = Image.open(img)
        dst_grid = Images.griddify(Images.shape_to_rect(im.size), 4, 4)
        puis = (im.size[0] * im.size[1]) / (10 / (1 / im.size[0]))
        src_grid = Images.distort_grid(dst_grid, puis)
        mesh = Images.grid_to_mesh(src_grid, dst_grid)
        im = im.transform(im.size, Image.MESH, mesh)
        lol = io.BytesIO()
        im.convert('RGBA').save(lol, 'PNG', optimize=True)
        lol.name = 'caca.png'
        lol.seek(0)
        return lol



    @commands.command(pass_context=True, no_pm=True,aliases=['magi','magic','magique','magick'])
    @commands.cooldown(2, 5, type=commands.BucketType.channel)
    async def magik(self, ctx):
        try:
            await ctx.trigger_typing()
            loop = asyncio.get_event_loop()
            img = await Images.get_apic(ctx)
            lol = await loop.run_in_executor(None, functools.partial(Images.magi, img))
            await ctx.send(file=discord.File(lol, filename=None))
        except Exception as e:
            await ctx.send("error : ```" + str(e) + "```")
            raise e



    def magik22(img):
        try:
            i = IMAGE(blob=img.getvalue())
        except:
            im = Image.open(img)
            lol = io.BytesIO()
            im.convert('RGB').save(lol, 'PNG', optimize=True)
            i = IMAGE(blob=lol.getvalue())

        i.format = 'jpg'
        print(i.size)
        i.alpha_channel = True
        i.transform(resize='800x800>')
        s = i.size
        print(s)
        i.liquid_rescale(width=int(i.width * 0.5), height=int(i.height * 0.5),delta_x=1, rigidity=0)
        i.liquid_rescale(width=int(i.width * 1.5), height=int(i.height * 1.5), delta_x=2,rigidity=0)
        #i.sample(s[0],s[1])
        magikd = io.BytesIO()
        i.save(file=magikd)
        magikd.seek(0)
        return magikd

    """
    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(2, 6, type=commands.BucketType.channel)
    async def magik2(self, ctx):
        try:
            await ctx.trigger_typing()
            loop = asyncio.get_event_loop()
            imgg = await Images.get_apic(ctx)
            lol = await loop.run_in_executor(None, functools.partial(Images.magik22, imgg))
            await ctx.send(file=discord.File(lol, filename="killmepls.jpg"))
        except Exception as e:
            await ctx.send("error : ```" + str(e) + "```")
            raise e

    """

    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(2, 6, type=commands.BucketType.channel)
    async def magik2(self, ctx,*, intense:int = None):
        "Magik image : usage !!magik2 *intensity*"
        try:
            await ctx.trigger_typing()
            pic = await Images.get_lmg(ctx)
            pic = urllib.parse.quote(str(pic))
            if intense:url = "https://nekobot.xyz/api/imagegen?type=magik&intensity="+str(intense)+"&image=" + str(pic)
            else:url = "https://nekobot.xyz/api/imagegen?type=magik&image=" + str(pic)
            print(url)
            js = await self.httpget(url)
            image_url = js['message']
            embed = discord.Embed(color=random.randint(0 , 0xFFFFFF))
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)
        except Exception as e:
            traceback.print_exc()
            await ctx.send(e)


    def braz(img):
            im2 = Image.open("content/img/braz.png")
            im1 = Image.open(img)
            im2 = im2.resize((260, 130))
            im1 = im1.resize((400, 400))
            box = 140, 295
            im2 = im2.convert('RGBA')
            im1.paste(im2, box=box, mask=im2)
            lol = io.BytesIO()
            im1.convert('RGBA').save(lol, 'PNG', optimize=True)
            lol.name = 'BRAZZER.png'
            lol.seek(0)
            return lol



    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(2, 4, type=commands.BucketType.channel)
    async def brazzer(self, ctx, *, userD: str = None):
        try:
            await ctx.trigger_typing()
            if True:
                if True:
                    loop = asyncio.get_event_loop()
                    img = await Images.get_apic(ctx)
                    lol = await loop.run_in_executor(None, functools.partial(Images.braz, img))
                    await ctx.send(file=discord.File(lol, filename=None))
        except Exception as e:
            await ctx.send("error : ```" + str(e) + "```")
            raise e

    def crop_to_circle(im):
        bigsize = (im.size[0] * 3 , im.size[1] * 3)
        mask = Image.new('L' , bigsize , 0)
        ImageDraw.Draw(mask).ellipse((0 , 0) + bigsize , fill=255)
        mask = mask.resize(im.size , Image.ANTIALIAS)
        mask = ImageChops.darker(mask , im.split()[-1])
        im.putalpha(mask)
        return im

    def autis(img):
        im1 = Image.open("content/img/jb.jpg")
        im2 = Image.open(img).convert('RGBA')
        im2 = im2.resize((150, 150))
        im2 = Images.crop_to_circle(im2)
        #im1 = im1.resize((485, 596))
        box = 280, 110
        im2 = im2.convert('RGBA')
        im1.paste(im2, box=box, mask=im2)
        lol = io.BytesIO()
        im1.save(lol, 'PNG', optimize=False)
        lol.name = 'pictureofdumb.png'
        lol.seek(0)
        return lol



    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(2, 4, type=commands.BucketType.channel)
    async def autistic(self, ctx):
        try:
            await ctx.trigger_typing()
            im = await Images.get_apic(ctx)
            loop = asyncio.get_event_loop()
            lol = await loop.run_in_executor(None , functools.partial(Images.autis , im))
            await ctx.send(file=discord.File(lol , filename=None))
        except Exception as e:
            await ctx.send("Lol something broke : "+str(e))
            traceback.print_exc()


    def ripp(img):
        im1 = Image.open("content/img/rip.png")
        im2 = Image.open(img)
        im2 = im2.resize((200, 200))
        im1 = im1.resize((485, 596))
        box = 130, 300
        im2 = im2.convert('RGBA')
        im1.paste(im2, box=box, mask=im2)
        lol = io.BytesIO()
        im1.save(lol, 'PNG', optimize=False)
        lol.name = 'RIP.png'
        lol.seek(0)
        return lol




    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(2, 4, type=commands.BucketType.channel)
    async def rip(self, ctx, *, userD: str = None):
        try:
            await ctx.trigger_typing()
            url = False
            if userD:
                if userD.startswith('http://') or userD.startswith('https://'):
                    img_url = userD
                    url = True
                else:
                    url = False
                pass
            else:
                ctx.message.mentions.append(ctx.message.author)
            if True:
                if len(ctx.message.mentions) > 0 or url:
                    if not url:
                        userD = ctx.message.mentions[0]
                        img_url = userD.avatar_url
                    else:
                        pass
                    img = io.BytesIO()
                    async with aiohttp.ClientSession() as session:
                        async with session.get(str(img_url)) as resp:
                            img.write(await resp.read())
                    loop = asyncio.get_event_loop()
                    lol = await loop.run_in_executor(None, functools.partial(Images.ripp, img))
                    await ctx.send(file=discord.File(lol, filename=None))
                else:
                    await ctx.send("you need to @mention someone or to use an image link")
        except Exception as e:
            await ctx.send("If you use mention, the account must have a avatar")
            raise e



    def resp(img):
        im1 = Image.open("content/img/f.jpg")
        im2 = Image.open(img)
        im2 = im2.convert('RGBA')
        im2 = im2.rotate(7, expand=True)
        im2 = im2.resize((70, 89))
        # im1 = im1.resize((485,596))
        box = 365, 95
        im1.paste(im2, box=box, mask=im2)
        lol = io.BytesIO()
        im1.convert('RGB').save(lol, 'PNG', optimize=True)
        lol.name = 'ResPekt.png'
        lol.seek(0)
        return lol



    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(2, 4, type=commands.BucketType.channel)
    async def respect(self, ctx, *, userD: str = None):
        try:
            await ctx.trigger_typing()
            url = False
            if userD:
                if userD.startswith('http://') or userD.startswith('https://'):
                    img_url = userD
                    url = True
                else:
                    url = False
                pass
            else:
                ctx.message.mentions.append(ctx.message.author)
            if True:
                if len(ctx.message.mentions) > 0 or url:
                    if not url:
                        userD = ctx.message.mentions[0]
                        img_url = userD.avatar_url
                    else:
                        pass
                    img = io.BytesIO()
                    async with aiohttp.ClientSession() as session:
                        async with session.get(str(img_url)) as resp:
                            img.write(await resp.read())
                    loop = asyncio.get_event_loop()
                    lol = await loop.run_in_executor(None, functools.partial(Images.resp, img))
                    await ctx.send(file=discord.File(lol, filename=None))
                else:
                    await ctx.send("you need to @mention someone or to use an image link")
        except Exception as e:
            await ctx.send("error : ```" + str(e) + "```")
            raise e


    def jpg(img,quali):
        img = Image.open(img)
        img2 = io.BytesIO()
        img = img.convert("RGBA")
        img.save(img2, 'JPEG', quality=quali, optimize=False, subsampling=2)
        img2.name = "killmepls.jpg"
        img2.seek(0)
        return img2


    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(2, 4, type=commands.BucketType.channel)
    async def jpeg2(self, ctx, *, quali: str = None):
        try:
            await ctx.trigger_typing()
            try:
                q = quali.split(' ')
                if len(q)>1:
                    qual = int(q[1])
                quali = qual // 2
            except:
                quali = 6

            if quali<1:quali = 1
            if quali > 75:quali = 75
            img = await Images.get_apic(ctx)
            loop = asyncio.get_event_loop()
            lol = await loop.run_in_executor(None, functools.partial(Images.jpg, img,quali))
            await ctx.send(file=discord.File(lol, filename=None))
        except Exception as e:
            await ctx.send(e)



    @commands.command(pass_context=True, no_pm=True)
    async def avatar(self, ctx):
        if ctx.message.mentions:
            await ctx.send(ctx.message.mentions[0].avatar_url)
            return
        if ctx.message.author.avatar_url:
            await ctx.send(ctx.message.author.avatar_url)
        else:
            await ctx.send(ctx.message.author.default_avatar_url)


    async def httpget(self,url):
        async with httpx.AsyncClient() as client:
            js = await client.get(str(url),timeout=30)
        return js.json()



    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(2, 4, type=commands.BucketType.channel)
    async def deepfry(self, ctx):
        try:
            await ctx.trigger_typing()
            pic = await Images.get_lmg(ctx)
            pic = urllib.parse.quote(str(pic))
            url = "https://nekobot.xyz/api/imagegen?type=deepfry&image="+str(pic)
            js = await self.httpget(url)
            image_url = js['message']
            embed = discord.Embed(color=random.randint(0, 0xFFFFFF))
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)
        except Exception as e:
            traceback.print_exc()
            await ctx.send(e)


    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(2, 4, type=commands.BucketType.channel)
    async def jpeg(self, ctx):
        try:
            await ctx.trigger_typing()
            pic = await Images.get_lmg(ctx)
            pic = urllib.parse.quote(str(pic))
            url = "https://nekobot.xyz/api/imagegen?type=jpeg&url="+str(pic)
            js = await self.httpget(url)
            image_url = js['message']
            embed = discord.Embed(color=random.randint(0, 0xFFFFFF))
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)
        except Exception as e:
            traceback.print_exc()
            await ctx.send(e)


    @commands.command(pass_context=True , no_pm=True)
    @commands.cooldown(2, 4, commands.BucketType.user)
    async def phcomment(self, ctx, *, comment: str='Sample Text'):
        """PronHub Comment Image"""
        await ctx.trigger_typing()
        try:
            url = (f"https://nekobot.xyz/api/imagegen?type=phcomment"
                              f"&image={urllib.parse.quote(str(ctx.author.avatar_url_as(format='png')))}"
                              f"&text={urllib.parse.quote(str(comment))}&username={urllib.parse.quote(str(ctx.author.name))}")

            js = await self.httpget(url)
            if not js["success"]:
                return await ctx.send("**Errored**")

            embed = discord.Embed(color=random.randint(0 , 0xFFFFFF))
            embed.set_image(url=js['message'])
            await ctx.send(embed=embed)
        except :
            traceback.print_exc()


    @commands.command(pass_context=True , no_pm=True)
    @commands.cooldown(2, 4, commands.BucketType.user)
    async def tweet(self, ctx, username: str = None, *, text: str='Sample text'):
        """send a tweet"""
        await ctx.trigger_typing()

        if not username:
            username = ctx.message.author.name
        url = (f"https://nekobot.xyz/api/imagegen?type=tweet"
                          "&username=%s"
                          "&text=%s" % (urllib.parse.quote(str(username)), urllib.parse.quote(str(text)),))


        js = await self.httpget(url)

        if not js["success"]:
            return await ctx.send("**Errored**")

        embed = discord.Embed(color=random.randint(0 , 0xFFFFFF))
        embed.set_image(url=js['message'])
        await ctx.send(embed=embed)


    @commands.command(pass_context=True , no_pm=True)
    @commands.cooldown(2, 4, commands.BucketType.user)
    async def trumptweet(self, ctx, *,text: str='Sample text'):
        """send a tweet"""
        await ctx.trigger_typing()
        url = "https://nekobot.xyz/api/imagegen?type=trumptweet&text="+urllib.parse.quote(str(text))
        js = await self.httpget(url)

        if not js["success"]:
            return await ctx.send("**Errored**")

        embed = discord.Embed(color=random.randint(0 , 0xFFFFFF))
        embed.set_image(url=js['message'])
        await ctx.send(embed=embed)


    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(2, 4, type=commands.BucketType.channel)
    async def trash(self, ctx):
        try:
            await ctx.trigger_typing()
            pic = await Images.get_lmg(ctx)
            pic = urllib.parse.quote(str(pic))
            url = "https://nekobot.xyz/api/imagegen?type=trash&url="+str(pic)
            js = await self.httpget(url)
            image_url = js['message']
            embed = discord.Embed(color=random.randint(0, 0xFFFFFF))
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)
        except Exception as e:
            traceback.print_exc()
            await ctx.send(e)

    @commands.command(pass_context=True , no_pm=True)
    @commands.cooldown(2, 4, commands.BucketType.user)
    async def changemymind(self, ctx, *,text: str='Sample text'):
        """send a tweet"""
        await ctx.trigger_typing()
        url = "https://nekobot.xyz/api/imagegen?type=changemymind&text="+urllib.parse.quote(str(text))
        print(str(url))

        js = await self.httpget(url)

        if not js["success"]:
            return await ctx.send("**Errored**")

        embed = discord.Embed(color=random.randint(0 , 0xFFFFFF))
        embed.set_image(url=js['message'])
        await ctx.send(embed=embed)

