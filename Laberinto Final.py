import random
import os
import time
import tkinter as tk
from tkinter import ttk

class Window:
    def __init__(self, size):
        self.root = tk.Tk()
        self.root.title("Laberinto")
        #Ventana y recuadro
        self.table_frame = ttk.Frame(self.root)
        self.table_frame.grid(row=0, column=0)

        #Genera el laberinto
        self.laberinto = generate(size)
        #Tamaño del laberinto expandido
        self.size = len(self.laberinto)
        #Arreglo para las celdas
        self.maze = [[None for _ in range(self.size+2)] for _ in range(self.size+2)]

        #LLena la pantalla de celdas azules, cubre el tamaño del laberinto + marco de una casilla
        for row in range(self.size+2):
            for col in range(self.size+2):
                self.maze[row][col] = tk.Label(self.table_frame, height=2, width=4, bg="#0000FF")
                self.maze[row][col].grid(row=row, column=col)

        #Interpreta el laberinto en la pantalla
        self.transcribeMaze(self.laberinto)

        #Inicia la solución del laberinto después de 1 segundo
        self.root.after(1000, lambda: resolver_laberinto_dp(self.laberinto, self.drawRoute))

        #Carga la pantalla
        self.root.mainloop()

    #Modifica el color de las celdas según el contenido del laberinto
    def transcribeMaze(self, maze):
        for row in range(self.size):
            for col in range(self.size):
                # Pared: Azul, Meta: Blanco, Pregunta: Rojo, Pasillo: Negro
                color = {1: "#0000FF", 2: "#FFFFF8", 0: "#000000", 5: "#FF0000"}.get(maze[row][col], "#000000")
                self.maze[row + 1][col + 1].config(bg=color)
        # Actualiza la ventana gráfica para asegurar que los cambios se reflejen
        self.root.update_idletasks()


    #Cambia el color de la celda seleccionada (La ruta para resolver el laberinto)
    def drawRoute(self, x, y):
        if self.laberinto[x][y] == 5:
            self.maze[x+1][y+1].config(bg="#FF0000")
        else:
            self.maze[x+1][y+1].config(bg="#FFFF00")
            self.root.update_idletasks()

# Generación del laberinto###########################################################################################

DIRECTIONS = {'v': (0, 1), '^': (0, -1), '>': (1, 0), '<': (-1, 0), 'n': (0, 0)}
LETTERS = ('^', 'v', '<', '>')

#Verifica si la dirección elegida es válida
def is_valid(dir, pos, maze):
    #El origen no es válido
    if dir == 'n':
        return False
    #La nueva posición debe estar dentro del laberinto
    newPos = [pos[0]+DIRECTIONS[dir][1], pos[1]+DIRECTIONS[dir][0]]
    if newPos[0] < 0 or newPos[1] < 0:
        return False
    if newPos[0] >= len(maze) or newPos[1] >= len(maze):
        return False
    return True

#Genera un laberinto base con el origen en la esquina superior izquierda
#La primera columna apunta hacia arriba
#El resto del laberinto apunta a la izquierda
def baseMaze(size):
    #Apunta todo a la izquierda
    maze = [['<' for _ in range(size)] for _ in range(size)]
    #La primera columna se apunta hacia arriba
    for row in maze:
        row[0] = '^'
    #Se pone el origen en 0,0
    maze[0][0] = 'n'
    return maze

#Toma un laberinto y modifica las direcciones
def randomizeMaze(maze):
    pos = [0, 0]

    #Suficientes iteraciones para el tamaño requerido
    for i in range(1000):
        #Dirección inválida para iniciar el ciclo
        dir = 'n'
        #Se selecciona una dirección para mover el origen que sea válida
        while not is_valid(dir, pos, maze):
            dir = random.choice(LETTERS)

        #Apunta a la nueva dirección
        maze[pos[0]][pos[1]] = dir

        #Se mueve en la dirección elegida
        pos = [pos[0]+DIRECTIONS[dir][1], pos[1]+DIRECTIONS[dir][0]]

        #Se asigna el nuevo origen
        maze[pos[0]][pos[1]] = 'n'

    return maze

