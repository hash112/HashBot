import nextcord
from nextcord.ext import commands

import psycopg2
from dotenv import dotenv_values

token = dotenv_values('.env.secret')

def getMessage(msg, member_id): # Esta función sirve para buscar menciones personalizadas dentro del mensaje.
    custom_mention = False
    msg = msg.split()
    for i, word in enumerate(msg):
        if word == "<@>":
            msg[i] = f"<@{member_id}>"
            custom_mention = True

    if not custom_mention: msg.append(f"<@{member_id}>") # Si no hay mención dentro del mensaje, la coloca al final
    msg = " ".join(msg)
    return msg

class Saludos(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def hola(self, ctx): # Comando basico de saludo
        await ctx.send(f"Hola {ctx.author.mention}")
        return

    @commands.Cog.listener() 
    async def on_member_join(self, member): # Mensaje cuando alguien se une al server (si hay)
        conn = psycopg2.connect("Credentials")
        with conn.cursor() as cur:
            cur.execute("SELECT id_welcome_chnnl, msg_welcome FROM greeting WHERE id_server = %s;", [member.guild.id])
            msg = cur.fetchone()
            if msg is None: 
                conn.close()
                return
            
            else:
                id_channel, welcome_msg = msg
                channel = await self.client.fetch_channel(id_channel)
                msg = getMessage(welcome_msg, member.id)
                await channel.send(msg)
                
        conn.close()
        return

    @commands.Cog.listener()
    async def on_member_remove(self, member): # Mensaje cuando alguien se va de server (si hay)
        conn = psycopg2.connect("Credentials")
        with conn.cursor() as cur:
            cur.execute("SELECT id_farewell_chnnl, msg_farewell FROM greeting WHERE id_server = %s;", [member.guild.id])
            msg = cur.fetchone()
            if msg is None: 
                conn.close()
                return
            
            else:
                id_channel, welcome_msg = msg
                channel = await self.client.fetch_channel(id_channel)
                msg = getMessage(welcome_msg, member.id)
                await channel.send(msg)
                
        conn.close()
        return
    
def setup(client):
    client.add_cog(Saludos(client))