## ClassifiedHamBot

import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
import os

# Load environment variables
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Connect to database

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

# Add Alert
@bot.tree.command(name="addtracker", description="Add tracker for an item.", guild=GUILD_ID)
async def addtracker(interaction: discord.Interaction, key: str):
    print('Adding new tracker')
    # Do some database stuff here
    
    # Print a message to chat or send through DM?
    await interaction.user.send("This is a DM")
    # await interaction.response.send_message(f"Added a tracker for \"{key}\", {interaction.user.mention}")
    
# Remove Alert
@bot.tree.command(name="deltracker", description="Delete a tracker.", guild=GUILD_ID)
async def deltracker(interaction: discord.Interaction, key: str):
    print('Removing tracker')
    # Do some database stuff here
    
    await interaction.response.send_message(f"Removing tracker for \"{key}\", {interaction.user.mention}")

# List Alert(s)
@bot.tree.command(name="listtrackers", description="List current trackers for a user.", guild=GUILD_ID)
async def listtrackers(interaction: discord.Interaction):
    print(f'Listing all trackers for {interaction.user.name}')
    # Get all trackers for calling user
    
    await interaction.response.send_message(f"Currently tracking:, {interaction.user.mention}")
    
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