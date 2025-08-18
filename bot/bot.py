## ClassifiedHamBot

import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
import os
import requests
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# API url
API_URL = 'http://api:8000'

# Set up logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Define intents for the bot
intents = discord.Intents.default()
intents.message_content = True

# Initialize the bot
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    try:
        guild = discord.Object(id=1391854912505254130)
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} commands to guild {guild.id}")
    except Exception as e:
        print(f'Error syncing commands: {e}')
        
    print(f'{bot.user.name} is ready to go!')

@bot.event
async def on_message(message):
    # Don't reply to its own messages
    if message.author == bot.user:
        return
    print(f"{message}")

GUILD_ID = discord.Object(id=1391854912505254130)

# Add Tracker
@bot.tree.command(name="addtracker", description="Add tracker for an item.", guild=GUILD_ID)
async def addtracker(interaction: discord.Interaction, item_name: str):
    print('Adding new tracker')
    # Do some database stuff here
    response = requests.post(f'{API_URL}/trackers?uname={interaction.user.name}&iname={quote_plus(item_name)}')
    if response.status_code == 201:
        await interaction.response.send_message(f'Added tracker for {item_name}, {interaction.user.mention}')
    elif response.status_code == 409:
        await interaction.response.send_message(f'A tracker for {item_name} already exists, {interaction.user.mention}')
    # await interaction.response.send_message(f"Added a tracker for \"{key}\", {interaction.user.mention}")
    
# Remove Tracker
@bot.tree.command(name="deltracker", description="Delete a tracker.", guild=GUILD_ID)
async def deltracker(interaction: discord.Interaction, id: str):
    print('Removing tracker')
    # Do some database stuff here
    response = requests.delete(f'{API_URL}/trackers?uname={interaction.user.name}&id={id}')
    if response.status_code == 200:
        await interaction.response.send_message(f"Removing tracker {id}")
    elif response.status_code == 404:
        await interaction.response.send_message(f"Could not find tracker with id: {id}")

# List Tracker(s)
@bot.tree.command(name="listtrackers", description="List current trackers for a user.", guild=GUILD_ID)
async def listtrackers(interaction: discord.Interaction):
    print(f'Listing all trackers for {interaction.user.name}')
    # Get all trackers for calling user
    response = requests.get(f'{API_URL}/trackers?uname={interaction.user.name}')
    await interaction.response.send_message(f"Trackers for {interaction.user.mention}:\n" + 'Id  |  Item Name\n' + '\n'.join(f'{x[0]}  |  {x[2]}' for x in response.json()))
    
# Help?
@bot.tree.command(name="trackerhelp", description="A test slash command", guild=GUILD_ID)
async def help(interaction: discord.Interaction):
    print('Listing all commands.')
    await interaction.response.send_message(f"")
    
@bot.tree.command(name="blah", description="A test slash command", guild=GUILD_ID)
async def test(interaction: discord.Interaction):
    print('Testing')
    await interaction.response.send_message(f"This is a test, {interaction.user.mention}")
    
bot.run(token=token, log_handler=handler, log_level=logging.DEBUG)