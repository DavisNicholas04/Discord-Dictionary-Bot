import discord


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


async def formatting_error(msg: discord.Message, history_channel: discord.TextChannel):
    await history_channel.send(
        f"ERROR IN FORMATTING: please follow the format convention\n"
        f"<word>: <#>. <definition> [optional] <#>. <definition>\n"
        f"example 1: あわてぃーはーてぃ: 1. hurry, in a hurry\n"
        f"example 2: でーじ : 1. Really, very 2. truly, genuinely\n\n"
        f"content: {msg.content}")