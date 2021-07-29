## Discord-Bot
Personal discord bot used to quickly store and retrieve various notes. 

Simple overview of use/purpose.

## Description

An in-depth paragraph about your project and overview of use.
This bot is hosted on AWS in an EC2 instance. The redis library is used to obscure sensitive information. 

## Getting Started

### Dependencies
Created with python 3.9
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
