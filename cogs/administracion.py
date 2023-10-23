import nextcord
from nextcord.ext import commands

from io import StringIO

class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command()
    async def borrar(self, ctx):
        mensaje = ctx.message.content.split()
        if ctx.author.top_role == ctx.guild.roles[4]:
            try:
                cantidad_borrar = int(mensaje[1])
                await ctx.channel.purge(limit=cantidad_borrar+1)

            except:
                await ctx.send("Ingresa un número despues del comando")

    @commands.command()
    async def cmsg(self, ctx):
        custom = StringIO()
        mensaje = ctx.message.content.split()
        if ctx.author.top_role == "Admin":
            for i, msg in enumerate(mensaje):
                if i > 0: custom.write(f"{msg} ")

            await ctx.channel.purge(limit=1)
            await ctx.send(custom.getvalue())

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