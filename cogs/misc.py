import asyncio
import random
import urllib
import os

import discord
from discord.ext import commands

import cogs.prefix as prefix


def is_admin(context):
    if context.message.author.id == "135496683009081345" or context.message.author.id == '135483608491229184':
        return True
    return context.message.author.server_permissions.manage_server


class Misc:


    def __init__(self, bot_):
        self.bot = bot_
        self.prefix = prefix.Prefix()


    def should_remove(self, m):
        prefix_ = self.prefix.get_prefix(self.bot, m, False)
        if m.content.startswith(prefix_) or m.author.id == "229223616217088001":
            return True
        return False


    @commands.command(name="stats", hidden=True)
    async def misc_stats(self):
        """Shows how many servers butty's in, and how many people are in those servers"""
        total = 0
        for server in self.bot.servers:
            total += len(server.members)
        await self.bot.say("I am currently being a sandwich in {} servers, feeding {} users".format(
            len(self.bot.servers), total)
        )

    @commands.command(name="stats_secret", hidden=True)
    async def misc_stats_secret(self):
        server_list = []
        for server in self.bot.servers:
            server_list.append(server.name)
        server_list.sort()
        await self.bot.say('\n'.join(server_list))

    @commands.command(name="reload", hidden=True)
    async def misc_reload_module(self, module):
       self.bot.unload_extension(module)
       self.bot.load_extension(module)
       await self.bot.say("done")


    @commands.command(name="invite")
    async def misc_invite(self):
        """Show's Butty's invite link

         Just in case you want to add it to your server"""
        await self.bot.say("https://harru.club/invite")
    

    @commands.command(name="clean", aliases=['purge'], pass_context=True)
    async def misc_clean(self, context, number: int = 0):
        """<limit>  -  removes butty's commands and spam

        Removes any messages sent by butty, as well as any
        messages starting with butty's command prefix. 200 message limit"""
        if not is_admin(context):
            await self.bot.say("Sorry, only server admins can use this command")
            return None
        elif not number:
            await self.bot.say("You need to set a limit, I can't just remove everything")
            return None
        elif number > 200:
            await self.bot.say("That's too many, calm down")
            return None

        await self.bot.purge_from(context.message.channel, limit=number, check=self.should_remove)


    @commands.command(name="flip")
    async def misc_flip(self):
        """Flip a coin

        For, you know, picking something randomly
        (as long as there's only two things to choose from)"""
        await self.bot.say("\\*flips coin* ... {}!".format(random.choice(['Heads', 'Tails'])))


    @commands.command(name="roll")
    async def misc_roll(self, number_of_dice : int, number_of_sides : int):
        """<x> <y>  -  where x and y are integers, rolls x dice with y sides

        Rolls some dice, for when just two choices aren't enough"""
        diceno = ""
        if not number_of_sides > 100000000000 and not number_of_dice > 10:
            print("yay")
            for x in range(0, number_of_dice):
                diceno += "For dice " + str(x + 1) + " you rolled: " + str(random.randint(1, number_of_sides)) + "\n"
            await self.bot.say(diceno)
        else:
            await self.bot.say("The side limit is 100000000000 and the dice limit is 10")


    @commands.command(name="duck")
    async def misc_duck(self, *message):
        """<query>  -  makes a lmddgtfy link for your <query>

        lmddgtfy == Let Me Duck Duck Go That For You"""
        query = urllib.parse.quote(' '.join(message))
        await self.bot.say("http://lmddgtfy.net/?q=" + query)


    @commands.command(name="restart", aliases=["getout"], pass_context=True, hidden=True)
    async def misc_restart(self, ctx):
        if ctx.message.author.id == "135483608491229184" or ctx.message.author.id == "135496683009081345":
            os.system("git pull && systemctl restart butty")

    @commands.command(name="presence", aliases=["statuschange"], pass_context=True)
    async def misc_statuschange(self, ctx, *newgame : str):
        if ctx.message.author.id == "135483608491229184" or ctx.message.author.id == "135496683009081345":
            await self.bot.change_presence(game=discord.Game(name=newgame))
            print("yay")


def setup(bot):
    bot.add_cog(Misc(bot))
