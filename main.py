# Importar las librerias de nextcord
import nextcord
from nextcord.ext import commands
import os

# Importar el token de un archivo por separado
from api_secret import BOTTOKEN

import datetime

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix = '$', intents=intents)

@client.event
async def on_ready():
    print("----------------------------[LOG]----------------------------")
    print(f"[{datetime.datetime.now()}] Bot inicializado como {client.user}")
    return

extensiones = [f"cogs.{filename[:-3]}" for filename in os.listdir('./cogs') if filename.endswith(".py")]
if __name__ == '__main__':
    for archivo in extensiones:
        client.load_extension(archivo)

client.run(BOTTOKEN)