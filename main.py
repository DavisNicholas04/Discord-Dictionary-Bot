import re
import os
import discord
from time import sleep
import error_messages as error
import messages
from dotenv import load_dotenv


intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    global all_channels_iterator
    all_channels_iterator = client.get_all_channels()
    global bot_channel_name
    bot_channel_name = "bot-commands"
    global bot_channel
    bot_channel = discord.utils.get(all_channels_iterator, name=bot_channel_name)
    global bot_channel_id
    bot_channel_id = bot_channel.id
    await set_channels_defaults()


@client.event
async def on_message(msg: discord.Message):
    if msg.author == client.user:
        return
    if await is_in_channel(msg, bot_channel):
        await set_channel(msg)

    elif await is_in_channel(msg, dictionary_channel):
        await check_dict_commands(msg)

    elif await is_in_channel(msg, history_channel):
        await error.non_writing_channel(msg, history_channel)

    elif await is_in_channel(msg, alpha_dict_channel):
        await check_alpha_commands(msg)
    return


async def check_dict_commands(msg: discord.Message):
    """
     format
        - edit-entry-name: /edit <entry-word> name=<new-name>
        - edit-entry-definition: /edit <entry-word> num=<definition-number> def=<new-def>
        - remove-entry-definition: /edit <entry-word> num=<definition-number> remove
    """
    await msg.delete(delay=10)
    if not msg.content.startswith("/"):
        await reformat_dictionary_input(msg)

        # For the /edit command in the dictionary channel
    elif msg.content.startswith(dict_edit):
        command_removed_entry = msg.content.removeprefix(dict_edit).strip()
        entry_word = command_removed_entry.split(" ", 1)[0].strip()
        entry_word_removed_entry = command_removed_entry.removeprefix(entry_word)
        option_and_update = entry_word_removed_entry.split("=", 1)
        searched_msg: discord.Message = await search(entry_word, dictionary_channel)
        if searched_msg is None:
            await messages.entry_not_found(dictionary_channel, history_channel, msg, entry_word)
            return

        # For changing the Entry-Word for a given entry
        if option_and_update[0].strip() == "name":
            desired_name = f"__{option_and_update[1].strip()}__: {searched_msg.content.split(':', 1)[1].strip()}"
            await messages.edited_entry_msg(
                msg, searched_msg, desired_name, history_channel, edited_field="ENTRY-WORD EDITED"
            )
            await searched_msg.edit(content=desired_name)

        # For editing the definition of a dictionary entry
        elif option_and_update[0].strip() == "num":
            if option_and_update[1].__contains__("def="):
                num_and_def = option_and_update[1].split("def=", 1)
                num = num_and_def[0].strip()
                edited_def = num_and_def[1]

                # Splits definition at number and ending tick marks that all definitions are formatted to have
                # and gets rid of white space. vertical lines (|) will signify the split location of the message
                # the case where we edit word x on the y+1 definition.
                # <Word>: ...```<num+0>. <def>``` ```<num+1>.| <def>|```...
                split_def = searched_msg.content.split("```" + num + ".", 1)
                num_of_defs = re.split("[1-9]+.", searched_msg.content).__len__()
                if split_def.__len__() == 1 and num_of_defs > 2:
                    def_num_not_found = await dictionary_channel.send(
                        f"Could not find definition #{num} of {entry_word} in the dictionary. "
                        f"make sure it was typed correctly. this message will expire in 30 sec"
                    )
                    await def_num_not_found.delete(delay=30)
                    await history_channel.send(
                        f"SEARCH FAILED:\nChannel:{dictionary_channel}\n"
                        f"author: {msg.author.name}: {msg.author.discriminator}\n"
                        f"Original Content:\n{msg.content}\n``` ```"
                    )
                    return

                desired_definition_pt1 = split_def[0]
                desired_definition_pt2 = split_def[1].split("```", 1)[1].strip()
                desired_entry_state = f"{desired_definition_pt1}```{num}. {edited_def}```{desired_definition_pt2}"
                await messages.edited_entry_msg(
                    msg, searched_msg, desired_entry_state, history_channel, edited_field=f"DEFINITION {num} EDITED"
                )
                await searched_msg.edit(content=desired_entry_state)

            # For when you want to delete a definition from a given entry
            elif option_and_update[1].strip().endswith("remove"):
                num = int(option_and_update[1].strip().removesuffix("remove").strip())
                split_def = searched_msg.content.split(f"```{num}.", 1)
                desired_definition_pt1 = split_def[0]
                desired_definition_pt2 = split_def[1].split("```", 1)[1].strip()
                desired_entry_state = f"{desired_definition_pt1}{desired_definition_pt2}"

                indexes = re.findall("[1-9][0-9]*", desired_entry_state)

                for i in range(num + 1, indexes.__len__() + 2):
                    desired_entry_state = desired_entry_state.replace(f"{i}.", f"{i-1}.")

                await messages.edited_entry_msg(
                    msg, searched_msg, desired_entry_state, history_channel, edited_field=f"DEFINITION {num} REMOVED"
                )
                await searched_msg.edit(content=desired_entry_state)


            else:
                await error.edit_def_error(msg, error_channel, "def=", "remove")
                return
        else:
            await error.edit_def_error(msg, error_channel, "name=", "num=",
                                       instead_of=f" \"{option_and_update[0].strip()}\"")
            return

    elif msg.content.startswith(dict_add):
        command_removed_entry = msg.content.removeprefix(dict_add).strip()
        entry_word = command_removed_entry.split(" ", 1)[0].strip()
        entry_word_removed_entry = command_removed_entry.removeprefix(entry_word)
        option_and_update = entry_word_removed_entry.split("=", 1)
        searched_msg: discord.Message = await search(entry_word, dictionary_channel)
        if searched_msg is None:
            await messages.entry_not_found(dictionary_channel, history_channel, msg, entry_word)
            return
        num = re.split("[1-9]+.", searched_msg.content).__len__()
        if option_and_update[0].strip() == "def":
            new_def = f"{searched_msg.content}```{num}.{option_and_update[1].strip()}```"
            await messages.edited_entry_msg(
                msg, searched_msg, new_def, history_channel, edited_field="ENTRY-WORD EDITED"
            )
            await searched_msg.edit(content=new_def)

    else:
        await error.def_chan_cmd_error(msg, error_channel)
        return


