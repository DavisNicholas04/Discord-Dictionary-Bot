import discord
import datetime

async def invalid_command(msg: discord.Message):
    await msg.channel.send(f"```{msg.content}``` is not a valid command")


async def channel_does_not_exist(channel: discord.TextChannel):
    await channel.send(
        """This channel does not exist.```
    1. Check your spelling
    2. Check your capitalization 
    3. Ensure that you actually created this channel```
    """
    )


async def formatting_error(msg: discord.Message, error_channel: discord.TextChannel):
    await error_channel.send(
        f"ERROR IN FORMATTING: please follow the format convention\n"
        f"<word>: <#>. <definition> [optional] <#>. <definition>\n"
        f"example 1: あわてぃーはーてぃ: 1. hurry, in a hurry\n"
        f"example 2: でーじ : 1. Really, very 2. truly, genuinely\n"
        f"author: {msg.author.name}: {msg.author.discriminator}\n"
        f"content: ``{msg.content}``\n``` ```")


async def non_writing_channel(msg: discord.Message, channel: discord.TextChannel):
    content = msg.content
    author = msg.author.name
    discriminator = msg.author.discriminator
    warning = await channel.send(
        "You should not be here, this is my channel. I'm deleting your message from MY channel.\n-")
    await msg.delete()
    notification = await channel.send(
        f"MESSAGE DELETED FROM {channel.name} channel.\nauthor:{author}: {discriminator}\ncontent:\n{content}\n"
        f"THIS NOTIFICATION WILL BE DELETED AT APPROXIMATELY "
        f"{(datetime.datetime.now() + datetime.timedelta(hours=6)).strftime('%m-%d-%Y %H:%M:%S')}\n``` ```")

    await warning.delete(delay=21600)
    await notification.delete(delay=21600)