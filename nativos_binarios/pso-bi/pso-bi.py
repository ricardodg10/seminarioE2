import random
import time

# función para leer el número de vértices del archivo .mtx
def leer_vertices(mtx_file):
    with open(mtx_file, 'r') as file:
        lines = file.readlines()
        num_vertices, _, _ = map(int, lines[1].split())  # Número de vértices
    return num_vertices

# función para leer las aristas del archivo .mtx
def leer_aristas(mtx_file):
    aristas = []
    with open(mtx_file, 'r') as file:
        lines = file.readlines()
        for line in lines[2:]:
            v1, v2 = map(int, line.split())
            aristas.append((v1, v2))  # Pareja de vértices (arista)
    return aristas

# clase partícula
class Particula:
    def __init__(self, dimension, LB, UB, aristas):
        self.dimension = dimension
        self.lower_bound = LB
        self.upper_bound = UB
        self.posicion_real = [random.uniform(LB, UB) for _ in range(dimension)]
        self.posicion = [binarizar_sigmoide(x) for x in self.posicion_real]
        self.velocidad = [random.uniform(LB, UB) for _ in range(dimension)]
        self.aristas = aristas

        self.reparar()
        self.fitness = self.calcular_fitness()
        self.mejor_personal = self.posicion[:]
        self.mejor_fitness = self.fitness

    def calcular_fitness(self):
        return sum(self.posicion)  # cantidad de vértices cubiertos

    def reparar(self):
        for v1, v2 in self.aristas:
            if self.posicion[v1 - 1] == 0 and self.posicion[v2 - 1] == 0:
                self.posicion[random.choice([v1 - 1, v2 - 1])] = 1

    def actualizar_velocidad(self, mejor_global, w, c1, c2):
        for i in range(self.dimension):
            r1 = random.random()
            r2 = random.random()
            cognit = c1 * r1 * (self.mejor_personal[i] - self.posicion[i])
            social = c2 * r2 * (mejor_global[i] - self.posicion[i])
            self.velocidad[i] = w * self.velocidad[i] + cognit + social

    def actualizar_posicion(self):
        for i in range(self.dimension):
            self.posicion_real[i] += self.velocidad[i]
            self.posicion_real[i] = max(self.lower_bound, min(self.posicion_real[i], self.upper_bound))
        self.posicion = [binarizar_sigmoide(x) for x in self.posicion_real]
        self.reparar()

# función sigmoide
def s1(v):
    return 1 / (1 + pow(2.71828, -v))

# binarización
def binarizar_sigmoide(v):
    return 1 if random.random() < s1(v) else 0

# clase del algoritmo PSO
class PSO:
    def __init__(self, funcion_objetivo, num_particulas, dimension, LB, UB, max_iter, w, c1, c2, aristas):
        self.funcion_objetivo = funcion_objetivo
        self.num_particulas = num_particulas
        self.dimension = dimension
        self.lower_bound = LB
        self.upper_bound = UB
        self.max_iter = max_iter
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.aristas = aristas

        self.poblacion = [Particula(dimension, LB, UB, aristas) for _ in range(num_particulas)]
        self.mejor_global = self.poblacion[0].posicion[:]
        self.mejor_valor = self.funcion_objetivo(self.mejor_global)

    def optimizar(self):
        tiempo_inicio = time.time()

        for t in range(1, self.max_iter + 1):
            for particula in self.poblacion:
                valor = self.funcion_objetivo(particula.posicion)

                if valor < particula.mejor_fitness:
                    particula.mejor_fitness = valor
                    particula.mejor_personal = particula.posicion[:]

                if valor < self.mejor_valor:
                    self.mejor_valor = valor
                    self.mejor_global = particula.posicion[:]

            for particula in self.poblacion:
                particula.actualizar_velocidad(self.mejor_global, self.w, self.c1, self.c2)
                particula.actualizar_posicion()

            print(f"Iteración {t} - Vértices cubiertos (activos): {sum(self.mejor_global)}")

        tiempo_total = time.time() - tiempo_inicio
        return self.mejor_global, self.mejor_valor, tiempo_total


# ------------------------- BLOQUE PRINCIPAL -------------------------
if __name__ == "__main__":
    archivo = "C:/Users/ricar/OneDrive/Escritorio/seminario/benchmark/C125-9.mtx"
    num_vertices = leer_vertices(archivo)
    aristas = leer_aristas(archivo)

    def funcion_objetivo(solucion):
        return sum(solucion)

    tamanio_poblacion = 5
    lower_bound = -6
    upper_bound = 6
    max_iteraciones = 100
    w = 0.5
    c1 = 2
    c2 = 2

    pso = PSO(funcion_objetivo, tamanio_poblacion, num_vertices,
              lower_bound, upper_bound, max_iteraciones, w, c1, c2, aristas)

    mejor_sol, mejor_valor, tiempo = pso.optimizar()

    print("\nMejor solución encontrada (binaria):", mejor_sol)
    print("Vértices seleccionados:", [i + 1 for i, v in enumerate(mejor_sol) if v == 1])
    print("Valor de la función objetivo:", mejor_valor)
    print("Tiempo de ejecución:", tiempo, "[s]")
