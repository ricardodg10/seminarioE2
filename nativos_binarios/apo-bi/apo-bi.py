import random
import time
import math

# -----------------------------------------------
# FUNCIONES AUXILIARES
# -----------------------------------------------

def leer_vertices(ruta):
    with open(ruta, 'r') as file:
        lines = file.readlines()
        num_vertices, _, _ = map(int, lines[1].split())
    return num_vertices

def leer_aristas(ruta):
    aristas = []
    with open(ruta, 'r') as file:
        lines = file.readlines()
        for line in lines[2:]:
            v1, v2 = map(int, line.split())
            aristas.append((v1, v2))  # base 1
    return aristas

def s1(v):
    return 1 / (1 + math.exp(-v))

def binarizar_sigmoide(v):
    return 1 if random.random() < s1(v) else 0

def levy_flight(dimension):
    beta = 1.5
    sigma_u = (math.gamma(1 + beta) * math.sin(math.pi * beta / 2) /
               (math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1)/2)))**(1 / beta)
    sigma_v = 1
    U = [random.gauss(0, sigma_u) for _ in range(dimension)]
    V = [random.gauss(0, sigma_v) for _ in range(dimension)]
    return [u / abs(v) ** (1 / beta) for u, v in zip(U, V)]

def funcion_objetivo(solucion):
    return sum(solucion)

def reparar_solucion(solucion, aristas):
    for v1, v2 in aristas:
        if solucion[v1 - 1] == 0 and solucion[v2 - 1] == 0:
            solucion[random.choice([v1 - 1, v2 - 1])] = 1
    return solucion

# -----------------------------------------------
# CLASE PUFFIN (INDIVIDUO)
# -----------------------------------------------
class Puffin:
    def __init__(self, dimension, LB, UB, aristas):
        self.dimension = dimension
        self.lower_bound = LB
        self.upper_bound = UB
        self.aristas = aristas
        self.posicion_real = [random.uniform(LB, UB) for _ in range(dimension)]
        self.posicion = [binarizar_sigmoide(v) for v in self.posicion_real]
        self.posicion = reparar_solucion(self.posicion, aristas)
        self.fitness = funcion_objetivo(self.posicion)

    def evaluar(self):
        self.fitness = funcion_objetivo(self.posicion)
        return self.fitness

    def ajustar_limites(self, vector):
        return [max(self.lower_bound, min(x, self.upper_bound)) for x in vector]

    def actualizar_desde_vector_real(self, nuevo_vector):
        self.posicion_real = self.ajustar_limites(nuevo_vector)
        self.posicion = [binarizar_sigmoide(v) for v in self.posicion_real]
        self.posicion = reparar_solucion(self.posicion, self.aristas)
        self.fitness = funcion_objetivo(self.posicion)

    # Estrategia aérea: evitar depredadores
    def evitar_dep(self, X_r, L, R):
        return [x_i + (x_i - x_r) * l + R for x_i, x_r, l in zip(self.posicion_real, X_r, L)]

    # Estrategia aérea: picada
    def picada(self, Y, S):
        return [y * S for y in Y]

    # Estrategia subacuática: recolección cooperativa
    def recoleccion(self, X2, X3, F, L1=None):
        if L1:
            return [x1 + F * l1 * (x2 - x3) for x1, x2, x3, l1 in zip(self.posicion_real, X2, X3, L1)]
        else:
            return [x1 + F * (x2 - x3) for x1, x2, x3 in zip(self.posicion_real, X2, X3)]

    # Estrategia subacuática: intensificación
    def intensificar(self, W, f):
        return [w * (1 + f) for w in W]

    # Estrategia subacuática: evasión
    def evasion(self, X_r, modo="levy", L2=None, beta=None, F=0.5):
        if modo == "levy":
            return [x1 + F * l * (x1 - x2) for x1, x2, l in zip(self.posicion_real, X_r, L2)]
        else:
            return [x1 + beta * (x1 - x2) for x1, x2 in zip(self.posicion_real, X_r)]