#Expande la matriz
#Las posiciones originales se separan por paredes
#Las paredes a las que apuntan las posiciones se convierten en pasillos
def convertMaze(maze):
    #Se crea una matriz llena de unos en la que caben las casillas y las paredes
    nlen = 2 * len(maze) - 1
    nmaze = [[1 for _ in range(nlen)] for _ in range(nlen)]

    #Las casillas se vuelven ceros
    for i in range(nlen):
        for j in range(nlen):
            if i % 2 == 0 and j % 2 == 0:
                nmaze[i][j] = 0

    #Se evalua la dirección a la que apunta cada casilla
    #La pared a la que apunta se convierte en pasillo 
    for i, row in enumerate(maze):
        for j, pos in enumerate(row):
            nmaze[(i * 2) + DIRECTIONS[pos][1]][(j * 2) + DIRECTIONS[pos][0]] = 0

    num_preguntas = 3
    for __ in range(num_preguntas):
        while True:
            x = random.randint(0, nlen - 1)
            y = random.randint(0, nlen - 1)

            if nmaze[x][y] == 0:
                nmaze[x][y] = 5
                break

    #Caso base: esquina inferior derecha
    exitPos = [nlen-1,nlen-1]
    #Randomiza el eje que cambia y la casilla que se va a asignar
    exitPos[random.randint(0,1)] = 2*random.randint(0,len(maze)-1)
    #Asigna el final del laberinto
    nmaze[exitPos[0]][exitPos[1]] = 2
    return nmaze


def generate(size):
    #Genera un laberinto base
    #Randimiza el laberinto
    #Convierte el laberinto a un formato usable
    return convertMaze(randomizeMaze(baseMaze(size)))

#variable global para controlar si se respondio correctamente
respuesta_correcta = False
res = ""

#funcion para hacer una pregunta matematica que permite seguir si se contesta correctamente
def hacer_pregunta():
    global respuesta_correcta, res, temporizador_activo
    respuesta_correcta = False
    res = ""
    temporizador_activo = True

    #crear una ventana emergente para la pregunta
    pregunta_ventana = tk.Toplevel()
    pregunta_ventana.title("Pregunta")
    pregunta_ventana.geometry("400x300")

    #deshabilitar el cierre de la ventana con el botón de cerrar
    pregunta_ventana.protocol("WM_DELETE_WINDOW", lambda: None)

    #generar una pregunta aleatoria
    a, b = random.randint(1, 1000), random.randint(1, 100)
    operador = random.choice(['+', '-'])
    if operador == '+':
        respuesta_correcta_valor = a + b
    else:
        respuesta_correcta_valor = a - b

    #pregunta
    titulo_label = tk.Label(pregunta_ventana, text=f"Celda de pregunta", font=("Helvetica", 16))
    titulo_label.pack(pady=10)
    pregunta_label = tk.Label(pregunta_ventana, text=f"¿Cuanto es {a} {operador} {b}?", font=("Helvetica", 16))
    pregunta_label.pack(pady=10)

    #celda de respuesta
    respuesta = tk.Entry(pregunta_ventana, font=("Helvetica", 16))
    respuesta.pack(pady=10)

    #funcion para verificar la respuesta
    def verificar_respuesta():
        global respuesta_correcta, temporizador_activo
        res = respuesta.get()
        temporizador_activo = False  #detener el temporizador
        if res == str(respuesta_correcta_valor):
            resultado_label.config(text="Correcto, puedes continuar", fg="green")
            respuesta_correcta = True
            pregunta_ventana.after(2000, pregunta_ventana.destroy)
        else:
            resultado_label.config(text="Incorrecto, has perdido", fg="red")
            pregunta_ventana.after(2000, os._exit, 0)

    #función para el temporizador
    def tiempo_restante(i, label, ventana):
        if i > -1 and temporizador_activo:  #continuar solo si el temporizador está activo
            label.config(text=f"Tiempo restante: {i} segundos")
            ventana.after(1000, tiempo_restante, i-1, label, ventana)
        elif temporizador_activo:  #si el tiempo se agota y el temporizador sigue activo
            label.config(text="Tiempo agotado, has perdido.", fg="red")
            ventana.after(2000, os._exit, 0)

    #manejar la tecla "Enter" para verificar la respuesta
    def on_enter(event):
        verificar_respuesta()

    respuesta.bind("<Return>", on_enter)

    #mostrar tiempo
    tiempo = tk.Label(pregunta_ventana, text="", font=("Helvetica", 18))
    tiempo.pack(pady=10)
    tiempo_restante(10, tiempo, pregunta_ventana)  #iniciar el temporizador con 10 segundos

    #mostrar resultado
    resultado_label = tk.Label(pregunta_ventana, text="", font=("Helvetica", 16))
    resultado_label.pack(pady=10)

    #esperar a que la pregunta sea respondida 
    pregunta_ventana.wait_window()


