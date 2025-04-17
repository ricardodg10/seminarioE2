import random
import math
import time
import numpy as np

# ---------------------- Lectura del grafo ----------------------
# función para obtener la cantidad de vértices desde el archivo .mtx
def leer_vertices(mtx_file):
    with open(mtx_file, 'r') as file:
        lines = file.readlines()
        num_vertices, _, _ = map(int, lines[1].split())
    return num_vertices

# función para leer las aristas desde el archivo .mtx
# cada línea representa una arista como un par de vértices (v1, v2)
def leer_aristas(mtx_file):
    aristas = []
    with open(mtx_file, 'r') as file:
        lines = file.readlines()
        for line in lines[2:]:
            v1, v2 = map(int, line.split())
            aristas.append((v1, v2))
    return aristas

# ---------------------- Funciones S-shape ----------------------
# función sigmoide clásica para binarizar una posición real
def s1(v):
    return 1 / (1 + math.exp(-v))

# se aplica la función sigmoide y luego una comparación aleatoria para obtener 0 o 1
def binarizar_sigmoide(v):
    return 1 if random.random() < s1(v) else 0

# ---------------------- Clase Partícula ----------------------
class Particula:
    # inicialización de la partícula
    def __init__(self, dimension, LB, UB):
        self.dimension = dimension  # dimensión del problema
        self.lower_bound = LB       # límite inferior de posición
        self.upper_bound = UB       # límite superior de posición

        # posición y velocidad inicial aleatoria para cada dimensión
        self.posicion = [random.uniform(LB, UB) for _ in range(dimension)]
        self.velocidad = [random.uniform(LB, UB) for _ in range(dimension)]

        # mejor posición personal conocida y su valor asociado
        self.p_best = self.posicion[:]
        self.p_best_valor = float('inf')

    # actualiza la velocidad basada en la mejor posición personal y global
    def actualizar_velocidad(self, g_best, w, c1, c2):
        for i in range(self.dimension):
            r1 = random.random()
            r2 = random.random()
            cognitive = c1 * r1 * (self.p_best[i] - self.posicion[i])
            social = c2 * r2 * (g_best[i] - self.posicion[i])
            self.velocidad[i] = w * self.velocidad[i] + cognitive + social

    # actualiza la posición asegurando que se mantenga dentro de los límites
    def actualizar_posicion(self):
        for i in range(self.dimension):
            self.posicion[i] += self.velocidad[i]
            self.posicion[i] = max(self.lower_bound, min(self.posicion[i], self.upper_bound))

# ---------------------- Clase PSO ----------------------
class PSO:
    def __init__(self, funcion_objetivo, num_particulas, dimension, lower_bound, upper_bound, max_iter, aristas, w=0.5, c1=2.0, c2=2.0):
        self.funcion_objetivo = funcion_objetivo  # función a minimizar
        self.num_particulas = num_particulas      # número de partículas
        self.dimension = dimension                # dimensión del problema
        self.lower_bound = lower_bound            # límite inferior de posición
        self.upper_bound = upper_bound            # límite superior de posición
        self.max_iter = max_iter                  # número máximo de iteraciones
        self.aristas = aristas                    # lista de aristas del grafo
        self.w = w                                # inercia
        self.c1 = c1                              # coeficiente cognitivo
        self.c2 = c2                              # coeficiente social

        # crear el enjambre con partículas iniciales
        self.enjambre = [Particula(dimension, lower_bound, upper_bound) for _ in range(num_particulas)]

        # mejor solución global conocida y su valor
        self.g_best = None
        self.g_best_valor = float('inf')
        self.g_best_binaria = []  # solución binaria correspondiente

    # verifica si una solución binaria cubre todas las aristas del grafo
    def es_cobertura_valida(self, solucion):
        cubiertas = set()
        for i, bit in enumerate(solucion):
            if bit == 1:
                cubiertas.add(i + 1)
        for v1, v2 in self.aristas:
            if v1 not in cubiertas and v2 not in cubiertas:
                return False
        return True

    # si una solución binaria no cubre todas las aristas, la repara
    def reparar_solucion(self, solucion):
        cubiertas = set(i + 1 for i, bit in enumerate(solucion) if bit == 1)
        for v1, v2 in self.aristas:
            if v1 not in cubiertas and v2 not in cubiertas:
                if random.random() < 0.5:
                    solucion[v1 - 1] = 1
                    cubiertas.add(v1)
                else:
                    solucion[v2 - 1] = 1
                    cubiertas.add(v2)
        return solucion

    # ciclo principal de optimización
    def optimizar(self):
        tiempo_inicio = time.time()

        for iteracion in range(1, self.max_iter + 1):
            for particula in self.enjambre:
                # convertir posición real a binaria
                solucion_binaria = [binarizar_sigmoide(x) for x in particula.posicion]

                # verificar y reparar si es necesario
                if not self.es_cobertura_valida(solucion_binaria):
                    solucion_binaria = self.reparar_solucion(solucion_binaria)

                valor = self.funcion_objetivo(solucion_binaria)  # contar 1s (vértices usados)

                # actualizar mejor personal
                if valor < particula.p_best_valor:
                    particula.p_best_valor = valor
                    particula.p_best = particula.posicion[:]

                # actualizar mejor global
                if valor < self.g_best_valor:
                    self.g_best_valor = valor
                    self.g_best = particula.posicion[:]
                    self.g_best_binaria = solucion_binaria[:]

            # actualizar velocidad y posición para la siguiente iteración
            for particula in self.enjambre:
                particula.actualizar_velocidad(self.g_best, self.w, self.c1, self.c2)
                particula.actualizar_posicion()

            print(f"Iteración: {iteracion}. Mejor valor: {self.g_best_valor} (unos: {sum(self.g_best_binaria)})")

        tiempo_total = time.time() - tiempo_inicio

        # verificación final de validez
        if not self.es_cobertura_valida(self.g_best_binaria):
            self.g_best_binaria = self.reparar_solucion(self.g_best_binaria)

        # mostrar resultado final
        print("\nMejor solución encontrada (binaria):", self.g_best_binaria)
        print("Vértices seleccionados:", [i + 1 for i, v in enumerate(self.g_best_binaria) if v == 1])
        print("Valor de la función objetivo:", sum(self.g_best_binaria))
        print("Tiempo de ejecución:", tiempo_total, "[s]")

# ---------------------- Ejecución ----------------------
# función objetivo: contar la cantidad de vértices activos (1s)
def funcion_objetivo(posicion):
    return sum(posicion)

if __name__ == "__main__":
    # archivo .mtx con el grafo a optimizar
    ruta = "C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\benchmark\\C125-9.mtx"

    cantidad_vertices = leer_vertices(ruta)  # número de vértices
    aristas = leer_aristas(ruta)            # lista de aristas

    # inicializar y ejecutar el PSO
    pso = PSO(
        funcion_objetivo=funcion_objetivo,
        num_particulas=10,
        dimension=cantidad_vertices,
        lower_bound=-6,
        upper_bound=6,
        max_iter=100,
        aristas=aristas
    )

    pso.optimizar()
