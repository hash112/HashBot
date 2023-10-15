import nextcord
from nextcord.ext import commands

class Saludos(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def hola(self, ctx): # Comando basico de saludo
        await ctx.send(f"Hola {ctx.author.mention}")
        return

    @commands.Cog.listener()
    async def on_member_join(self, miembro):
        canal = miembro.guild.get_channel(1161591714193096715)
        await canal.send(f"Bienvenido/a {miembro.mention} :)")
        return

    @commands.Cog.listener()
    async def on_member_remove(self, miembro):
        canal = miembro.guild.get_channel(1161591714193096715)
        await canal.send(f"Adios {miembro.mention}")
        return
    
def setup(client):
    client.add_cog(Saludos(client))