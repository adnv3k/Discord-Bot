## Discord-Bot
Personal discord bot, hosted on AWS EC2, used to quickly store and retrieve various notes. 


## Description

This bot stores information as a shelf saved locally. The redis library is used to obscure sensitive information. 

## Getting Started

### Dependencies
Created with python 3.9.6
Full list of dependencies availble in requirements.txt


### Usage
**Not intended for public use**

pip install -r requirements.txt

A redis server will need to be configured with appropriate information for: 

Discord Bot Authorization Token (https://discord.com/developers/applications)

Any sensitive information

Commands can be defined using this format:
```
@bot.command(name='COMMAND')
async def append_project(ctx, *arg, **kwarg):
    await ctx.message.delete(delay=7) # This will delete the message that called the command
    # Your code here
```

## Help

```
.help
```
Calls default help command defined by Discord

## License
See the LICENSE.md file for details
