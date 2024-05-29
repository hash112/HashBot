import nextcord
from nextcord.ext import commands

import psycopg2
from dotenv import dotenv_values

token = dotenv_values('.env.secret')

class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcome(self, ctx, channel: nextcord.TextChannel, *msg):
        conn = psycopg2.connect("Credentials");
        msg = " ".join(msg)
        with conn.cursor() as cur:

            # Crea un mensaje de bienvenida para cuando alguien se une al server
            cur.execute("SELECT id_server FROM greeting WHERE id_server = %s;", [ctx.guild.id])
            if cur.fetchone() is None: 
                cur.execute("INSERT INTO greeting (id_server, id_welcome_chnnl, msg_welcome) VALUES(%s, %s, %s);", [ctx.guild.id, channel.id, msg])
                await ctx.send(f"Se ha creado el mensaje de bienvenida del canal <#{channel.id}>")
            
            # O lo actualiza si ya existe uno
            else: 
                cur.execute("UPDATE greeting SET id_welcome_chnnl = %s, msg_welcome = %s WHERE id_server = %s;", [channel.id, msg, ctx.guild.id])
                await ctx.send(f"Se ha cambiado el mensaje de bienvenida del canal <#{channel.id}>")

            conn.commit()

        conn.close()
        return
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setfarewell(self, ctx, channel: nextcord.TextChannel, *msg):
        conn = psycopg2.connect("Credentials")
        msg = " ".join(msg)
        with conn.cursor() as cur:

            # Lo mismo que las bienvenidas
            cur.execute("SELECT id_server FROM greeting WHERE id_server = %s;", [ctx.guild.id])
            if cur.fetchone() is None: 
                cur.execute("INSERT INTO greeting (id_server, id_farewell_chnnl, msg_farewell) VALUES(%s, %s, %s);", [ctx.guild.id, channel.id, msg])
                await ctx.send(f"Se ha creado el mensaje de despedida del canal <#{channel.id}>")

            else: 
                cur.execute("UPDATE greeting SET id_farewell_chnnl = %s, msg_farewell = %s WHERE id_server = %s;", [channel.id, msg, ctx.guild.id])
                await ctx.send(f"Se ha cambiado el mensaje de despedida del canal <#{channel.id}>")

            conn.commit()

        conn.close()
        return
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setrolemsg(self, ctx, channel: nextcord.TextChannel, *msg):
        conn = psycopg2.connect("Credentials")
        msg = await channel.send(f"{' '.join(msg)}")
        with conn.cursor() as cur:

            # Permite crear varios mensajes de roles
            cur.execute("INSERT INTO role_msg (id_server, id_role_channel, id_role_msg) VALUES (%s, %s, %s);", [ctx.guild.id, channel.id, msg.id])
            conn.commit()
            await ctx.send(f"Se ha agregado un nuevo mensaje a <#{channel.id}>")

        conn.close()
        return
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setrolereact(self, ctx, role: nextcord.Role, emoji: nextcord.PartialEmoji, id_msg: int):    
        conn = psycopg2.connect("Credentials")
        custom = emoji.is_custom_emoji()
        if custom:
            await ctx.send(f"No puedes utilizar emojis personalizados")
            return
        
        with conn.cursor() as cur:

            #Busca un array de mensajes, en caso de que haya mas de un emoji or rol
            cur.execute("SELECT id_role_msg, id_role_channel FROM role_msg WHERE id_server = %s;", [ctx.guild.id])
            arr_msg = cur.fetchall()
            if not arr_msg:
                await ctx.send(f"No hay mensaje con ese id.")
                conn.close()
                return
            
            #Recorre el array de mensajes encontrados en el servidor
            for i, id_fetch in enumerate(arr_msg):
                if id_msg in id_fetch:

                    #Seleciiona el emoji del rol que queremos usar
                    cur.execute("SELECT emoji FROM roles WHERE id_role_msg = %s AND id_role = %s;", [id_msg, role.id])

                    #en el array [0] es el canal, [1] es el mensaje
                    id_channel = id_fetch[0]
                    id_msg_fetch = id_fetch[1]
                    emojifetch = cur.fetchone()
                    if emojifetch is None:
                        channel = await ctx.guild.fetch_channel(id_msg_fetch)
                        msg = await channel.fetch_message(id_msg)
                        cur.execute("INSERT INTO roles (id_role_msg, id_role, emoji) VALUES (%s, %s, %s);", [id_msg, role.id, emoji.name])
                        await ctx.send(f"Se ha agregado {emoji.name} para el rol <@{role.name}> en el mensaje del canal <#{id_channel}>")

                    else:
                        channel = await ctx.guild.fetch_channel(id_channel)
                        msg = await channel.fetch_message(id_msg_fetch)
                        await msg.remove_reaction(*emojifetch, self.client.user)
                        cur.execute("UPDATE roles SET emoji = %s WHERE id_role_msg = %s AND id_role = %s;", [emoji.name, id_msg, role.id])
                        await ctx.send(f"Se ha actualizado {emoji.name} para el rol {role.name} en el mensaje del canal <#{id_channel}>")

                    conn.commit()
                    await msg.add_reaction(emoji)

        conn.close()
        return

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, cantidad_borrar: int):

        # Borra los mensajes que le pidas de un canal
        cantidad_borrar = cantidad_borrar
        await ctx.channel.purge(limit=cantidad_borrar+1)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def fclear(self, ctx):

        # Borra rapidamente 25
        await ctx.channel.purge(limit=25)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def cmsg(self, ctx, *msg):

        # Mensaje customizado
        await ctx.channel.purge(limit=1)
        await ctx.send(" ".join(msg))
    
    @setwelcome.error
    @setfarewell.error
    @fclear.error
    @clear.error
    @setrolemsg.error
    @setrolereact.error
    @cmsg.error
    async def errors(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Error: no permisos de administrador")

        elif(isinstance(error, commands.BadArgument)):
            print("Argumentos inválidos")
        
        elif(isinstance(error, ValueError)):
            print("Argumentos inválidos")
        
        return 1

def setup(client):
    client.add_cog(Admin(client))
