import asyncio
from asyncio.tasks import sleep
from logging import exception
import shelve
from datetime import datetime
from datetime import timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import tzlocal
import os
import discord
from discord.ext import commands
from decouple import config


try:
    token = os.environ.get('DISCORD_TOKEN')
    my_server = os.environ.get('MY_SERVER')
    league_logins = os.environ.get('LEAGUE_LOGINS')
    if token == None:
        exception()
except:
    token = config('DISCORD_TOKEN')
    my_server = config('MY_SERVER')
    league_logins = config('LEAGUE_LOGINS')

league_logins = [league_logins]

sched = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))
sched.start()

bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    channel = bot.get_channel(id=1008634623938539610)
    await channel.send(f"Online at {str(datetime.now()).split('.')[0]}")
    # guild = discord.utils.find(lambda g: g.name == my_server, bot.guilds)
    # guild = discord.utils.get(bot.guilds, name=my_server)
    # print(f'Server:{guild.name}(id: {guild.id})')

#region Reminder
@bot.command(name='remindme')
async def set_reminder(ctx, reminder, time, delay=7):
    await ctx.message.delete(delay=delay)
    if time[0] == " ":
        return  

    now = datetime.now()
    seconds = await process_time(time)
    end_date = now + timedelta(seconds=seconds+1) # stop interval just before the 2nd run
    sched.add_job(
        remind, 
        kwargs={"msg":reminder, "id":ctx.author.id},
        trigger='interval', 
        seconds=seconds, 
        start_date=now, 
        end_date=end_date,
        name=reminder)
    await ctx.send(f'```{reminder} has been set for {end_date}.```', delete_after=delay)

# For reminders
async def process_time(time):
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
    time = time.split(" ")
    seconds = 0
    for ele in time:
        for i, char in enumerate(ele):
            if char.isalpha():
                if char.lower() == "d":
                    seconds += int(ele[:i]) * 60 * 60 * 24
                elif char.lower() == "h":
                    seconds += int(ele[:i]) * 60 * 60
                elif char.lower() == 'm':
                    seconds += int(ele[:i]) * 60
                elif char.lower() == 's':
                    seconds += int(ele[:i])
    return seconds

#remind in reminders channel
async def remind(msg, id):
    channel = bot.get_channel(id=1008635857252646962)
    await channel.send(f'**REMINDER: ** <@{id}> {msg}')


@bot.command(name='reminders')
async def get_reminders(ctx, delay=15):
    await ctx.message.delete(delay=delay)
    jobs = sched.get_jobs()
    if not jobs:
        await ctx.send(f'No reminders.', delete_after=delay)
    else:
        await ctx.send(f'**Reminders:**', delete_after=delay)
        for job in jobs:
            await ctx.send(f'```{job.name}\n{job.next_run_time}```', delete_after=delay)
#endregion

# Clear msgs
@bot.command(name='clear')
async def delete_messages(ctx, amount=10, delay=7):
    await ctx.message.delete(delay=delay)
    await ctx.channel.purge(limit=amount+1)

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

# Helper function for projects command
async def send_list_as_code(ctx, list, delay):
    for item in list:
        await ctx.send(f'```{item}```', delete_after=delay)
#endregion

@bot.command(name='commands')
async def help(ctx, delay=30):
    await ctx.message.delete(delay=delay)
    await ctx.send(
        f'7 Commands', delete_after=delay)
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
    await ctx.send(
        f'**.remindme "(reminder)" "(xd xh xm xs)"**\nAdds (reminder) to time in format (d h m s)',
        delete_after=delay)
    await ctx.send(
        f'**.reminders**\nDisplays all reminders.',
        delete_after=delay)
    await ctx.send(
        f'**.clear (number of msgs to delete)**\nDeletes (number of msgs to delete) in channel that command was called in.',
        delete_after=delay)
bot.run(token)