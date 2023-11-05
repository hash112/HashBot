import nextcord
from nextcord.ext import commands
import api_secret as db
import psycopg2

class Roles(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        conn = psycopg2.connect(host=db.HOST, dbname=db.NAME, user=db.USER, password=db.PASSWORD, port=db.PORT)
        with conn.cursor() as cur:
            cur.execute("SELECT id_role, emoji FROM roles WHERE id_role_msg = %s;", [payload.message_id])
            data = cur.fetchone()
            if data is None:
                conn.close()
                return
            
            id_role, emoji = data
            if emoji == payload.emoji.name:
                role = payload.member.guild.get_role(id_role)
                if role not in payload.member.roles:
                    await payload.member.add_roles(role)

            conn.close()

def setup(client):
    client.add_cog(Roles(client))