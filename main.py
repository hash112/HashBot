import discord
from discord.ext import commands

client = commands.Bot(command_prefix='$')

@client.event
async def inicio():
    print("Listo para chambear")
    print("-------------------------")

@client.command()
async def hola(ctx):
    await ctx.send("Hola mundo")

client.run('')