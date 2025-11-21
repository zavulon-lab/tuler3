from discord.ext import commands
from discord import Intents

GUILD_ID = 1421879715081224304 

intents = Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Загружаем handlers.py
import handlers
