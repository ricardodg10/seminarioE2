import random
import time
import math
import matplotlib.pyplot as plt  

'''Funciones de lectura'''
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

'''Función S-shape'''
# función sigmoide
def s1(v):
    return 1 / (1 + math.exp(-v))

# binarización
def binarizar_sigmoide(v):
    return 1 if random.random() < s1(v) else 0

'''Función objetivo'''
def funcion_objetivo(solucion):
    return sum(solucion)

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
        self.fitness = funcion_objetivo(self.posicion)
        self.mejor_personal = self.posicion[:]
        self.mejor_fitness = self.fitness

    def reparar(self):
        for v1, v2 in self.aristas:
            if self.posicion[v1 - 1] == 0 and self.posicion[v2 - 1] == 0:
                self.posicion[random.choice([v1 - 1, v2 - 1])] = 1

    def actualizar_velocidad(self, mejor_global, w, c1, c2):
        for i in range(self.dimension):
            r1 = random.random()
            r2 = random.random()
            cognit = c1 * r1 * (self.mejor_personal[i] - self.posicion[i])  # funcionamiento de parte cognitiva para el dominio real
            social = c2 * r2 * (mejor_global[i] - self.posicion[i])         # funcionamiento de parte social para el dominio real
            self.velocidad[i] = w * self.velocidad[i] + cognit + social

    def actualizar_posicion(self):
        for i in range(self.dimension):
            self.posicion_real[i] += self.velocidad[i]
            self.posicion_real[i] = max(self.lower_bound, min(self.posicion_real[i], self.upper_bound))
        self.posicion = [binarizar_sigmoide(x) for x in self.posicion_real]
        self.reparar()

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
        self.mejor_valor = funcion_objetivo(self.mejor_global)
        self.iteracion_mejor = None         
        self.tiempo_mejor = None   

        self.historial_convergencia = []         

    def optimizar(self):

        print("\nEjecución PSO\n")
        tiempo_inicio = time.time()

        for t in range(1, self.max_iter + 1):
            for particula in self.poblacion:
                valor = funcion_objetivo(particula.posicion)

                if valor < particula.mejor_fitness:
                    particula.mejor_fitness = valor
                    particula.mejor_personal = particula.posicion[:]

                if valor < self.mejor_valor:
                    self.mejor_valor = valor
                    self.mejor_global = particula.posicion[:]
                    
                    self.iteracion_mejor = t
                    self.tiempo_mejor = time.time() - tiempo_inicio

            for particula in self.poblacion:
                particula.actualizar_velocidad(self.mejor_global, self.w, self.c1, self.c2)
                particula.actualizar_posicion()

            
            self.historial_convergencia.append(self.mejor_valor)
            print(f"Iteración {t} - Vértices cubiertos (g_best) {sum(self.mejor_global)}")

        tiempo_total = time.time() - tiempo_inicio
        return self.mejor_global, self.mejor_valor, tiempo_total


'''Main'''
if __name__ == "__main__":
    ruta_b1 = "C:/Users/ricar/OneDrive/Escritorio/seminario/benchmark/C125-9.mtx"
    ruta_b2 = "C:/Users/ricar/OneDrive/Escritorio/seminario/benchmark/keller4.mtx"
    ruta_b3 = "C:/Users/ricar/OneDrive/Escritorio/seminario/benchmark/keller5.mtx"

    num_vertices = leer_vertices(ruta_b3) 
    aristas = leer_aristas(ruta_b3)

    tamanio_poblacion = 5
    lower_bound = -6
    upper_bound = 6
    max_iteraciones = 100
    w = 0.5
    c1 = 2
    c2 = 2

    pso = PSO(funcion_objetivo=funcion_objetivo, num_particulas=tamanio_poblacion, dimension=num_vertices,
              LB=lower_bound, UB=upper_bound, max_iter=max_iteraciones, w=w, c1=c1, c2=c2, aristas=aristas)

    mejor_sol, mejor_valor, tiempo = pso.optimizar()

    # Resultado final
    print("\nMejor solución encontrada:", mejor_sol)
    print("Vértices seleccionados:", [i + 1 for i, v in enumerate(mejor_sol) if v == 1])
    print("Cobertura de vértices:", mejor_valor)

    print(f"\nMejor solución encontrada en iteración {pso.iteracion_mejor} \nMejor solución encontrada en el tiempo: {pso.tiempo_mejor} segundos")

    print("\nTiempo de ejecución total:", tiempo, "[s]\n")

    # Grafica de convergencia
    plt.plot(pso.historial_convergencia)
    plt.title('Convergencia del algoritmo PSO')
    plt.xlabel('Iteraciones')
    plt.ylabel('Valor de la función objetivo')
    plt.show()
