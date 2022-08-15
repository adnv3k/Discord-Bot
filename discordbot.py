import asyncio
from asyncio.tasks import sleep
import shelve
from datetime import datetime
from datetime import timedelta
import string
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import tzlocal
import os
import discord
from discord.ext import commands
from decouple import config

# token = config('DISCORD_TOKEN')
# my_server = config('MY_SERVER')
# league_logins = config('LEAGUE_LOGINS')
sched = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))
sched.start()

# import redis depreciated 

token = os.environ.get('DISCORD_TOKEN')
my_server = os.environ.get('MY_SERVER')
league_logins = os.environ.get('LEAGUE_LOGINS')
league_logins = [league_logins]

# depreciated code from when using a redis server to serve secrets
# redis_server = redis.Redis()
# token = str(redis_server.get('DISCORD_TOKEN').decode('utf-8'))
# my_server = str(redis_server.get('MY_SERVER').decode('utf-8'))
# league_logins = str(redis_server.get('LEAGUE_LOGINS').decode('utf-8')).split('(NEWLINE)')
# cmd = str(redis_server.get('CMD').decode('utf-8')).split('(NEWLINE)')

bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    # guild = discord.utils.find(lambda g: g.name == my_server, bot.guilds)
    # guild = discord.utils.get(bot.guilds, name=my_server)
    # print(f'Server:{guild.name}(id: {guild.id})')

# Helper function
# For projects command
async def send_list_as_code(ctx, list, delay):
    for item in list:
        await ctx.send(f'```{item}```', delete_after=delay)

# For reminders
async def process_time(ctx, time):
    '''
    "in 1 hr"
    "in 30 seconds"
    in 1 hour and 45 minutes
    in 3 hours
    tomorrow

    '''
    '''
    seconds, sec, secs, s
    minutes, min, mins, m
    hours, hrs, hr, h
    days, day, d
    week, weeks, wk
    month, months
    tomorrow
    
    '''
    # time = "in 1h 23m 3s"
    # in HH:MM:SS
    # time = "in 1 hour and 45 minutes and 15 seconds"
    time = time.split(" ")
    seconds = 0
    for ele in time[1:]:
        for i, char in enumerate(ele):
            if char.isalpha():
                if char.lower() == "h":
                    seconds += int(ele[:i]) * 60 * 60
                elif char.lower() == 'm':
                    seconds += int(ele[:i]) * 60
                elif char.lower() == 's':
                    seconds += int(ele[:i])
    return seconds

#remind in reminders channel
async def remind(ctx, msg, id):
    await ctx.send(f'**REMINDER: ** <@{id}> {msg}', delete_after=5)


#region Reminder
@bot.command(name='remindme')
async def set_reminder(ctx, reminder, time, delay=7):
    await ctx.message.delete(delay=delay)
    if time[0] == " ":
        return  
    # .remindme "take out garbage" "in 1 hr"
    # reminders = shelve.open('reminders')
    # reminders[reminder] = datetime.timestamp(time)
    # reminders.close()

    now = datetime.now()
    seconds = await process_time(ctx, time)
    print(ctx.author.id)
    end_date = now + timedelta(seconds=seconds+1) # stop interval just before the 2nd run
    sched.add_job(
        remind, 
        kwargs={"ctx":ctx, "msg":reminder, "id":ctx.author.id},
        trigger='interval', 
        seconds=seconds, 
        start_date=now, 
        end_date=end_date)

    await ctx.send(f'{reminder} has been set for {end_date}.', delete_after=delay)

async def get_reminders(ctx, delay=30):
    await ctx.send(f'reminders:', delete_after=delay)


#region League
@bot.command(name='leag')
async def get_league_logins(ctx, delay=5):
    await ctx.message.delete(delay=delay)
    await send_list_as_code(ctx, league_logins, delay)

@bot.command(name='league')
async def get_league_logins(ctx, delay=5):
    await ctx.message.delete(delay=delay)
    await send_list_as_code(ctx, league_logins, delay)
#endregion

#region CMD commands
@bot.command(name='cmd')
async def get_cmd_shortcuts(ctx,delay=7):
    await ctx.message.delete(delay=delay)
    await send_list_as_code(ctx, cmd, delay)
    print(f'cmd retrieved at: {str(datetime.now())}')
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

@bot.command(name='add_project')
async def add(ctx, name, info):
    await ctx.message.delete(delay=5)
    name = name.upper()
    projects_file = shelve.open('projects')
    projects_file[name] = info
    projects_file.close()
    await ctx.send(f'Added "**{name}**" to projects.\n{info}', delete_after=7)

@bot.command(name='remove_project')
async def remove_project(ctx, name):
    await ctx.message.delete(delay=7)
    name = name.upper()
    projects_file = shelve.open('projects')
    del projects_file[name]
    projects_file.close()
    await ctx.send(f'"{name}" removed from projects.', delete_after=7)

@bot.command(name='delete_project')
async def remove_project(ctx, name):
    await ctx.message.delete(delay=7)
    name = name.upper()
    projects_file = shelve.open('projects')
    del projects_file[name]
    projects_file.close()
    await ctx.send(f'"{name}" removed from projects.', delete_after=7)

@bot.command(name='append_project')
async def append_project(ctx, name, appendage):
    await ctx.message.delete(delay=7)
    name = name.upper()
    projects_file = shelve.open('projects')
    projects_file[name] += f'\n{appendage}'
    projects_file.close()
    await ctx.send(f'"{appendage}" has been added to "{name}."', delete_after=7)
#endregion

@bot.command(name='commands')
async def help(ctx, delay=30):
    await ctx.message.delete(delay=delay)
    await ctx.send(
        f'4 Commands', delete_after=delay)
    await ctx.send(
        f'**.projects (delay)**\nDisplays all items in the projects list for (delay) seconds.',
        delete_after=delay)
    await ctx.send(
        f'**.add_project "(name)" "(description)"**\nAdds a project to the projects list with (name) and (description).',
        delete_after=delay)
    await ctx.send(
        f'**.remove_project "(name)"**\nRemoves a project from the projects list by (name).',
        delete_after=delay)
    await ctx.send(
        f'**.append_project "(name)" "(appendage)"**\nAdds (appendage) to the description of the project (name).',
        delete_after=delay)

bot.run(token)