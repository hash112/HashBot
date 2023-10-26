import nextcord
from nextcord.ext import commands

import random # Para tener turnos aleatorios

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
        if p2 == ctx.author:
            await ctx.send(f"No te puedes retar a ti mismo")
            return

        if p2 == self.client.user:
            await ctx.send(f"No puedes retarme (aún)")
            return
        
        global player1, player2
        global p1_score, p2_score
        global turn, n_turn
        global isOver
        player1 = ctx.author
        player2 = p2
        p1_score = []
        p2_score = []
        turn = random.randint(0, 1)
        if turn:
            turn = player1

        else:
            turn = player2

        n_turn = 1
        isOver = False
        board = print_hash(p1_score, p2_score)
        await ctx.send(f"{board[0]}{board[1]}{board[2]}\n{board[3]}{board[4]}{board[5]}\n{board[6]}{board[7]}{board[8]}")
        await ctx.send(f"Turno de {turn.mention}")
        return
         
    @commands.command()
    async def place(self, ctx, pos):
        try:
            global turn, n_turn
            global p1_score, p2_score
            global isOver
            if isOver:
                await ctx.send(f"Debes iniciar un juego nuevo o esperar a que el otro acabe")
                return
            
            pos = int(pos)
            if ctx.author == turn:
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
                        return
                else:
                    await ctx.send(f"Asegurate de poner un entero entre 1 y 9")
                    return
                
                board = print_hash(p1_score, p2_score) 
                await ctx.send(f"{board[0]}{board[1]}{board[2]}\n{board[3]}{board[4]}{board[5]}\n{board[6]}{board[7]}{board[8]}")
                if 4 < n_turn: # Aqui ya empieza a checar si algun jugador gano
                    p1_score.sort()
                    p1_win = check_win(p1_score)
                    if p1_win:
                        board = print_hash(p1_score, p2_score)
                        await ctx.send(f"Ganó {player1.mention}")
                        isOver = True
                        return 

                    p2_score.sort()
                    p2_win = check_win(p2_score)
                    if p2_win:
                        await ctx.send(f"Ganó {player2.mention}")
                        isOver = True
                        return 
                    
                if n_turn == 9: # Si nadie gana
                    board = print_hash(p1_score, p2_score)
                    await ctx.send(f"Nadie ganó jaja")
                    isOver = True
                    return
                
                await ctx.send(f"Turno de {turn.mention}")
                n_turn += 1
                return
            
            else:
                await ctx.send(f"No es tu turno o no estás jugando")
                return

        except:
            await ctx.send(f"Por favor ingresa un número")

    @commands.command()
    async def cancel(self, ctx): # Comando para cancelar un juego, solo aplica si es turno del que lo invoca
        global isOver
        if turn == ctx.author:
            await ctx.send(f"{ctx.author.mention} canceló la partida :(")
            isOver = True

        else:
            await ctx.send(f"No tienes permiso de cancelar una partida.")

def setup(client):
    client.add_cog(TicTac(client))