# Discord-Dictionary-Bot (MVP) <sub><sub><sup>This is a personal project. Documentation may be slow</sub></sub></sup>

This bot is for formatting dictionary entries in discord.

### Formatting
Enter dictionary entries within the format and your entry will be deleted, formatted and reposted by the bot.
format users must follow:

1. ```<word>: <number>. <defintion>  <definition set>```
  
    - \<word>: word you want to define
    - \<number>: words can have multiple definitions, use a number to separate them
    - \<definition>: the definition you want to assign to this entries word
    - \<definition set>: <number>. <definition> | EMPTY
  
2. more formats comming soon
 
Allowed input: Latin Alphabet (i.e.: ABC), Hiragana (i.e.: あいう)、Katakana (i.e.: アイウ), and Kanji (i.e.: 花華鼻)
  
### Backslash commands 

Changing which channels are associated with the dictionary, phrases, undefined words, and success logging are as follows 

(**NOTICE: These commmands must be sent in a channel named __bot-commands__**):
  
```/setDict <channelName>```
  By default the bot will set this channel to a channel named **dictionary**. This command sets the channel that will act as the dictionary. all user inputs in dictionary channel will be replaced with bot input with a record of the original input sent to the history channel.
  If there is an error with formatting, it will be sent to the error channel (must be named error as of MVP) with a error message. You can copy your message and reformat it appropriately.
  
```/setHist <channelName>```
  By default the bot will set this channel to a channel named **history**. This command sets the channel that will print out the history of entries and, in future updates, entry edits.
  Typing is not allowed in this channel, if you type it will be deleted and you will recieve a msg notifying you that this channel is not for typing. the bot will repost the content you posted in the history channel in case it was meant for the dictionary. In the MVP version of the app, the error msg and reprint is perminant, but this will be changed so that any typing in this channel will only be recorded for 30 minutes (or some set time).
  
**Recommended**: turn off typing for this channel to avoid loss of content

  ```/setWords <channelName>```
    By default the bot will set this channel to a channel named **needs-translation**. This command sets the channel that will hold words that you want to define at a later date. No formatting is currently enforced and the bot will not interact with this channel
    
  ```/setPhrase <channelName>```
      By default the bot will set this channel to a channel named **文と句**. This command sets the channel that will hold phrases. The intended use of this channel is to see the defined or undefined words used in context. No formatting is currently enforced and the bot will not interact with this channel. 

**Dictionary channel commands**

```/edit <entry-word> name=<new entry-word name>```

```/edit <entry-word> num=<definition number> def=<replacement definition entry>```

```/edit <entry-word> num=<definition-number> remove```

```/add <entry-word> def=<new definition>```

```DEFINITION-SAFE-DELETE (comming soon)```

**alphabetical order dictionary channel commands**

```/alpha```


