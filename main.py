# Importar las librerias de nextcord
import nextcord
from nextcord.ext import commands
import os

# Importar el token de un archivo por separado
from apikeys import Token

# Uso de json (Aun por implementar)
import json

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix = '$', intents=intents)

@client.event
async def on_ready():
    print(f"Bot inicializado como {client.user}")
    print("------------------------------------")
    return

extensiones = [f"cogs.{filename[:-3]}" for filename in os.listdir('./cogs') if filename.endswith(".py")]
if __name__ == '__main__':
    for archivo in extensiones:
        client.load_extension(archivo)

client.run(Token())