async def search(word, channel: discord.TextChannel):
    message_history = [msg async for msg in channel.history()]
    for msg in message_history:
        if msg.content.replace("_", "").startswith(word):
            return msg


async def check_alpha_commands(msg: discord.Message):
    if msg.content == alphabetize_command:
        await alphabetize_dictionary()


async def reformat_dictionary_input(msg: discord.Message):
    if re.search(f"[a-zA-z???-??????-??????????????????{os.environ['KANJI']} ]+[:][\n]*"
                 f"([ 1-9]+[.][\n]*[a-zA-z???-??????-??????????????????,{os.environ['KANJI']} ]+)+[\n]*", msg.content):
        await msg.delete()
        searched_entry: discord.Message = await search(msg.content.split(":", 1)[0], dictionary_channel)
        if searched_entry is not None:
            entry_word = searched_entry.content.split(":", 1)[0].strip()
            sent = await dictionary_channel.send(
                f"{entry_word} is already a dictionary entry.\n"
                f"link: {searched_entry.jump_url}\n"
                f"if you would like to add a definition to this entry, use this as a template:"
            )
            sent2 = await dictionary_channel.send(f"/add {entry_word} def=")
            await sent.delete(delay=30)
            await sent2.delete(delay=30)
            await error.repeat_entry(msg, error_channel)
            return
        msgArray = msg.content.split(":")
        term = msgArray[0]
        definitions = msgArray[1]
        print(f"{term}\n\n\n{definitions}")
        split_definitions = re.split('[1-9]+.', definitions)
        # pop(0) to get rid of empty index
        backslash = "\\n"
        split_definitions.pop(0)
        num_of_definitions = len(split_definitions)
        # index = get_most_recent_msg_index(dictionary_channel)
        reformatted_msg = f"__{term}__:"
        for i, defs in zip(range(num_of_definitions), split_definitions):
            final_def = defs.strip().replace("\n", " ")
            reformatted_msg = f"{reformatted_msg}```{i + 1}.{final_def}```"
        sent_message = await msg.channel.send(reformatted_msg)
        await messages.formatting_complete_msg(history_channel, msg, sent_message)
    else:
        await error.formatting_error(msg, error_channel)

# async def get_most_recent_msg_index(channel: discord.TextChannel):
#     recent_msg: discord.Message = [msg async for msg in channel.history(limit=1)][0]
#     index = recent_msg.content.split(".", 1)[0]
#     return int(index) + 1


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
    phrases_name = "?????????"
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
    num_of_msgs = [message.content async for message in alpha_dict_channel.history()].__len__()
    await alpha_dict_channel.purge(limit=num_of_msgs)
    messages_list.sort(key=sort_by_word)
    for message in messages_list:
        await alpha_dict_channel.send(message)
    await messages.content_reload_msg(history_channel, alpha_dict_channel, num_of_msgs)
    sleep(.5)


def sort_by_word(content):
    word = content.split(":", 1)[0]
    return word


# Bot channel commands and variables
set_dictionary_channel = "/setDict"
set_phrase_channel = "/setPhrase"
set_undefined_words_channel = "/setUWords"
set_history_channel = "/setHist"
set_alpha_dict_channel = "/setAZDict"
alphabetize_command = "/alpha"
dict_edit = "/edit"
dict_add = "/add"

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
load_dotenv()
client.run(os.environ['DISCORD_TOKEN'])
