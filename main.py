import datetime
import re
import os
import discord
from dotenv import load_dotenv


class myClient(discord.Client):

    async def on_ready(self):
        print(f"Logged in as {client.user}".format(client))
        global all_channels_iterator
        all_channels_iterator = client.get_all_channels()
        global bot_channel_name
        bot_channel_name = "bot-commands"
        global bot_channel
        bot_channel = discord.utils.get(all_channels_iterator, name=bot_channel_name)
        global bot_channel_id
        bot_channel_id = bot_channel.id

    async def on_message(self, msg: discord.Message):
        in_bot_channel = msg.channel.name == bot_channel_name
        in_dictionary_channel = msg.channel.name == "dictionary"
        in_phrases_channel = msg.channel.name == phrases
        in_history_channel = msg.channel.name == history
        # if msg.author == client.user:
        #     return

        if in_bot_channel:
            await set_channel(msg)
        elif in_dictionary_channel:
            await reformat_dictionary_input(msg)
        else:
            await invalid_command(msg)
        return


async def reformat_dictionary_input(msg: discord.Message):
    if re.search('[1-9]*(?=.)(?=[a-zA-Z]+(?=:)(?=[1-9]*(?=.)(?=[a-zA-Z, ]+)))+$', msg.content):
        msgArray = msg.content.split(":")
        term = msgArray[0]
        definitions = msgArray[1]
        split_definitions = re.split('[1-9]*(?=.)$', definitions)
        num_of_definitions = len(split_definitions)
        reformatted_msg = term

        for i, defs in range(num_of_definitions), split_definitions:
            reformatted_msg = f"__{reformatted_msg}__: ```{i + 1}. {defs}```"
        sent_message = await msg.channel.send(reformatted_msg)

        await history_channel.send(f"Formatted on: ``{datetime.date.today().strftime('%d-%m-%Y %H:%M:%S')}``\n "
                                   f"New Message Link: {sent_message.jump_url}\n"
                                   f"Original Content:\n{msg}")
        # await history_channel.send(f"Created on: ``{datetime.date.today().strftime('%d-%m-%Y %H:%M:%S')}``\n "
        #                            f"Link: {sent_message.jump_url}\n"
        #                            f"Content:\n{sent_message}")
        await msg.delete()
    else:
        await history_channel.send(
            f"ERROR IN FORMATTING: please follow the format convention\n"
            f"<word>: <#>. <definition> [optional] <#>. <definition>\n"
            f"example 1: あわてぃーはーてぃ: 1. hurry, in a hurry\n"
            f"example 2: でーじ : 1. Really, very 2. truly, genuinely\n\n"
            f"content: {msg}")
        await msg.delete()


async def set_channel(msg: discord.Message):
    valid_command = \
        msg.content.startswith(set_dictionary_channel) or \
        msg.content.startswith(set_phrase_channel) or \
        msg.content.startswith(set_undefined_words_channel) or \
        msg.content.startswith(set_history_channel)
    typeOf_channel = ""
    if valid_command:
        given_command = msg.content.split(' ')[0]
        channel = msg.content.removeprefix(given_command).strip()
        print(given_command)
        if channel in ["dictionary", "文と句", "needs-translation", "history", "bot-commands"]:
            if given_command == set_dictionary_channel:
                global dictionary
                dictionary = channel
                global dictionary_channel
                dictionary_channel = discord.utils.get(msg.guild.channels, name=dictionary)
                global dictionary_id
                dictionary_id = dictionary_channel.id
                typeOf_channel = "dictionary"

            elif given_command == set_phrase_channel:
                global phrases
                phrases = channel
                global phrases_channel
                phrases_channel = discord.utils.get(msg.guild.channels, name=phrases)
                global phrases_id
                phrases_id = phrases_channel.id
                typeOf_channel = "phrases"

            elif given_command == set_undefined_words_channel:
                global undefined_words
                undefined_words = channel
                global undefined_words_channel
                undefined_words_channel = discord.utils.get(msg.guild.channels, name=undefined_words)
                global undefined_words_id
                undefined_words_id = undefined_words_channel.id
                typeOf_channel = "undefined_words"

            elif given_command == set_history_channel:
                global history
                history = channel
                global history_channel
                history_channel = discord.utils.get(msg.guild.channels, name=history)
                global history_id
                history_id = history_channel.id
                typeOf_channel = "history"

            if typeOf_channel != "":
                await msg.channel.send(f"{typeOf_channel} channel set to: {channel}")
                return
        else:
            await msg.channel.send(channel_does_not_exist)


async def invalid_command(msg: discord.Message):
    await msg.channel.send(f"```{msg}``` is not a valid command")


# Messages
channel_does_not_exist = \
    """This channel does not exist.```
    1. Check your spelling
    2. Check your capitalization 
    3. Ensure that you actually created this channel
    ```
    """

# Bot channel commands and variables
set_dictionary_channel = "/setDict"
set_phrase_channel = "/setPhrase"
set_undefined_words_channel = "/setUWords"
set_history_channel = "/setHist"
all_channels_iterator = None

dictionary = None
dictionary_channel: discord.TextChannel
dictionary_id = None

phrases = None
phrases_channel: discord.TextChannel
phrases_id = None

undefined_words = None
undefined_words_channel: discord.TextChannel
undefined_words_id = None

history = None
history_channel: discord.TextChannel
history_id = None

bot_channel_name = None
bot_channel = None
bot_channel_id = None

# Vitals
intents = discord.Intents.all()
client = myClient(intents=intents)
load_dotenv()
client.run(os.environ['DISCORD_TOKEN'])

# elif inBotChannel and msg.content.startswith("setDict/"):
# if channel in discord.Guild.text_channels:
#     dictionary = channel
#     await msg.channel.send(f"dictionary channel set to: {dictionary}")
# else:
#     await msg.channel.send(channel_does_not_exist)
