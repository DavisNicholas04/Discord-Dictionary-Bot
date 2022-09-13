import discord
import datetime


def history_msg(original_msg: discord.Message, searched_msg: discord.Message,
                history_channel: discord.TextChannel, edited_field="MESSAGE"):
    await history_channel.send(
        f"{edited_field} EDITED on: ``{datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S')}``\n"
        f"Link to edited entry: {searched_msg.jump_url}"
        f"author: {original_msg.author.name}: {original_msg.author.discriminator}\n"
        f"Original Content:\n``{searched_msg.content}``\n``` ```"
    )
