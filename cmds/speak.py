import asyncio
import time
import googletrans
import discord
from discord.ext import commands, tasks
from discord import app_commands
from gtts import gTTS
from typing import Dict, List, Set
from datetime import datetime, timezone, timedelta
from core.classes import Cog_Extensoon
import json

with open('setting.json', 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

class Logs:
    def __init__(self, user: discord.User, msg: str, lang):
        self.user = user
        self.lang = lang
        self.time = time.time()
        self.msg = msg.replace('_',  '\_').replace('*', '\*')
        self.line = f"<t:{int(self.time)}:R> {self.user.mention} : {self.msg}"
        self.line2 = f"<t:{int(self.time)}:R> {self.user.mention}讓我用{self.lang}說 : {self.msg}"

    def __str__(self):
        return self.line2

class HistoryMenuButton(discord.ui.Button['owo']):
    def __init__(self, t, page, size, l):
        if t == 1:
            super().__init__(emoji='⬅️', style=discord.ButtonStyle.blurple, disabled=True if page == 0 else False, row = 0)
        elif t == 2:
            super().__init__(style=discord.ButtonStyle.green,
                       label=f"{page+1}/{size}",disabled=True, row = 0)
        elif t == 3:
            super().__init__(style=discord.ButtonStyle.blurple,
                       emoji='➡', disabled=True if page+1 == size else False, row = 0)
        self.t = t
        self.page = page
        self.size = size
        self.l = l


    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.t == 1:
            self.page -= 1
            await interaction.message.edit(view=HistoryMenu(l=self.l, page=self.page, size=self.size), embed=self.l[self.page])
        elif self.t == 2:
            await interaction.response.send_measage('你怎麼做到的')
        elif self.t == 3:
            self.page += 1
            await interaction.message.edit(view=HistoryMenu(l=self.l, page=self.page, size=self.size), embed=self.l[self.page])


class HistoryMenu(discord.ui.View):
    def __init__(self, l, page=0, size=0, timeout=300):
        super().__init__(timeout=timeout)
        print(l)
        print(len(l))
        self.list = l
        self.page = page
        self.size = len(l)
        for i in [1,2,3]:
            a = HistoryMenuButton(i, page, self.size, l)
            a.row = 0
            self.add_item(a)


class Speak(Cog_Extensoon):
    def __init__(self, bot: commands.Bot):

        self.bot: commands.Bot = bot
        self.last_time = {}
        self.needmove:Set[discord.Guild] = set()
        self.waiting = {}
        self.history: Dict[int: List[Logs]] = {}
        self.nick = {
            '阿諾': [564737111094198274],
        }
        self.ban = []

    def nn(self, user):
        for name in self.nick:
            for id in self.nick[name]:
                if id == user.id:
                    return name
        if user.nick:
            name = user.nick
        else:
            name = user.name
        return name

    def play(self, guild):
        print(self.waiting)
        arg = self.waiting[guild.id][0]
        del self.waiting[guild.id][0]
        translator = googletrans.Translator()
        results = translator.detect(arg[4])
        language = results.lang
        print(language)
        print(arg)
        word = arg[0]
        print('eewww')
        print(word)
        word = word.replace('.', "點").replace('?', '問號')
        if language == 'zh-CN':
            language = 'zh-TW'
        myobj = gTTS(text=word, lang=language, slow=False)
        myobj.save(f"{guild.id}voice.mp3")
        voice = guild.voice_client

        def after(error):
            if error is None:
                if len(self.waiting[guild.id]) > 0:
                    self.play(guild)
            else:
                print("\n\n幹好像出錯了靠邀--------------------------------------------\n\n")
                print(error)

        print('voice.play')
        voice.play(source=discord.FFmpegPCMAudio(
            source=f"{guild.id}voice.mp3"), after=after)
        print(f'我說了{arg[0]}')
        self.last_time[guild.id] = [time.time(), voice]
        if self.leave.is_running():
            pass
        else:
            self.leave.start()

    # @commands.command()
    async def change(self, ctx: commands.Context, *, name):
        print("awa")
        with open('nick.json', 'r', encoding='utf8') as jf:
            data = json.load(jf)
        data[str(ctx.author.id)] = name
        with open('nick.json', 'w', encoding='utf8') as jf:
            json.dump(data, jf)
        await ctx.send(f"{ctx.author.mention}好我記住了 我以後會叫你{name}")

    @tasks.loop(seconds=1)
    async def moveowo(self):
        a = self.needmove
        for g in a:
            voice = g.voice_client
            voice.move_to(self.waiting[g.id][0][2])
            self.play(g)
            self.needmove.remove(g)


    @tasks.loop(seconds=60)
    async def leave(self):
        if len(self.last_time) == 0:
            self.leave.stop()
        for id in self.last_time:
            if time.time() - self.last_time[id][0] > 600:
                voice: discord.VoiceProtocol = self.last_time[id][1]
                await voice.disconnect(force=True)
                voice.cleanup()
                self.last_time.pop(id)

    @commands.command()
    async def limit(self, ctx: commands.Context):
        await ctx.send(f'{self.bot.is_ws_ratelimited()}')

    #@commands.command(name='speak')
    async def speak(self, ctx: commands.Context, *, arg: str):
        if ctx.author.id in self.ban:
            await ctx.send("你被禁止使用這個指令了")
            return
        await ctx.message.delete()
        # print("eee")
        if not ctx.author.voice:
            await ctx.send(":x: 你不在一個音樂頻道，我不知道要去哪".format(ctx.message.author.name))
            print("awa")
            return
        else:
            channel = ctx.author.voice.channel
        # print(discord.voice_client.VoiceClient.is_connected)
        print(channel)

        if ctx.voice_client is None:
            await channel.connect()
            print(self.bot.is_ws_ratelimited())
            await ctx.send(f':arrow_forward: 我在: ``{channel}``')
            print("hey")
        else:
            await ctx.voice_client.move_to(channel)
        print("wew")
        if len(ctx.message.mentions) > 0:
            for mem in ctx.message.mentions:
                name = self.nn(mem)
                arg = arg.replace(f'<@{mem.id}>', name)
        name = self.nn(ctx.author)
        args = f'{name}說{arg}'
        # ["arg", "time", "ch", "user"]
        if self.waiting.get(ctx.guild.id) is None:
            self.waiting[ctx.guild.id] = []
        self.waiting[ctx.guild.id].append([args, ctx.message.created_at, ctx.channel, ctx.author])
        voice = ctx.guild.voice_client
        self.last_time[ctx.guild.id] = [time.time(), voice]
        if self.leave.is_running():
            pass
        else:
            self.leave.start()
        translator = googletrans.Translator()
        results = translator.detect(arg)
        language = results.lang
        if 'zh-CN' in language:
            language = 'zh-TW'
        else:
            language = language[0]
        await ctx.send(f'我用{language}說了{args}', ephemeral=True)
        if ctx.voice_client.is_playing():
            print(f'我等等要說 {args}')
            await self.log(user=ctx.author, arg=args, ch=ctx.channel,
                           time=ctx.message.created_at,
                           fail=True, slash=False)
            return
        else:
            self.play(guild=ctx.guild)
        print(f'我說了{arg}')
        translator = googletrans.Translator()
        results = translator.detect(arg)
        language = results.lang
        if language == 'zh-CN':
            language = 'zh-TW'
        await self.log(user=ctx.author, arg=f'<@{ctx.author.id}>要我用{language}說了 {arg} ', ch=ctx.channel,
                       time=ctx.message.created_at,
                       fail=False, slash=False)

    # @app_commands.command(name='change', description="改變機器人叫你的名子")
    async def _change(self, inte: discord.Interaction, name: str):
        print("awa")
        with open('nick.json', 'r', encoding='utf8') as jf:
            data = json.load(jf)
        data[str(inte.user.id)] = name
        with open('nick.json', 'w', encoding='utf8') as jf:
            json.dump(data, jf)
        await inte.response.send_message(f"{inte.user.mention}好我記住了 我以後會叫你{name}")

    @app_commands.command(name='history', description="查看這個伺服器半個小時內speak的紀錄")
    async def _get_history(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if self.history.get(interaction.guild.id) is None:
            await interaction.edit_original_response(content="沒有半個小時內的紀錄")
            return
        msgs = f"{interaction.guild.name}半個小時內的speak紀錄"
        temp = []
        temp_2 = []
        for i in self.history[interaction.guild.id]:
            if (time.time()-int(i.time)) >= 1800:
                continue
            msgs = f"{msgs}\n{i.line}"
            temp.append(i)
        self.history[interaction.guild.id] = temp
        # print(temp)
        temp_2.append(discord.Embed(title=f'{interaction.guild.name} 半小時內的紀錄'))
        print(temp_2)
        for i in temp:
            # print('a')
            # print(str(i))
            # print(temp_2)
            if len(temp_2[-1].fields) >= 25:
                temp_2.append(discord.Embed(title=f'{interaction.guild.name} 半小時內的紀錄'))
            temp_2[-1].add_field(name='', value=i.line2)
            # print(temp_2)
        await interaction.edit_original_response(content='', embed=temp_2[0], view=HistoryMenu(temp_2))
        embed = discord.Embed(description=f'{interaction.user.mention} 調閱了 {interaction.guild} 的紀錄',
                              color=0x1cbfff)
        embed.set_author(name=f'{interaction.user}', icon_url=interaction.user.avatar)
        channel = self.bot.get_channel(1080868147252432947)
        await channel.send(embed=embed)


    @app_commands.command(name='speak', description="輸入你要我幫你說的話")
    async def _speak(self, inte: discord.Interaction, arg: str):
        await inte.response.defer(ephemeral=True)
        if inte.user.id in self.ban:
            await inte.edit_original_response(content="你被禁止使用這個指令了")
            return
        if not inte.user.voice:
            await inte.edit_original_response(content=":x: 你不在一個音樂頻道，我不知道要去哪".format(inte.user.name))
            return
        else:
            channel = inte.user.voice.channel

        if len(arg) > 300:
            await inte.edit_original_response(content="字數請勿超過300字")
            return
        # print(discord.voice_client.VoiceClient.is_connected)
        # print(channel)
        awa = False
        print('aaaaa')
        print(channel.name)
        print(inte.guild.voice_client)
        if inte.guild.voice_client is None:
            print('oooo')
            await channel.connect()
            print('a')
            await inte.followup.send(content=f':arrow_forward: 我在: ``{channel}``')
            # await inte.edit_original_response(content=f':arrow_forward: 我在: ``{channel}``')
            awa = True
        else:
            if not inte.guild.voice_client.is_playing():
                print('ggggg')
                if channel.id != inte.guild.voice_client.channel.id:
                    await inte.guild.voice_client.move_to(channel)
                    print('b')
                    await inte.followup.send(content=f':arrow_forward: 我在: ``{channel}``')
                    awa = True
            else:
                pass
        name = self.nn(inte.user)
        arg2 = arg
        arg = f'{name}說{arg}'
        # ["arg", "time", "ch", "user"]
        if self.waiting.get(inte.guild.id) is None:
            self.waiting[inte.guild.id] = []
        self.waiting[inte.guild.id].append([arg, inte.created_at, inte.channel, inte.user, arg2])
        print(f'我說了{arg}')
        translator = googletrans.Translator()
        results = translator.detect(arg2)
        language = results.lang
        print(language)
        if language == 'zh-CN':
            language = 'zh-TW'
        if awa:
            await inte.followup.send(content=f'我用{language}說了{arg}', ephemeral=True)
        else:
            await inte.followup.send(content=f'我用{language}說了{arg}', ephemeral=True)
        voice = inte.guild.voice_client
        import time
        self.last_time[inte.guild.id] = [time.time(), voice]
        if self.leave.is_running():
            pass
        else:
            self.leave.start()

        if inte.guild.voice_client.is_playing():
            user = inte.user
            arg = arg
            ch = inte.channel
            time = inte.created_at
            slash = True
            embed = discord.Embed(description=f"原本{user.mention}\n在<#{ch.id}>要我說話，但是我正在說所以等等再說了",
                                  color=0xff9500)
            embed.set_author(name=f'{user}', icon_url=user.avatar)
            embed.add_field(name="內容", value=arg, inline=False)
            embed.set_footer(text=f'{time.astimezone(timezone(timedelta(hours=8)))}  slash:{slash}')
            channel = self.bot.get_channel(0)
            if self.history.get(ch.guild.id) is None:
                self.history[ch.guild.id] = [Logs(user, arg, language)]
            else:
                self.history[ch.guild.id].append(Logs(user, arg, language))
            print(self.history[ch.guild.id])
            await channel.send(embed=embed)

        else:
            user = inte.user
            arg = arg
            ch = inte.channel
            time = inte.created_at
            slash = True
            embed = discord.Embed(description=f"{user.mention}\n在<#{ch.id}>要我說", color=0xff9500)
            embed.set_author(name=f'{user}', icon_url=user.avatar)
            embed.add_field(name="內容", value=arg, inline=False)
            embed.set_footer(text=f'{time.astimezone(timezone(timedelta(hours=8)))}  slash:{slash}')
            channel = self.bot.get_channel(0)
            if self.history.get(ch.guild.id) is None:
                self.history[ch.guild.id] = [Logs(user, arg, language)]
            else:
                self.history[ch.guild.id].append(Logs(user, arg, language))
            print(self.history[ch.guild.id])
            await channel.send(embed=embed)
            self.play(guild=inte.guild)

    async def log(self, user, arg, ch, time, fail, slash):
        print(arg)
        if fail:
            embed = discord.Embed(description=f"原本{user.mention}\n在<#{ch.id}>要我說話，但是我正在說所以等等再說了",
                                  color=0xff9500)
            embed.set_author(name=f'{user}', icon_url=user.avatar)
            embed.add_field(name="內容", value=arg, inline=False)
            embed.set_footer(text=f'{time.astimezone(timezone(timedelta(hours=8)))}  slash:{slash}')
        else:
            embed = discord.Embed(description=f"{user.mention}\n在<#{ch.id}>要我說", color=0xff9500)
            embed.set_author(name=f'{user}', icon_url=user.avatar)
            embed.add_field(name="內容", value=arg, inline=False)
            embed.set_footer(text=f'{time.astimezone(timezone(timedelta(hours=8)))}  slash:{slash}')
        channel = self.bot.get_channel(0)
        if self.history.get(ch.guild.id) is None:
            self.history[ch.guild.id] = [Logs(user, arg)]
        else:
            self.history[ch.guild.id].append(Logs(user, arg))
        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Speak(bot))