def resolver_laberinto_dp(laberinto, actualizarPantalla):
    n = len(laberinto)
    dp = [[-1 for _ in range(n)] for _ in range(n)] #crear matriz para almacenar resultados de subproblemas, se llena con -1 para indicar que ninguna de esas celdas
                                                    #se ha explorado

    #funcion recursiva para explorar el laberinto, empezara en (0, 0)
    def buscar_camino_dp(x, y):
        if x < 0 or y < 0 or x >= n or y >= n or laberinto[x][y] == 1:
        #si la celda que recorre esta fuera de los limites o es un muro, es un camino no valido asi que regresa falso
            return False
        #si la celda es la salida "2", marca la celda en dp como parte de la solucion y regresa true indicando que se encontro un camino
        if laberinto[x][y] == 2:
            dp[x][y] = 2
            return True
        #si la celda que recorre esta marcada con un 5, llama a la funcion hacer pregunta
         # Si la celda es una celda de pregunta (5), haz la pregunta.
        if laberinto[x][y] == 5:
            hacer_pregunta()  # Llama a la función para hacer la pregunta.
            
        #si la celda ya se ha explorado (su valor es diferente a -1), reusa el valor almacenado para evitar calculos redundantes
        #   -1 es el valor inicial para indicar que todavia no se ha explorado una celda en dp
        #   si la condicion es verdadera, la celda ya ha sido explorada. el algoritmo ya sabe si un camino hacia la salida existe en esta celda
            if not respuesta_correcta:
                return False
        if dp[x][y] != -1:
            #si el valor en esta celda es "2", la expresion es true
            return dp[x][y] == 2

        #esta linea marca de manera temporal la celda actual (x, y) como un muro "1" esto se hace para prevenir que el algoritmo revisite la misma celda durante la 
        #   exploracion recursiva, evitando loops infinitos 
        laberinto[x][y] = 1

        #este if revisa si un camino hacia la salida se encuentra en la celda (x, y) mediante explorar recursivamente las celdas vecinas
        if (buscar_camino_dp(x + 1, y) or buscar_camino_dp(x, y + 1) or
            buscar_camino_dp(x - 1, y) or buscar_camino_dp(x, y - 1)):
            #si se encuentra un camino, marca como parte de la solucion esa celda y regresa true
            dp[x][y] = 5
            actualizarPantalla(x, y)
            time.sleep(0.04)
            return True

        #si un camino no fue encontrado desde la celda, se marca la celda en dp con "0" para evitar explorarlo de nuevo
        laberinto[x][y] = 0
        dp[x][y] = 0
        return False

    #exito guarda el resultado de buscar_camino_dp(0, 0). indica si se encontro un camino de la entrada (0, 0) hasta la salida "2"
    exito = buscar_camino_dp(0, 0)

    return exito

#mostrar la ventana del laberinto con un tamaño de 10
Window(10)
