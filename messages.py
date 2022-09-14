import discord
import datetime


async def edited_entry_msg(command_msg: discord.Message, original_msg: discord.Message, new_msg,
                           history_channel: discord.TextChannel, edited_field="MESSAGE EDITED"):
    await history_channel.send(
        f"{edited_field} on: ``{datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S')}``\n"
        f"Link to edited entry: {original_msg.jump_url}\n"
        f"author: {command_msg.author.name}: {command_msg.author.discriminator}\n"
        f"Original Content:\n{original_msg.content}\n"
        f"New Content:\n{new_msg}``` ```"
    )


async def content_reload_msg(history_channel: discord.TextChannel, updated_channel: discord.TextChannel, num_of_msgs):
    await history_channel.send(
        f"{updated_channel} was updated on {datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S')}\n"
        f"There are now {num_of_msgs} entries"
    )


async def formatting_complete_msg(history_channel: discord.TextChannel, original_msg: discord.Message,
                                  reformatted_msg: discord.Message):
    await history_channel.send(f"Formatted on: ``{datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S')}``\n"
                               f"New Message Link: {reformatted_msg.jump_url}\n"
                               # f"index: {index}\n"
                               f"author: {original_msg.author.name}: {original_msg.author.discriminator}\n"
                               f"Original Content:\n{original_msg.content}\n``` ```")


async def entry_not_found(dictionary_channel: discord.TextChannel, history_channel: discord.TextChannel,
                          original_msg: discord.Message, entry_word):
    cant_find_msg = await dictionary_channel.send(
        f"Could not find {entry_word} in the dictionary. "
        f"make sure it was typed correctly. this message will expire in 30 sec\n"
        f"command typed: {original_msg}"
    )
    await cant_find_msg.delete(delay=30)
    await history_channel.send(
        f"SEARCH FAILED:\nChannel:{dictionary_channel}\n"
        f"author: {original_msg.author.name}: {original_msg.author.discriminator}\n"
        f"Original Content:\n{original_msg.content}\n``` ```"
    )
