import asyncio

from discord.ext import commands

import cogs.misc as misc

class Song:
    def __init__(self, player, message):
        self.player = player

        self.message = message
        self.user = message.author
        self.channel = message.channel

        self.title = self.player.title
        self.url = self.player.url

        m, s = divmod(self.player.duration, 60)
        h, m = divmod(m, 60)

        if h:
            self.duration = "{}:{}:{}".format(h,m,s)
        elif m:
            self.duration = "{}:{}".format(m, s)
        else:
            self.duration = "{}".format(s)


class VoiceClient:
    def __init__(self, client, bot_):
        self.bot = bot_
        self.client = client

        self.current_song = None
        self.player = None
        self.queue = []

        self.loop = self.bot.loop.create_task(self.main_loop())

    async def play_next_in_queue(self):
        options = {
            'default_search': 'auto',
            'quiet': True,
            'ignoreerrors': True,
        }
        try:
            song = self.queue[0]
            del self.queue[0]
        except IndexError:
            print("error: Nothing next in queue")
            return None

        self.player = await self.client.create_ytdl_player(song.url, ytdl_options=options)
        self.current_song = Song(self.player, song.message)

        await self.bot.send_message(self.current_song.channel, "now playing `{}` ({})".format(
            self.current_song.title, self.current_song.duration))

        self.player.start()

    async def add_to_queue(self, name, message):
        options = {
            'default_search': 'auto',
            'quiet': True,
            'ignoreerrors': True,
            'skip_download': True,
        }

        song = Song(await self.client.create_ytdl_player(name, ytdl_options=options), message)
        self.queue.append(song)

        if self.player and self.player.is_playing():
            await self.bot.send_message(song.channel, "`{}` added to queue ({})".format(song.title, song.duration))

    async def main_loop(self):
        while True:
            try:
                await asyncio.sleep(1)
                if self.queue and (not self.player or not self.player.is_playing()):
                    await self.play_next_in_queue()
            except Exception as e:
                print("error: ", e)


class Voice:
    def __init__(self, bot_):
        self.bot = bot_
        self.voice_clients = {}

    '''
    @commands.group(pass_context=True)
    async def voice(self, context):
        if not context.invoked_subcommand:
            context.invoked_with = "help"
            await commands.bot._default_help_command(context, "voice")
    '''
    @commands.command(name="play", aliases=['add', 'p'], pass_context=True)
    async def voice_play(self, context, *song: str):
        """Search for and play something

        Examples:
          play relaxing flute sounds
          play https://www.youtube.com/watch?v=y_gknRMZ-OU
        """
        message = context.message

        voice = self.voice_clients.get(message.server.id)
        if not voice:
            if message.author.voice_channel:
                voice = VoiceClient(await self.bot.join_voice_channel(message.author.voice_channel), self.bot)
                self.voice_clients[message.server.id] = voice
            else:
                await self.bot.say("You aren't connected to a voice channel\nhint do [v j")

        await voice.add_to_queue(' '.join(song), message)

    @commands.command(name="stop", aliases=['skip', 's'], pass_context=True)
    async def voice_stop(self, context):
        """Skips the currently playing song"""
        voice = self.voice_clients.get(context.message.server.id)
        if voice.current_song.user != context.message.author and not misc.is_admin(context):
            await self.bot.say("You can't stop the music~~\n(you're not the person who put this on)")
            return None
        voice.player.stop()

    @commands.command(name="queue", aliases=['q'], pass_context=True)
    async def voice_queue(self, context):
        """Show the songs currently in the queue

        Because discord only allows 2000 characters per message,
        sometimes not all songs in the queue can be shown"""
        message = context.message

        voice = self.voice_clients.get(message.server.id)
        if not voice:
            self.bot.say("You haven't joined a voice channel; there is not queue")
            return None

        reply = "Current queue:"
        counter = 1
        for song in voice.queue:
            reply += "\n{}: `{}` ({})".format(counter, song.title, song.duration)
            counter += 1
        await self.bot.say(reply)

    @commands.command(name="remove", aliases=['qr'], pass_context=True)
    async def voice_remove(self, context, number):
        voice = self.voice_clients.get(context.message.server.id)
        song = voice.queue[int(number)-1]
        if song.user != context.message.author and not misc.is_admin(context):
            await self.bot.say("You can't stop the music~~\n(you're not the person who put this on)")
            return None
        await self.bot.say("Removed `{}` from the queue".format(song.title))
        del voice.queue[int(number)-1]

    @commands.command(name="playing", aliases=['cp'], pass_context=True)
    async def voice_playing(self, context):
        voice = self.voice_clients.get(context.message.server.id)
        song = voice.current_song
        await self.bot.say("now playing `{}` ({})".format(song.title, song.duration))

    @commands.command(name="leave", aliases=['l'], pass_context=True)
    async def voice_leave(self, context):
        voice = self.voice_clients[context.message.server.id]
        if not misc.is_admin(context):
            for song in voice.queue:
                if song.user != context.message.author:
                    await self.bot.say("You can't stop the music~~\n(someone else still has something queued)")
                    return None
        await voice.client.disconnect()
        voice.queue = []
        voice.player.stop()


def setup(bot):
    bot.add_cog(Voice(bot))

    # Todo:
    # Fix any bugs that pop up
    # Pause/resume