import nextcord
from nextcord.ext import commands

class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_reaction_add(self, reaccion, miembro):
        canal = miembro.guild.get_channel(1162480936387084339)
        await canal.send(f"{miembro.mention} reacciono al mensaje de {reaccion.message.author.mention} con {reaccion.emoji}")
        return
    
def setup(client):
    client.add_cog(Admin(client))