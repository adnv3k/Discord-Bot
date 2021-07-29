import asyncio
from asyncio.tasks import sleep
import os
# from ytdownloader import get_tracks
import shelve
import datetime
import discord
from discord import message
from discord import channel
from discord.ext.commands.core import command
from discord.flags import Intents, MessageFlags
from discord.ext import commands
import redis

redis_server = redis.Redis()
token = str(redis_server.get('DISCORD_TOKEN').decode('utf-8'))
my_server = str(redis_server.get('MY_SERVER').decode('utf-8'))
league_logins = str(redis_server.get('LEAGUE_LOGINS').decode('utf-8'))
cmd = str(redis_server.get('CMD').decode('utf-8')).split('(NEWLINE)')

bot = commands.Bot(command_prefix='.')
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    guild = discord.utils.find(lambda g: g.name == my_server, bot.guilds)
    guild = discord.utils.get(bot.guilds, name=my_server)
    print(f'Server:{guild.name}(id: {guild.id})')

#region League
@bot.command(name='leag')
async def get_league_logins(ctx):
    await ctx.message.delete(delay=5)
    await ctx.send(league_logins, delete_after=5)

@bot.command(name='league')
async def get_league_logins(ctx):
    await ctx.message.delete(delay=5)
    await ctx.send(league_logins, delete_after=5)
#endregion

#region CMD commands
@bot.command(name='cmd')
async def get_cmd_shortcuts(ctx,delay=7):
    await ctx.message.delete(delay=delay)
    for item in cmd:
        await ctx.send(f'```{item}```', delete_after=delay)
    print(f'cmd retrieved at: {str(datetime.datetime.now())}')
#endregion

#region Projects
@bot.command(name='projects')
async def get_projects(ctx,delay=30):
    await ctx.message.delete(delay=delay)
    projects_file = shelve.open('projects')
    await ctx.send(f'**{len(projects_file)} Projects**',delete_after=delay)
    for i in range(1, len([*projects_file])):
        p = i*4
        try:
            await ctx.send(f'\n\n**{[*projects_file][p-4].upper()}:**\n{projects_file[[*projects_file][p-4]]}\n\n**{[*projects_file][p-3].upper()}:**\n{projects_file[[*projects_file][p-3]]}\n\n**{[*projects_file][p-2].upper()}:**\n{projects_file[[*projects_file][p-2]]}\n\n**{[*projects_file][p-1].upper()}:**\n{projects_file[[*projects_file][p-1]]}',delete_after=delay)
        except:
            p -= 1
            try:
                await ctx.send(f'\n\n**{[*projects_file][p-3].upper()}:**\n{projects_file[[*projects_file][p-3]]}\n\n**{[*projects_file][p-2].upper()}:**\n{projects_file[[*projects_file][p-2]]}\n\n**{[*projects_file][p-1].upper()}:**\n{projects_file[[*projects_file][p-1]]}',delete_after=delay)
            except:
                p -= 1
                try:
                    await ctx.send(f'\n\n**{[*projects_file][p-2].upper()}:**\n{projects_file[[*projects_file][p-2]]}\n\n**{[*projects_file][p-1].upper()}:**\n{projects_file[[*projects_file][p-1]]}',delete_after=delay)
                except:
                    p -= 1
                    try:
                        await ctx.send(f'\n\n**{[*projects_file][p-1].upper()}:**\n{projects_file[[*projects_file][p-1]]}',delete_after=delay)
                    except:
                        pass
    projects_file.close()
    await ctx.send(f'**END**',delete_after=delay)

#Old code Save in case of bugs. delete later
@bot.command(name='projectsold')
async def get_projects(ctx,delay=30):
    await ctx.message.delete(delay=delay)
    projects_file = shelve.open('projects')
    await ctx.send(f'{len(projects_file)} Projects',delete_after=delay)
    for n in projects_file:
        await ctx.send(f'```Project: {n}\n{projects_file[n]}```',delete_after=delay)
    projects_file.close()

@bot.command(name='add_project')
async def add(ctx, name, info):
    await ctx.message.delete(delay=5)
    name = name.upper()
    projects_file = shelve.open('projects')
    projects_file[name] = info
    projects_file.close()
    await ctx.send(f'Added "{name}" to projects.', delete_after=7)

@bot.command(name='remove_project')
async def remove_project(ctx, name):
    await ctx.message.delete(delay=7)
    name = name.upper()
    projects_file = shelve.open('projects')
    del projects_file[name]
    projects_file.close()
    await ctx.send(f'"{name}" removed from projects.',delete_after=7)

@bot.command(name='append_project')
async def append_project(ctx, name, appendage):
    await ctx.message.delete(delay=7)
    name = name.upper()
    projects_file = shelve.open('projects')
    projects_file[name] += f'\n{appendage}'
    projects_file.close()
    await ctx.send(f'"{appendage}" has been added to "{name}."',delete_after=7)
#endregion

@bot.command(name='commands')
async def help(ctx, delay=30):
    await ctx.message.delete(delay=delay)
    await ctx.send(f'4 Commands', delete_after=delay)
    await ctx.send(f'.projects (delay):\nDisplays all items in the projects list for (delay) seconds.\n================================================================================',delete_after=delay)
    await ctx.send(f'.add_project "(name)" "(description)":\nAdds a project to the projects list with (name) and (description).\n================================================================================',delete_after=delay)
    await ctx.send(f'.remove_project "(name)":\nRemoves a project from the projects list by (name).\n================================================================================',delete_after=delay)
    await ctx.send(f'.append_project "(name)" "(appendage)":\nAdds (appendage) to the description of the project (name).\n================================================================================',delete_after=delay)

bot.run(token)
#TODO 