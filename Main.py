import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from collections import defaultdict
import asyncio
from YtDownloader import download_audio
from AudioCleaner import clean_audios
from ChatBot import talk

intents = discord.Intents.default()
intents.message_content = True

#settings for the prefix
katyusha = commands.Bot(command_prefix='!k ', intents=intents)

#load the .env file with the discord bot token
load_dotenv()
token = os.getenv("DISCORD_BOT_TOKEN")
audio_env_path = os.getenv("AUDIO_PATH")
ffmpeg_env_path = os.getenv("FFMPEG_PATH") #both ffmpeg and ffprobe are exe paths
ffprobe_env_path = os.getenv("FFPROBE_PATH")
context_env_path = os.getenv("CONTEXT_PATH")
bot_loop = katyusha.loop
queues = defaultdict(list)



#when the bot is loaded
@katyusha.event
async def on_ready():
    print(f'Katyusha is loaded. Logged in as {katyusha.user}');
    if audio_env_path is None:
        raise ValueError("AUDIO_PATH enviroment variable is missing")
    os.makedirs(audio_env_path, exist_ok=True)

    if context_env_path is None:
        raise ValueError("CONTEXT_PATH enviroment variable is missing")
    os.makedirs(context_env_path, exist_ok=True)



#simple hello command
@katyusha.command()
async def ping(ctx):
    await ctx.send("pong")



#play music
@katyusha.command()
async def play(ctx, url: str):
    guild_id = ctx.guild.id

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
    
    await ctx.send("Play this thing? What a pain, let's see...")
    if len(queues[guild_id]) > 10:
        await ctx.send("Enough! i'm not going to keep track of all these songs, give me a break!")
        return
    #will bring an error instead of path if it goes wrong
    success, path, title = download_audio(url, output_path=audio_env_path, ffmpeg_path=ffmpeg_env_path, ffprobe_path=ffprobe_env_path) 

    if success:
        queues[guild_id].append(path)
        all_queued = [song for queue in queues.values() for song in queue] 
        clean_audios(AUDIO_FOLDER=audio_env_path, current_queues=all_queued)
        if len(queues[guild_id]) > 0:
            await ctx.send(f"Get in line if you want this one played!")
            

        if not vc.is_playing():
            await play_next(ctx, vc, guild_id)
            #vc.play(discord.FFmpegPCMAudio(path), after=lambda e: print(f"It's done: {e}"))
            
    else:
        await ctx.send("Is the thing you want illegal or something?? I can't download it!! (Also you'd better not be trying to play some 10-hour meme video)")
        print(f"\nError downloading and converting file: {path}")


#plays next song in queue
@katyusha.command()
async def play_next(ctx, vc, guild_id):

    if queues[guild_id]:
        next_song = queues[guild_id].pop(0)
        vc.play(discord.FFmpegPCMAudio(next_song), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx, vc, guild_id), katyusha.loop))
        await ctx.send(f"Alright here's this garbage...\nNow playing: {os.path.basename(next_song)}")
        print(f"\nReturn is success, Now playing at {os.path.basename(next_song)} on server {guild_id}")
    else:
        await ctx.send("Aaand done. All garbage has been disposed.")


#skips to next song
@katyusha.command()
async def skip(ctx):
    guild_id = ctx.guild.id
    vc = ctx.voice_client

    if vc and vc.is_playing():
        await ctx.send("Thank god! The purgatory is over!")
        vc.stop()
    else:
        await ctx.send("I wish there was something to skip.")
        


#bot will stop playing an audio if there is an audio playing
@katyusha.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        guild_id = ctx.guild.id
        if guild_id in queues:
            queues[guild_id].clear()
        ctx.voice_client.stop()
        await ctx.send("I didn't even want to play it anyways...")
    else:
        await ctx.send("Stop what you freak???")



#bot will leave if it is in a discord voice channel
@katyusha.command()
async def leave(ctx):
    if ctx.voice_client:
        guild_id = ctx.guild.id
        if guild_id in queues:
            queues[guild_id].clear()
        await ctx.voice_client.disconnect()
        await ctx.send("Just so you know, I'm just leaving because I want to")
    else:
        await ctx.send("Are you stupid? leave what?")



@katyusha.command()
async def m(ctx,*,message:str):
    server_id = ctx.guild.id if ctx.guild else "DM"
    username = ctx.author.display_name
    response = await talk(server_id=server_id, username=username, message=message, CONTEXT_PATH=context_env_path)
    await ctx.send(response)



print(token)
if token is None:
    raise ValueError("DISCORD_BOT_TOKEN enviroment variable is missing")
katyusha.run(token)