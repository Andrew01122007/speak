# 導入Discord.py
import discord
import json
import os
import asyncio

from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks

with open('setting.json', 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)
# bot = commands.Bot(command_prefix='&')
# client是我們與Discord連結的橋樑
# client = discord.Client()
# print('請先設定我在玩啥')
# playing = input(str())
playing = "&help"
guild_ids = [1087567593587621939]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='&', case_insensitive=False, intents=intents,
                   activity=discord.Game(name=playing), status=discord.Status.online, help_command=None)


# bot.slash = SlashCommand(bot, sync_commands=True)
# logging.basicConfig(level=logging.INFO)


@bot.event
async def on_ready():
    print('目前登入身份：', bot.user)
    channel = bot.get_channel(0)
    await channel.send(f'目前登入身份：{bot.user}')
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    url = "https://www.youtube.com/watch?v=dQ_d_VKrFgM"
    game = discord.Streaming(name="走れソリよー♪風の様にー♪月見原をー♪ぱどるぱどるー♪", url=url)
    # discord.Status.<狀態>，可以是online,offline,idle,dnd,invisible
    await bot.change_presence(status=discord.Status.online, activity=game)
    print(bot.guilds)
    try:
        synced = await bot.tree.sync()
        print(f"Synced {synced} commands")
    except Exception as e:
        print("An error occurred while syncing: ", e)
    # for g in guild_ids:
    #     guild = discord.Object(id=g)
    #     bot.tree.copy_global_to(guild=guild)
    #     await bot.tree.sync(guild=guild)
    #     print(f'command loed:{guild}')
    now_ping.stop()


@app_commands.command(name="sync", description="同步Slash commands到全域或是當前伺服器")
@app_commands.rename(area="範圍")
@app_commands.choices(area=[Choice(name="當前伺服器", value=0), Choice(name="全域伺服器", value=1)])
@app_commands.guilds(discord.Object(id=0))
async def slash_sync(interaction: discord.Interaction, area: int = 0):
    await interaction.response.defer()
    if area == 0 and interaction.guild:  # 複製全域指令，同步到當前伺服器，不需等待
        bot.tree.copy_global_to(guild=interaction.guild)
        result = await bot.tree.sync(guild=interaction.guild)
    else:  # 同步到全域，需等待一小時
        result = await bot.tree.sync()

    msg = f'已同步以下指令到{"全部" if area == 1 else "當前"}伺服器：{"、".join(cmd.name for cmd in result)}'
    await interaction.edit_original_response(content=msg)
    '''try:
        now_ping.start()
    except RuntimeError:
        now_ping.stop()
        now_ping.restart()'''


@bot.command()
async def check(ctx, arg):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.send(arg)


@bot.command()
async def sreload(ctx, extension):
    await bot.reload_extension(F'cmds.{extension}')
    await ctx.message.delete()
    print(F'---reload {extension} ok---')


@tasks.loop(seconds=10)
async def now_ping():
    try:
        game = discord.Game(f'{playing} {round(float(bot.latency * 1000))}(ms)')
        await bot.change_presence(status=discord.Status.online, activity=game)
        if round(float(bot.latency * 1000)) > 250:
            channel = bot.get_channel(0)
            await channel.send(f'天啊爆ping了 當時{round(float(bot.latency * 1000))}(ms)')
    except OverflowError:
        pass
    except AttributeError:
        pass


async def main():
    async with bot:
        for name in os.listdir('./cmds'):
            if name.endswith('.py'):
                await bot.load_extension(f'cmds.{name[:-3]}')
                print(name)
        await bot.start(jdata['TOKEN'])


asyncio.run(main())

