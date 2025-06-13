import random       # para las variables aleatorias del algoritmo
import time         # para medir el tiempo de ejecución
import math         # para funciones matemáticas como logaritmo y tangente

# función Lévy Flight para saltos aleatorios en el espacio de búsqueda
def levy_flight(dimension):
    beta = 1.5 # 0 < beta <= 2

    sigma_u = (math.gamma(1 + beta) * math.sin(math.pi * beta / 2) /
             (math.gamma((1 + beta) / 2) * beta * 2**((beta - 1) / 2)))**(1 / beta)
    sigma_v = 1

    U = [random.gauss(0, sigma_u) for _ in range(dimension)]
    V = [random.gauss(0, sigma_v) for _ in range(dimension)]

    step_lenght = [u / abs(v)**(1 / beta) for u, v in zip(U, V)] # zip para iterar dentro del mismo "for" los valores de "U" y de "V"
    return step_lenght

# clase puffin
class Puffin:
    def __init__(self, dimension, LB, UB):
        self.dimension = dimension      # número de dimensiones del problema
        self.lower_bound = LB           # límite inferior del espacio de búsqueda
        self.upper_bound = UB           # límite superior del espacio de búsqueda

        # inicializar posición aleatoria
        self.posicion = [random.uniform(LB, UB) for _ in range(dimension)]
        self.valor = float('inf')       # valor de la función objetivo (a minimizar)

    def evaluar(self, funcion_objetivo):
        # evalúa el valor de la función objetivo en la posición actual
        self.valor = funcion_objetivo(self.posicion)
        return self.valor

