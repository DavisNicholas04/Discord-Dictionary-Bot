import datetime
import re
import os
import discord
import error_messages as error
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
        await set_channels_defaults()

    async def on_message(self, msg: discord.Message):
        if msg.author == client.user:
            return
        if await is_in_channel(msg, bot_channel):
            await set_channel(msg)

        elif await is_in_channel(msg, dictionary_channel):
            await reformat_dictionary_input(msg)

        elif await is_in_channel(msg, history_channel):
            await error.non_writing_channel(msg, history_channel)

        elif await is_in_channel(msg, alpha_dict_channel):
            await check_commands(msg)
        return


async def check_commands(msg: discord.Message):
    if msg.content == alphabetize_command:
        await alphabetize_dictionary()


async def reformat_dictionary_input(msg: discord.Message):
    if re.search(
            f"[a-zA-zぁ-ゔァ-ヴー々〆〤ヶ{os.environ['KANJI']} ]+[:][\n]*([ 1-9]+[.][\n]*[a-zA-zぁ-ゔァ-ヴー々〆〤ヶ,{os.environ['KANJI']} ]+)+[\n]*",
            msg.content):
        msgArray = msg.content.split(":")
        term = msgArray[0]
        definitions = msgArray[1]
        split_definitions = re.split('[1-9]+.', definitions)
        split_definitions.pop(0)
        num_of_definitions = len(split_definitions)
        index = get_most_recent_msg_index(dictionary_channel)
        reformatted_msg = f"{index}. __{term}__:"
        for i, defs in zip(range(num_of_definitions), split_definitions):
            reformatted_msg = f"{reformatted_msg}```{i + 1}.{defs.strip()}```"
        sent_message = await msg.channel.send(reformatted_msg)
        await history_channel.send(f"Formatted on: ``{datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S')}``\n"
                                   f"New Message Link: {sent_message.jump_url}\n"
                                   f"index: {index}\n"
                                   f"author: {msg.author.name}: {msg.author.discriminator}\n"
                                   f"Original Content:\n{msg.content}\n``` ```")
        await msg.delete()
    else:
        await error.formatting_error(msg, error_channel)
        await msg.delete()


async def get_most_recent_msg_index(channel: discord.TextChannel):
    recent_msg: discord.Message = [msg async for msg in channel.history(limit=1)][0]
    index = recent_msg.content.split(".", 1)[0]
    return int(index) + 1

async def set_channel(msg: discord.Message):
    valid_command = \
        msg.content.startswith(set_dictionary_channel) or \
        msg.content.startswith(set_phrase_channel) or \
        msg.content.startswith(set_undefined_words_channel) or \
        msg.content.startswith(set_history_channel)
    typeOf_channel = None
    if valid_command:
        given_command = msg.content.split(' ')[0]
        channel = msg.content.removeprefix(given_command).strip()
        if channel in os.environ['DEFAULT_CHANNELS']:
            if given_command == set_dictionary_channel:
                global dictionary_name
                dictionary_name = channel
                global dictionary_channel
                dictionary_channel = discord.utils.get(msg.guild.channels, name=dictionary_name)
                global dictionary_id
                dictionary_id = dictionary_channel.id
                typeOf_channel = "dictionary"

            elif given_command == set_phrase_channel:
                global phrases_name
                phrases_name = channel
                global phrases_channel
                phrases_channel = discord.utils.get(msg.guild.channels, name=phrases_name)
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
                global history_name
                history_name = channel
                global history_channel
                history_channel = discord.utils.get(msg.guild.channels, name=history_name)
                global history_id
                history_id = history_channel.id
                typeOf_channel = "history"

            if typeOf_channel != "":
                await msg.channel.send(f"{typeOf_channel} channel set to: {channel}")
                return
        else:
            await error.channel_does_not_exist(msg.channel)
    else:
        await error.invalid_command(msg)


async def set_channels_defaults():
    text_channels_list = bot_channel.guild.text_channels
    global dictionary_name
    dictionary_name = "dictionary"
    global dictionary_channel
    dictionary_channel = discord.utils.get(text_channels_list, name=dictionary_name)
    global dictionary_id
    dictionary_id = dictionary_channel.id

    global phrases_name
    phrases_name = "文と句"
    global phrases_channel
    phrases_channel = discord.utils.get(text_channels_list, name=phrases_name)
    global phrases_id
    phrases_id = phrases_channel.id

    global undefined_words
    undefined_words = "needs-translation"
    global undefined_words_channel
    undefined_words_channel = discord.utils.get(text_channels_list, name=undefined_words)
    global undefined_words_id
    undefined_words_id = undefined_words_channel.id

    global history_name
    history_name = "history"
    global history_channel
    history_channel = discord.utils.get(text_channels_list, name=history_name)
    global history_id
    history_id = history_channel.id

    global error_channel_name
    error_channel_name = "errors"
    global error_channel
    error_channel = discord.utils.get(text_channels_list, name=error_channel_name)
    global error_channel_id
    error_channel_id = error_channel.id

    global alpha_dict_name
    alpha_dict_name = "alphabetical-order-dictionary"
    global alpha_dict_channel
    alpha_dict_channel = discord.utils.get(text_channels_list, name=alpha_dict_name)
    global alpha_dict_channel_id
    alpha_dict_channel_id = alpha_dict_channel.id


async def is_in_channel(msg: discord.Message, channel: discord.TextChannel):
    if msg.channel == channel:
        return True
    else:
        return False





async def alphabetize_dictionary():
    messages_list = [message.content async for message in dictionary_channel.history()]
    num_of_msgs = messages_list.__len__()
    await alpha_dict_channel.purge(limit=num_of_msgs)
    messages_list.sort(key=sort_by_word)
    for message in messages_list:
        await alpha_dict_channel.send(message)
    await history_channel.send(
        f"{alpha_dict_name} was updated on {datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S')}"
        f"\nThere are now {num_of_msgs} entries")


def sort_by_word(content):
    word = content.split(":", 1)[0]
    return word



# Bot channel commands and variables
set_dictionary_channel = "/setDict"
set_phrase_channel = "/setPhrase"
set_undefined_words_channel = "/setUWords"
set_history_channel = "/setHist"
set_alpha_dict_channel = "/setAZDict"
alphabetize_command = "/alphabetize"

all_channels_iterator = None

dictionary_name = None
dictionary_channel: discord.TextChannel
dictionary_id = None

phrases_name = None
phrases_channel: discord.TextChannel
phrases_id = None

undefined_words = None
undefined_words_channel: discord.TextChannel
undefined_words_id = None

history_name = None
history_channel: discord.TextChannel
history_id = None

bot_channel_name = None
bot_channel: discord.TextChannel
bot_channel_id = None

error_channel_name = None
error_channel: discord.TextChannel
error_channel_id = None

alpha_dict_name = None
alpha_dict_channel: discord.TextChannel
alpha_dict_channel_id = None

# Vitals
intents = discord.Intents.all()
client = myClient(intents=intents)
load_dotenv()
client.run(os.environ['DISCORD_TOKEN'])
