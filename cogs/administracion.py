import nextcord
from nextcord.ext import commands
import psycopg2
import api_secret as db

class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcome(self, ctx, channel: nextcord.TextChannel, *msg):
        conn = psycopg2.connect(host=db.HOST, dbname=db.NAME, user=db.USER, password=db.PASSWORD, port=db.PORT)
        msg = " ".join(msg)
        with conn.cursor() as cur:
            cur.execute("SELECT id_server FROM greeting WHERE id_server = %s;", [ctx.guild.id])
            if cur.fetchone() is None: cur.execute("INSERT INTO greeting (id_server, id_welcome_chnnl, msg_welcome) VALUES(%s, %s, %s);", [ctx.guild.id, channel.id, msg])
            else: cur.execute("UPDATE greeting SET id_welcome_chnnl = %s, msg_welcome = %s WHERE id_server = %s;", [channel.id, msg, ctx.guild.id])
            conn.commit()

        conn.close()
        return
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setfarewell(self, ctx, channel: nextcord.TextChannel, *msg):
        conn = psycopg2.connect(host=db.HOST, dbname=db.NAME, user=db.USER, password=db.PASSWORD, port=db.PORT)
        msg = " ".join(msg)
        with conn.cursor() as cur:
            cur.execute("SELECT id_server FROM greeting WHERE id_server = %s;", [ctx.guild.id])
            if cur.fetchone() is None: cur.execute("INSERT INTO greeting (id_server, id_farewell_chnnl, msg_farewell) VALUES(%s, %s, %s);", [ctx.guild.id, channel.id, msg])
            else: cur.execute("UPDATE greeting SET id_farewell_chnnl = %s, msg_farewell = %s WHERE id_server = %s;", [channel.id, msg, ctx.guild.id])
            conn.commit()

        conn.close()
        return
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setrolemsg(self, ctx, channel: nextcord.TextChannel, *msg):
        return
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setrolereact(self, ctx, role: nextcord.Role, emoji):
        print(role.id)
        print(emoji)
        return

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, cantidad_borrar):
        try:
            cantidad_borrar = int(cantidad_borrar)
            await ctx.channel.purge(limit=cantidad_borrar+1)

        except:
            await ctx.send("Ingresa un número despues del comando")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def fclear(self, ctx):
        await ctx.channel.purge(limit=25)

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