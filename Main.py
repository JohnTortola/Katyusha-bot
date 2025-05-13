import discord
from discord.ext import commands
from yt_downloader import download_audio
from dotenv import load_dotenv
import os

intents = discord.Intents.default()
intents.message_content = True

#settings for the prefix
katyusha = commands.Bot(command_prefix='!kt ', intents=intents)

#when the bot is loaded
@katyusha.event
async def on_ready():
    print(f'Katyusha is loaded. Logged in as {katyusha.user}');

@katyusha.command()
async def hello(ctx):
    await ctx.send("Panzer vooooor!!")


@katyusha.command()
async def play(ctx, url: str):

    #Voice connection (check where user who called this function is and will join/move to the channel)
    if not ctx.author.voice:
        await ctx.send("Where do you even want me to play that, idiot!")
        return
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        vc = await voice_channel.connect()
    else:
        vc = ctx.voice_client
        await vc.move_to(voice_channel)

    #check if its already playing something
    if ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.send("Get in line if you want this one played!")
        return
    
    await ctx.send("Play this thing? What a pain, let's see...")
    #will bring an error instead of path if it goes wrong
    success, path, title = download_audio(url) 

    if success:
        mp3_path = path
        await ctx.send(f"Alright here goes nothing...\nNow playing: {title}")
        print(f"\nReturn is {success}, Now playing at {path}")

        if not vc.is_playing():
            vc.play(discord.FFmpegPCMAudio(path), after=lambda e: print(f"It's done: {e}"))
    else:
        await ctx.send("Is the thing you want illegal or something?? I can't download it!!")
        print(f"\nError downloading and converting file: {path}")

#bot will stop playing an audio if there is an audio playing
@katyusha.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("I didn't even want to play it anyways...")
    else:
        await ctx.send("Stop what you freak???")

#bot will leave if it is in a discord voice channel
@katyusha.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Just so you know, I'm just leaving because I want to")
    else:
        await ctx.send("Are you stupid? leave what?")

#load the .env file with the discord bot token
load_dotenv()
token = os.getenv("DISCORD_BOT_TOKEN")
print(token)
katyusha.run(token)