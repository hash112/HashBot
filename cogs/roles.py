import nextcord
from nextcord.ext import commands

class Roles(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.role_message_id = 1164052200604061740
        self.emoji_name = "✅"
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        role = nextcord.utils.get(payload.member.guild.roles, name="Miembro")
        if payload.message_id == self.role_message_id and payload.emoji.name == self.emoji_name:
            if role not in payload.member.roles:
                await payload.member.add_roles(role)

            channel = self.client.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if payload.member != self.client.user:
                await message.remove_reaction(payload.emoji, payload.member)


def setup(client):
    client.add_cog(Roles(client))