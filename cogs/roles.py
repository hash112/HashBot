import nextcord
from nextcord.ext import commands

import psycopg2
from dotenv import dotenv_values

token = dotenv_values('.env.secret')

class Roles(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        conn = psycopg2.connect("Credentials")
        with conn.cursor() as cur:

            # Busca el emoji con el rol en relacion con el mensaje
            cur.execute("SELECT id_role, emoji FROM roles WHERE id_role_msg = %s;", [payload.message_id])
            data = cur.fetchone()
            if data is None:
                conn.close()
                return
            
            # Asigna el rol en caso de no tenerlo
            id_role, emoji = data
            if emoji == payload.emoji.name:
                role = payload.member.guild.get_role(id_role)
                if role not in payload.member.roles:
                    await payload.member.add_roles(role)

            conn.close()

def setup(client):
    client.add_cog(Roles(client))