# -----------------------------------------------
# CLASE APO
# -----------------------------------------------
class APO:
    def __init__(self, num_puffins, dimension, LB, UB, max_iter, aristas):
        self.num_puffins = num_puffins
        self.dimension = dimension
        self.lower_bound = LB
        self.upper_bound = UB
        self.max_iter = max_iter
        self.aristas = aristas
        self.poblacion = [Puffin(dimension, LB, UB, aristas) for _ in range(num_puffins)]
        self.mejor_global = self.poblacion[0].posicion[:]
        self.mejor_valor = self.poblacion[0].fitness

    def optimizar(self):
        tiempo_inicio = time.time()

        for t in range(1, self.max_iter + 1):
            B = 2 * math.log(1 / random.random()) * (1 - (t / self.max_iter))
            C = 0.5
            candidatos = []

            if B > C:
                # Fase aérea
                for i, puffin in enumerate(self.poblacion):
                    r = random.choice([j for j in range(self.num_puffins) if j != i])
                    X_r = self.poblacion[r].posicion_real
                    L = levy_flight(self.dimension)
                    alpha = random.gauss(0, 1)
                    R = round(0.5 * (0.5 + random.random()) * alpha)

                    Y = puffin.evitar_dep(X_r, L, R)
                    S = math.tan((random.random() - 0.5) * math.pi)
                    Z = puffin.picada(Y, S)

                    # evaluar Y y Z como candidatos
                    for vec in [Y, Z]:
                        temp = Puffin(self.dimension, self.lower_bound, self.upper_bound, self.aristas)
                        temp.actualizar_desde_vector_real(vec)
                        candidatos.append((temp.posicion, temp.fitness))
            else:
                # Fase subacuática
                for i, puffin in enumerate(self.poblacion):
                    r2, r3 = random.sample([j for j in range(self.num_puffins) if j != i], 2)
                    X2 = self.poblacion[r2].posicion_real
                    X3 = self.poblacion[r3].posicion_real
                    F = 0.5

                    if random.random() >= 0.5:
                        L1 = levy_flight(self.dimension)
                        W = puffin.recoleccion(X2, X3, F, L1)
                    else:
                        W = puffin.recoleccion(X2, X3, F)

                    f = 0.1 * (random.random() - 1) * (1 - (t / self.max_iter))
                    Y = puffin.intensificar(W, f)

                    r4 = random.choice([j for j in range(self.num_puffins) if j != i])
                    X_r = self.poblacion[r4].posicion_real

                    if random.random() >= 0.5:
                        L2 = levy_flight(self.dimension)
                        Z = puffin.evasion(X_r, "levy", L2=L2, F=F)
                    else:
                        beta = random.uniform(0, 1)
                        Z = puffin.evasion(X_r, "beta", beta=beta)

                    for vec in [W, Y, Z]:
                        temp = Puffin(self.dimension, self.lower_bound, self.upper_bound, self.aristas)
                        temp.actualizar_desde_vector_real(vec)
                        candidatos.append((temp.posicion, temp.fitness))

            # seleccionar mejores soluciones
            candidatos.sort(key=lambda x: x[1])
            for i in range(self.num_puffins):
                self.poblacion[i].posicion = candidatos[i][0]
                self.poblacion[i].posicion_real = candidatos[i][0]

            for puffin in self.poblacion:
                valor = funcion_objetivo(puffin.posicion)
                if valor < self.mejor_valor:
                    self.mejor_valor = valor
                    self.mejor_global = puffin.posicion[:]

            print(f"Iteración {t} - Vértices cubiertos (activos): {sum(self.mejor_global)}")

        tiempo_total = time.time() - tiempo_inicio
        return self.mejor_global, self.mejor_valor, tiempo_total

# -----------------------------------------------
# BLOQUE PRINCIPAL
# -----------------------------------------------
if __name__ == "__main__":
    ruta_archivo = "C:/Users/ricar/OneDrive/Escritorio/seminario/benchmark/C125-9.mtx"
    num_vertices = leer_vertices(ruta_archivo)
    aristas = leer_aristas(ruta_archivo)

    tamanio_poblacion = 5
    lower_bound = -6
    upper_bound = 6
    max_iteraciones = 100

    apo = APO(tamanio_poblacion, num_vertices, lower_bound, upper_bound, max_iteraciones, aristas)
    mejor_sol, mejor_valor, tiempo = apo.optimizar()

    print("\nMejor solución encontrada (binaria):", mejor_sol)
    print("Vértices seleccionados:", [i + 1 for i, v in enumerate(mejor_sol) if v == 1])
    print("Valor de la función objetivo:", mejor_valor)
    print("Tiempo de ejecución:", tiempo, "[s]")
