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
        conn = psycopg2.connect(host=db.HOST, dbname=db.NAME, user=db.USER, password=db.PASSWORD, port=db.PORT)
        msg = await channel.send(f"{' '.join(msg)}")
        with conn.cursor() as cur:
            cur.execute("INSERT INTO role_msg (id_server, id_role_channel, id_role_msg) VALUES (%s, %s, %s);", [ctx.guild.id, channel.id, msg.id])
            conn.commit()

        conn.close()
        return
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setrolereact(self, ctx, role: nextcord.Role, emoji: nextcord.PartialEmoji, id_msg: int):    
        conn = psycopg2.connect(host=db.HOST, dbname=db.NAME, user=db.USER, password=db.PASSWORD, port=db.PORT)
        custom = emoji.is_custom_emoji()
        if custom:
            await ctx.send(f"No puedes utilizar emojis personalizados")
            return
        
        with conn.cursor() as cur:
            cur.execute("SELECT id_role_msg, id_role_channel FROM role_msg WHERE id_server = %s;", [ctx.guild.id])
            arr_msg = cur.fetchall()
            if not arr_msg:
                await ctx.send(f"No hay mensaje con ese id.")
                conn.close()
                return
            
            for i, id_fetch in enumerate(arr_msg):
                if id_msg in id_fetch:
                    cur.execute("SELECT emoji FROM roles WHERE id_role_msg = %s AND id_role = %s;", [id_msg, role.id])
                    emojifetch = cur.fetchone()
                    if emojifetch is None:
                        channel = await ctx.guild.fetch_channel(id_fetch[1])
                        msg = await channel.fetch_message(id_msg)
                        cur.execute("INSERT INTO roles (id_role_msg, id_role, emoji) VALUES (%s, %s, %s);", [id_msg, role.id, emoji.name])

                    else:
                        channel = await ctx.guild.fetch_channel(id_fetch[1])
                        msg = await channel.fetch_message(id_fetch[0])
                        await msg.remove_reaction(emojifetch[0], self.client.user)
                        cur.execute("UPDATE roles SET emoji = %s WHERE id_role_msg = %s AND id_role = %s;", [emoji.name, id_msg, role.id])

                    conn.commit()
                    await msg.add_reaction(emoji)

                else:
                    await ctx.send(f"No hay mensaje con ese id.")
                    conn.close()
                    return

        conn.close()
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
    async def emojid(self, ctx, emoji: nextcord.PartialEmoji):
        print(emoji)
        print(emoji.name)
        print(emoji.id)

    
def setup(client):
    client.add_cog(Admin(client))