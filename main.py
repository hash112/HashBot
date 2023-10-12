# Importar las librerias de discord
import discord
from discord.ext import commands

# Importar el token de un archivo por separado
from apikeys import Token

intents = discord.Intents.all()
client = commands.Bot(command_prefix = '$', intents=intents)

@client.event
async def on_ready():
    print("Bot inicializado")
    print("-------------------------")

@client.command()
async def hola(ctx):
    await ctx.send("Hola mundo")

@client.event
async def on_member_join(miembro):
    canal = client.get_channel(1161591714193096715)
    await canal.send(f"Bienvenido/a {miembro.mention} :)")

@client.event
async def on_member_remove(miembro):
    canal = client.get_channel(1161591714193096715)
    await canal.send(f"Adios {miembro.mention}")

client.run(Token())