import nextcord
from nextcord.ext import commands

import random # Para tener turnos aleatorios

import psycopg2

import api_secret as db



isOver = True # Variable que nos indica si hay una partida en progreso

def print_hash(p1_score, p2_score):
    board = ["⬜" for space in range(9)] # Crea un espacio en blanco
    for mark in range(len(board)): # Rellena los espacios en blanco dependiendo de las marcas de los jugadores
        if mark in p1_score:
            board[mark] = "❌"

        elif mark in p2_score:
            board[mark] = "⭕"
            
    return board

def separate_results(score): # Esta funcion separa los resultados en caso de que haya mas de 3 marcas en la partida
    results = []
    for diff in range(len(score)): # Crea una lista para cada una de las posibles combinaciones para ganar
        temp = []
        for i, number in enumerate(score):
            if diff != i:
                temp.append(number)

        results.append(temp)

    if len(score) == 5: # Si por alguna razon hay 5 marcas de un jugador, las separa en varias listas de 3
        score = results
        results = []
        for arr in score:
            temp = separate_results(arr)
            for temp_arr in temp:
                if temp_arr not in results:
                    results.append(temp_arr)

    return results

def check_win(score): # Checa si algun jugador tiene una combinacion ganadora
    condition = [
        [0, 1, 2],
        [0, 3, 6],
        [0, 4, 8],
        [1, 4, 7],
        [2, 4, 6],
        [2, 5, 8],
        [3, 4, 5],
        [6, 7, 8]
    ]

    if len(score) > 3: # Si hay 4 marcas, invoca a la funcion que las separa y compara las listas que genere
        score = separate_results(score)
        for arr in score:
            if arr in condition:
                return True
            
    else: # Compara si una lista esta en una de las combinaciones para ganar
        if score in condition:
            return True
        
    return False

class TicTac(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def tictac(self, ctx, p2: nextcord.Member): # Genera un nuevo juego
        conn = psycopg2.connect(host=db.HOST, dbname=db.NAME, user=db.USER, password=db.PASSWORD, port=db.PORT)
        if p2 == ctx.author:
            await ctx.send(f"No te puedes retar a ti mismo")
            return

        if p2 == self.client.user:
            await ctx.send(f"No puedes retarme (aún)")
            return
        
        player1 = ctx.author
        player2 = p2
        turn = random.randint(0, 1)
        if turn:
            turn = player1.id

        else:
            turn = player2.id

        score = [player1.id, player2.id, turn, [], [], ctx.guild.id]
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tictac where id_server = %s;", [ctx.guild.id])
            isOver = cur.fetchone()
            if isOver is None:
                cur.execute("""INSERT INTO tictac 
                            (id_player1, 
                            id_player2, 
                            n_turn, 
                            who_turn,
                            p1_score,
                            p2_score,
                            id_server) 
                            VALUES (%s, %s, 1, %s, %s, %s, %s);
                            """, score)

            else:
                await ctx.send(f"Hay una partida en curso")
                conn.close()
                return
            
            conn.commit()

        conn.close()
        board = print_hash([], [])
        await ctx.send(f"{board[0]}{board[1]}{board[2]}\n{board[3]}{board[4]}{board[5]}\n{board[6]}{board[7]}{board[8]}")
        m_turno = self.client.get_user(turn)
        await ctx.send(f"Turno de {m_turno.mention}")
        return
         
    @commands.command()
    async def place(self, ctx, pos):
        try:
            pos = int(pos)

        except:
            await ctx.send(f"Por favor ingresa un número")
            return

        conn = psycopg2.connect(host=db.HOST, dbname=db.NAME, user=db.USER, password=db.PASSWORD, port=db.PORT)
        with conn.cursor() as cur:
            cur.execute("SELECT id_player1, id_player2, n_turn, who_turn, p1_score, p2_score FROM tictac WHERE id_server = %s;", [ctx.guild.id])
            data = cur.fetchone()
            if data is None:
                await ctx.send(f"Debes iniciar un juego nuevo")
                conn.close()
                return

            player1, player2, n_turn, turn, p1_score, p2_score = data
            if ctx.author.id == turn:
                if 0 < pos < 10: # Filtra los input para que el usuario no haga cosas raras
                    if pos-1 not in p1_score and pos-1 not in p2_score:
                        if turn == player1: # Agrega la posicion a la lista de las marcas de cada jugador
                            p1_score.append(pos-1)
                            turn = player2

                        elif turn == player2:
                            p2_score.append(pos-1)
                            turn = player1

                    else:
                        await ctx.send(f"Esa casilla ya está marcada")
                        conn.close()
                        return
                else:
                    await ctx.send(f"Asegurate de poner un entero entre 1 y 9")
                    conn.close()
                    return
                
                board = print_hash(p1_score, p2_score) 
                await ctx.send(f"{board[0]}{board[1]}{board[2]}\n{board[3]}{board[4]}{board[5]}\n{board[6]}{board[7]}{board[8]}")
                if 4 < n_turn: # Aqui ya empieza a checar si algun jugador gano
                    p1_score.sort()
                    p1_win = check_win(p1_score)
                    if p1_win:
                        winner = self.client.get_user(player1)
                        board = print_hash(p1_score, p2_score)
                        await ctx.send(f"Ganó {winner.mention}")
                        cur.execute("DELETE FROM tictac WHERE id_server = %s", [ctx.guild.id])
                        conn.commit()
                        conn.close()
                        return 

                    p2_score.sort()
                    p2_win = check_win(p2_score)
                    if p2_win:
                        winner = self.client.get_user(player2)
                        await ctx.send(f"Ganó {winner.mention}")
                        cur.execute("DELETE FROM tictac WHERE id_server = %s", [ctx.guild.id])
                        conn.commit()
                        conn.close()
                        return 
                    
                if n_turn == 9: # Si nadie gana
                    board = print_hash(p1_score, p2_score)
                    await ctx.send(f"Nadie ganó jaja")
                    cur.execute("DELETE FROM tictac WHERE id_server = %s", [ctx.guild.id])
                    conn.close()
                    return
                
                player = self.client.get_user(turn)
                await ctx.send(f"Turno de {player.mention}")
                n_turn += 1
                cur.execute("UPDATE tictac SET n_turn = %s, who_turn = %s, p1_score = %s, p2_score = %s WHERE id_server = %s;", [n_turn, turn, p1_score, p2_score, ctx.guild.id])
                conn.commit()
                conn.close()
                return
            
            else:
                await ctx.send(f"No es tu turno o no estás jugando")
                return

    @commands.command()
    async def cancel(self, ctx): # Comando para cancelar un juego, solo aplica si es turno del que lo invoca
        conn = psycopg2.connect(host=db.HOST, dbname=db.NAME, user=db.USER, password=db.PASSWORD, port=db.PORT)
        with conn.cursor() as cur:
            cur.execute("SELECT who_turn FROM tictac WHERE id_server = %s;", [ctx.guild.id])
            turn = cur.fetchone()
            if turn is None:
                await ctx.send(f"No hay partida en curso.")
                conn.close()
                return
        
            if turn[0] == ctx.author.id:
                cur.execute("DELETE FROM tictac WHERE id_server = %s", [ctx.guild.id])
                await ctx.send(f"{ctx.author.mention} canceló la partida :(")

            else:
                await ctx.send(f"No tienes permiso de cancelar una partida.")

            conn.commit()

        conn.close()

def setup(client):
    client.add_cog(TicTac(client))