# clase de algoritmo APO (Arctic Puffin Optimization)
class APO:
    def __init__(self, funcion_objetivo, num_puffins, dimension, lower_bound, upper_bound, max_iter):
        self.funcion_objetivo = funcion_objetivo
        self.num_puffins = num_puffins
        self.dimension = dimension
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.max_iter = max_iter

        # crear la población inicial de puffins
        self.poblacion = [Puffin(dimension, lower_bound, upper_bound) for _ in range(num_puffins)]

        # inicializar mejor solución global
        self.mejor_global = self.poblacion[0].posicion[:]
        self.mejor_valor = float('inf')

    def ajustar_limites(self, posicion):
        # asegura que cada valor de la posición esté dentro de los límites permitidos
        return [max(self.lower_bound, min(x, self.upper_bound)) for x in posicion]

    def optimizar(self):
        tiempo_inicio = time.time()  # medir tiempo de inicio

        for t in range(1, self.max_iter + 1):
            # factor de conversión de comportamiento B para determinar la estrategia (aire o agua)
            B = 2 * math.log(1 / random.random()) * (1 - (t / self.max_iter))
            C = 0.5  # valor umbral, definido en la teoría

            posiciones_candidatas = []

            # Fase aérea (exploración global)
            if B > C:  
                for i, puffin in enumerate(self.poblacion):
                    # estrategia 1: evadir depredadores
                    X_i = puffin.posicion
                    r = random.choice([j for j in range(self.num_puffins) if j != i])       # indice aleatorio de un individuo (excluye el actual)
                    X_r = self.poblacion[r].posicion                                        # posición del individuo aleatorio
                    L = levy_flight(self.dimension)                                         # componente de levy flight dentro de la dimension del problema
                    alpha = random.gauss(0, 1)                                              # random [0,1], distribución normal
                    R = round(0.5 * (0.5 + random.random()) * alpha)                        # componente R
                    Y_i = [x_i + (x_i - x_r) * l + R for x_i, x_r, l in zip(X_i, X_r, L)]   # posicion nueva al evadir depredadores

                    # estrategia 2: depredación en picada
                    S = math.tan((random.random() - 0.5) * math.pi)                         # coeficiente de velocidad
                    Z_i = [y * S for y in Y_i]                                              # nueva posición luego de la fase aérea

                    # ajustar limites
                    Y_i = self.ajustar_limites(Y_i)
                    Z_i = self.ajustar_limites(Z_i)

                    # unión de las soluciones
                    posiciones_candidatas.append((Y_i, self.funcion_objetivo(Y_i)))
                    posiciones_candidatas.append((Z_i, self.funcion_objetivo(Z_i)))
            
            # Fase subacuática (explotación local)
            else:  
                for i in range(self.num_puffins):
                    r1_1, r2_1, r3_1 = random.sample([j for j in range(self.num_puffins) if j != i], 3)                                     # se definen los índices de tres individuos distintos al actual (sample: para que los escogidos no sean repetidos)
                    X_r1_1, X_r2_1, X_r3_1 = self.poblacion[r1_1].posicion, self.poblacion[r2_1].posicion, self.poblacion[r3_1].posicion    # se obtienen las posiciones de los individuos aleatorios
                    F = 0.5                                                                                                                 # factor cooperativo (valor por teoría)
                    L1 = levy_flight(self.dimension)                                                                                        # componente de levy flight dentro de la dimension del problema

                    # estrategia 1: recolección de comida con la población

                    ## explora el entorno en cooperación con otros individuos
                    if random.random() >= 0.5:
                        W_i = [x_r1 + F * l1 * (x_r2 - x_r3) for x_r1, x_r2, x_r3, l1 in zip(X_r1_1, X_r2_1, X_r3_1, L1)]   # posición nueva al explorar le entorno en cooperación con otros individuos        

                    ## sigue a otros individuos y se une a un grupo más ventajoso
                    else:
                        W_i = [x_r1 + F * (x_r2 - x_r3) for x_r1, x_r2, x_r3 in zip(X_r1_1, X_r2_1, X_r3_1)]                # posición nueva al seguir al grupo más ventajoso

                    # estrategia 2: búsqueda intensificada (cambio de posición en el agua por falta de alimento)
                    f = 0.1 * (random.random() - 1) * (1 - (t / self.max_iter))                                             # factor adaptativo del frailencillo en el agua
                    Y_i = [w_i * (1 + f) for w_i in W_i]                                                                    # nueva posición en el agua

                    # estrategia 3: evadir depredadores

                    r1_2, r2_2 = random.sample([j for j in range(self.num_puffins) if j != i], 2)                               # se definen los índices de dos individuos distintos al actual (sample: para que los escogidos no sean repetidos)
                    X_r1_2, X_r2_2 = self.poblacion[r1_2].posicion, self.poblacion[r2_2].posicion                               # se obtienen las posiciones de los individuos aleatorios

                    if random.random() >= 0.5:
                        L2 = levy_flight(self.dimension)                                                                        # componente de levy flight dentro de la dimension del problema
                        Z_i = [x_r1_2 + F * l2 * (x_r1_2 - x_r2_2) for x_r1_2, x_r2_2, l2 in zip(X_r1_2, X_r2_2, L2)]           # nueva posición luego de evadir depredadores
                    else:
                        beta = random.uniform(0, 1)
                        Z_i = [x_r1_2 + beta * (x_r1_2 - x_r2_2) for x_r1_2, x_r2_2 in zip(X_r1_2, X_r2_2)]                     # nueva posición luego de evadir depredadores

                    # ajustar limites
                    Y_i = self.ajustar_limites(Y_i)
                    Z_i = self.ajustar_limites(Z_i)
                    W_i = self.ajustar_limites(W_i)

                    # union de las soluciones
                    posiciones_candidatas.append((W_i, self.funcion_objetivo(W_i)))
                    posiciones_candidatas.append((Y_i, self.funcion_objetivo(Y_i)))
                    posiciones_candidatas.append((Z_i, self.funcion_objetivo(Z_i)))
            
            # se ordenan las soluciones desde el menor al mayor fitness
            posiciones_candidatas.sort(key=lambda x: x[1])

            # se guardan las mejores posiciones y se reemplazan en la población
            for i in range(self.num_puffins):
                self.poblacion[i].posicion = posiciones_candidatas[i][0]

            # luego de haber actualizado la población completa
            for puffin in self.poblacion:
                valor = puffin.evaluar(self.funcion_objetivo)

                if valor < self.mejor_valor:
                    self.mejor_valor = valor
                    self.mejor_global = puffin.posicion[:]

            print(f"Iteración {t} - Mejor solución {self.mejor_global} - Mejor valor = {self.mejor_valor}")

        tiempo_total = time.time() - tiempo_inicio  # tiempo final
        return self.mejor_global, self.mejor_valor, tiempo_total


# main
if __name__ == "__main__":
    def funcion_objetivo(pos):
        # ejemplo de función objetivo: esfera
        return sum(x for x in pos)

    apo = APO(funcion_objetivo, num_puffins=5, dimension=2, lower_bound=-10, upper_bound=10, max_iter=10)
    mejor_pos, mejor_valor, tiempo = apo.optimizar()

    print("\nMejor posición encontrada:", mejor_pos)
    print("Valor mínimo encontrado:", mejor_valor)
    print("Tiempo de ejecución:", tiempo, "[s]")
