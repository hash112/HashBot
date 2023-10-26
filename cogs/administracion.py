import nextcord
from nextcord.ext import commands

class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def borrar(self, ctx, cantidad_borrar):
        try:
            cantidad_borrar = int(cantidad_borrar)
            await ctx.channel.purge(limit=cantidad_borrar+1)

        except:
            await ctx.send("Ingresa un número despues del comando")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def cmsg(self, ctx, *msg):
        await ctx.channel.purge(limit=1)
        await ctx.send(" ".join(msg))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def react(self, ctx):
        mensaje_comando = ctx.message.content.split()
        try:
            await ctx.channel.purge(limit=1)
            id_msg = int(mensaje_comando[1])
            message = await ctx.fetch_message(id_msg)
            await message.add_reaction(mensaje_comando[2])

        except:
            await ctx.send("Ingresa el ID del mensaje a reaccionar y el emoji")

    
def setup(client):
    client.add_cog(Admin(client))