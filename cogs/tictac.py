import nextcord
from nextcord.ext import commands

import random # Para tener turnos aleatorios
import math

import psycopg2 
from dotenv import dotenv_values

token = dotenv_values('.env.secret')

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
        conn = psycopg2.connect("Credentials")
        if p2 == ctx.author:
            await ctx.send(f"No te puedes retar a ti mismo")
            return

        if p2 == self.client.user: # Me gustaría agregar una IA básica
            await ctx.send(f"No puedes retarme (aún)")
            return
        
        player1 = ctx.author
        player2 = p2
        juego = math.floor((ctx.author.id * p2.id) / ctx.guild.id)
        turn = random.randint(0, 1)
        if turn: turn = player1.id
        else: turn = player2.id 
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tictac where id_game = %s;", [juego]) 
            isOver = cur.fetchone()
            if isOver is None: # Busca una entrada en la base que coincida con el server, si no hay, no hay partida en curso
                cur.execute("""INSERT INTO tictac 
                            (id_player1, 
                            id_player2, 
                            n_turn, 
                            who_turn,
                            p1_score,
                            p2_score,
                            id_server,
                            id_game) 
                            VALUES (%s, %s, 1, %s, %s, %s, %s, %s);
                            """, [player1.id, player2.id, turn, [], [], ctx.guild.id, juego])

            else:
                await ctx.send(f"Hay una partida en curso")
                conn.close()
                return
            
            conn.commit()

        conn.close()
        board = print_hash([], [])
        await ctx.send(f"{board[0]}{board[1]}{board[2]}\n{board[3]}{board[4]}{board[5]}\n{board[6]}{board[7]}{board[8]}")
        await ctx.send(f"Turno de <@{turn}>")
        return

    @commands.command()
    async def place(self, ctx, pos: int, p2: nextcord.Member): # Coloca una marca donde indique el usuario
        juego = math.floor((ctx.author.id * p2.id) / ctx.guild.id)
        conn = psycopg2.connect("Credentials")
        with conn.cursor() as cur:
            cur.execute("SELECT id_player1, id_player2, n_turn, who_turn, p1_score, p2_score FROM tictac WHERE id_game = %s;", [juego])
            data = cur.fetchone()
            if data is None: # Si no hay datos, no hay partida
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
                        board = print_hash(p1_score, p2_score)
                        await ctx.send(f"Ganó <@{player1}>")
                        cur.execute("DELETE FROM tictac WHERE id_game = %s", [juego])
                        conn.commit()
                        conn.close()
                        return 

                    p2_score.sort()
                    p2_win = check_win(p2_score)
                    if p2_win:
                        await ctx.send(f"Ganó <@{player2}>")
                        cur.execute("DELETE FROM tictac WHERE id_game = %s", [juego])
                        conn.commit()
                        conn.close()
                        return 
                    
                if n_turn == 9: # Si nadie gana
                    board = print_hash(p1_score, p2_score)
                    await ctx.send(f"Nadie ganó jaja")
                    cur.execute("DELETE FROM tictac WHERE id_game = %s", [juego])
                    conn.close()
                    return
                
                await ctx.send(f"Turno de <@{turn}>")
                n_turn += 1
                cur.execute("UPDATE tictac SET n_turn = %s, who_turn = %s, p1_score = %s, p2_score = %s WHERE id_game = %s;", 
                            [n_turn, turn, p1_score, p2_score, juego])
                conn.commit()
                conn.close()
                return
            
            else:
                await ctx.send(f"No es tu turno o no estás jugando")
                return

    @commands.command()
    async def cancel(self, ctx, p2: nextcord.Member): # Comando para cancelar un juego, solo aplica si eres uno de los jugadores
        conn = psycopg2.connect("Credentials")
        juego = math.floor((ctx.author.id * p2.id) / ctx.guild.id)
        with conn.cursor() as cur:
            cur.execute("SELECT id_player1, id_player2 FROM tictac WHERE id_game = %s;", [juego])
            turn = cur.fetchone()
            if turn is None:
                await ctx.send(f"No hay partida en curso.")
                conn.close()
                return
        
            if turn[0] == ctx.author.id or turn[1] == ctx.author.id:
                cur.execute("DELETE FROM tictac WHERE id_game = %s", [juego])
                conn.commit()
                await ctx.send(f"{ctx.author.mention} canceló la partida :(")

            else: await ctx.send(f"No tienes permiso de cancelar una partida.")

        conn.close()

    @commands.command()
    async def phash(self, ctx, p2: nextcord.Member): # Reimprime el tablero en caso de haberse perdido
        con = psycopg2.connect("Credentials")
        juego = math.floor((ctx.author.id * p2.id) / ctx.guild.id)
        with con.cursor() as cur:
            cur.execute("SELECT p1_score, p2_score, turn, FROM tictac WHERE id_game = %s", [juego])
            data = cur.fetchone()
            if data is None: # Si no hay datos, no hay partida
                await ctx.send("No hay partida en curso");
                con.close();
                return

            p1_score, p2_score, turno = data
            board = print_hash(p1_score, p2_score)
            con.close();
            await ctx.send(f"{board[0]}{board[1]}{board[2]}\n{board[3]}{board[4]}{board[5]}\n{board[6]}{board[7]}{board[8]}")
            await ctx.send(f"Turno de <@{turno}>")
            return

    @tictac.error
    @place.error
    @cancel.error
    @phash.error
    async def bad_arguments(self, ctx, error):
        if(isinstance(error, commands.BadArgument)):
            await ctx.send("Argumentos inválidos")
        
        elif(isinstance(error, ValueError)):
            await ctx.send("Argumentos inválidos")
        
        return 1

def setup(client):
    client.add_cog(TicTac(client))
