import random
import time
import math
import matplotlib.pyplot as plt  

'''Funciones de lectura'''

# función para leer y obtener el número de vértices desde archivo .mtx
def leer_vertices(mtx_file):
    with open(mtx_file, 'r') as file:
        lines = file.readlines()
        num_vertices, _, _ = map(int, lines[1].split())
    return num_vertices

# función para leer aristas del archivo .mtx
# cada línea representa una arista como un par de vértices (v1, v2)
def leer_aristas(mtx_file):
    aristas = []
    with open(mtx_file, 'r') as file:
        lines = file.readlines()
        for line in lines[2:]:
            v1, v2 = map(int, line.split())
            aristas.append((v1, v2))  # no se ajustan porque se usan con v-1 más abajo
    return aristas

# función Lévy Flight para saltos aleatorios en el espacio de búsqueda
def levy_flight(dimension):
    beta = 1.5 # 0 < beta <= 2

    sigma_u = (math.gamma(1 + beta) * math.sin(math.pi * beta / 2) /
               (math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))) ** (1 / beta)
    sigma_v = 1

    U = [random.gauss(0, sigma_u) for _ in range(dimension)]
    V = [random.gauss(0, sigma_v) for _ in range(dimension)]

    step_lenght = [u / abs(v)**(1 / beta) for u, v in zip(U, V)] # zip para iterar dentro del mismo "for" los valores de "U" y de "V"
    return step_lenght

'''Funciones S-shape'''

# función sigmoide clásica para binarizar una posición real
def s1(v):
    return 1 / (1 + math.exp(-v))

# binarización usando sigmoide: se aplica la función sigmoide y luego una comparación aleatoria para obtener 0 o 1
def binarizar_sigmoide(v):
    return 1 if random.random() < s1(v) else 0

'''Función objetivo'''
def funcion_objetivo(solucion):
    return sum(solucion)

# verificación y reparación de soluciones (estilo GA)
def reparar_solucion(solucion, aristas):
    for v1, v2 in aristas:
        if solucion[v1 - 1] == 0 and solucion[v2 - 1] == 0:
            solucion[random.choice([v1 - 1, v2 - 1])] = 1
    return solucion

'''Arctic Puffin Optimization'''

# Clase Puffin
class Puffin:
    # inicialización del puffin
    def __init__(self, dimension, LB, UB):
        self.dimension = dimension  # dimensión del problema
        self.lower_bound = LB       # límite inferior de posición
        self.upper_bound = UB       # límite superior de posición
        self.aristas = aristas

        # posición inicial aleatoria 
        self.posicion_real = [random.uniform(LB, UB) for _ in range(dimension)]
        self.posicion_binaria = [binarizar_sigmoide(v) for v in self.posicion_real]

        self.valor = float('inf')

    def evaluar(self, funcion_objetivo):
        self.valor = funcion_objetivo(self.posicion_binaria)
        return self.valor
    
    '''Estrategia aérea'''
    #1.- Evadir depredadores
    def evadir_aire(self, X_r, L, R):
        return [x_i + (x_i - x_r) * l + R for x_i, x_r, l in zip(self.posicion_real, X_r, L)]
    
    #2.- Depredación en picada
    def dep_picada(self, Y, S):
        return [y * S for y in Y]
    
    '''Estrategia subacuática'''
    # 1.- Recolección de comida
    def recoleccion(self, X2, X3, F, L1=None):
        if L1:
            # sigue a otros miembros y se une a un grupo más ventajoso
            return [x1 + F * l1 * (x2 - x3) for x1, x2, x3, l1 in zip(self.posicion_real, X2, X3, L1)] 
        else:
            # explora el entorno en cooperación con otros individuos
            return [x1 + F * (x2 - x3) for x1, x2, x3 in zip(self.posicion_real, X2, X3)]
        
    # 2.- Intensificando la búsqueda
    def intensificar(self, W, f):
        return [w * (1 + f) for w in W]
    
    # 3.- Evadir depredadores
    def evadir_agua(self, X_r1, X_r2, L=None, beta=None, F=0.5):
        if L:
            return [x1 + F * l * (x1 - x2) for x1, x2, l in zip(X_r1, X_r2, L)]
        else:
            return [x1 + beta * (x1 - x2) for x1, x2 in zip(X_r1, X_r2)]


'''Clase del algoritmo APO (Arctic Puffin Optimization)'''
class APO:
    def __init__(self, funcion_objetivo, num_puffins, dimension, lower_bound, upper_bound, max_iter):
        self.funcion_objetivo = funcion_objetivo    # función a minimizar
        self.num_puffins = num_puffins              # número de puffins
        self.dimension = dimension                  # dimensión del problema
        self.lower_bound = lower_bound              # límite inferior de posición
        self.upper_bound = upper_bound              # límite superior de posición
        self.max_iter = max_iter                    # número máximo de iteraciones


        self.poblacion = [Puffin(dimension, lower_bound, upper_bound) for _ in range(num_puffins)]
        self.g_best_binario = [0] * dimension
        self.g_best_real = [0] * dimension
        self.mejor_valor = float('inf')
        self.iteracion_mejor = None                 # Para almacenar la iteración cuando se encontró el mejor g_best
        self.tiempo_mejor = None                    # Para almacenar el tiempo cuando se encontró el mejor g_best
        self.historial_convergencia = []            # Para almacenar los valores de la función objetivo en cada iteración

    def ajustar_limites(self, posicion):
        return [max(self.lower_bound, min(x, self.upper_bound)) for x in posicion]

    def optimizar(self, aristas):
        tiempo_inicio = time.time()

        for t in range(1, self.max_iter + 1):
            B = 2 * math.log(1 / random.random()) * (1 - (t / self.max_iter))
            C = 0.5
            candidatos = []

            if B > C:  # fase aérea
                for i, puffin in enumerate(self.poblacion):
                    X_i = puffin.posicion_real
                    r = random.choice([j for j in range(self.num_puffins) if j != i])
                    X_r = self.poblacion[r].posicion_real
                    L = levy_flight(self.dimension)
                    alpha = random.gauss(0, 1)
                    R = round(0.5 * (0.5 + random.random()) * alpha)

                    # evadir depredadores en aire
                    Y = puffin.evadir_aire(X_r, L, R)
                    S = math.tan((random.random() - 0.5) * math.pi)

                    # depredación en picada
                    Z = puffin.dep_picada(Y, S)

                    Y = self.ajustar_limites(Y)
                    Z = self.ajustar_limites(Z)

                    Y_bin = reparar_solucion([binarizar_sigmoide(y) for y in Y], aristas)
                    Z_bin = reparar_solucion([binarizar_sigmoide(z) for z in Z], aristas)

                    candidatos.append((Y_bin, Y, funcion_objetivo(Y_bin)))
                    candidatos.append((Z_bin, Z, funcion_objetivo(Z_bin)))

            else:  # fase subacuática
                for i in range(self.num_puffins):
                    r2, r3 = random.sample([j for j in range(self.num_puffins) if j != i], 2)
                    X_r2 = self.poblacion[r2].posicion_real
                    X_r3 = self.poblacion[r3].posicion_real
                    F = 0.5

                    # recolección de comida
                    if random.random() >= 0.5:
                        L1 = levy_flight(self.dimension)
                        W = self.poblacion[i].recoleccion(X_r2, X_r3, F, L1)
                    else:
                        W = self.poblacion[i].recoleccion(X_r2, X_r3, F)

                    # intensificar búsqueda
                    f = 0.1 * (random.random() - 1) * (1 - (t / self.max_iter)) # factor adaptativo
                    Y = self.poblacion[i].intensificar(W, f)

                    r4, r5 = random.sample([j for j in range(self.num_puffins) if j != i], 2)
                    X_r4, X_r5 = self.poblacion[r4].posicion_real, self.poblacion[r5].posicion_real

                    # evadir depredadores en agua
                    if random.random() >= 0.5:
                        L2 = levy_flight(self.dimension)
                        Z = self.poblacion[i].evadir_agua(X_r4, X_r5, L=L2)
                    else:
                        beta = random.uniform(0, 1)
                        Z = self.poblacion[i].evadir_agua(X_r4, X_r5, beta=beta)

                    W = self.ajustar_limites(W)
                    Y = self.ajustar_limites(Y)
                    Z = self.ajustar_limites(Z)

                    W_bin = reparar_solucion([binarizar_sigmoide(w) for w in W], aristas)
                    Y_bin = reparar_solucion([binarizar_sigmoide(y) for y in Y], aristas)
                    Z_bin = reparar_solucion([binarizar_sigmoide(z) for z in Z], aristas)

                    candidatos.append((W_bin, W, funcion_objetivo(W_bin)))
                    candidatos.append((Y_bin, Y, funcion_objetivo(Y_bin)))
                    candidatos.append((Z_bin, Z, funcion_objetivo(Z_bin)))

            # se ordenan las posiciones candidatas respecto su valor en la función objetivo (desde menor a mayor)
            candidatos.sort(key=lambda x: x[1])

            # se dejan las primeras N (cantidad de puffins en la población) 
            for i in range(self.num_puffins):
                self.poblacion[i].posicion_binaria = candidatos[i][0]
                self.poblacion[i].posicion_real = candidatos[i][1]

            # se calcula los valores de la población evaluadas en la función objetivo y se define la mejor solución
            for puffin in self.poblacion:
                valor = self.funcion_objetivo(puffin.posicion_binaria)
                if valor < self.mejor_valor:
                    self.mejor_valor = valor
                    self.g_best_binario = puffin.posicion_binaria[:]
                    self.g_best_real = puffin.posicion_real[:]
                    
                    self.iteracion_mejor = t
                    self.tiempo_mejor = time.time() - tiempo_inicio

            self.historial_convergencia.append(self.mejor_valor)

            # Imprimir la iteración y el resultado de la mejor solución encontrada (g_best)
            print(f"Iteración {t} - Vértices cubiertos (g_best): {sum(self.g_best_binario)}")

        tiempo_total = time.time() - tiempo_inicio

        return self.g_best_binario, self.mejor_valor, tiempo_total

# ejecución principal
if __name__ == "__main__":

    benchmark_var = 2

    if(benchmark_var==1):
        ruta_archivo = "C:/Users/ricar/OneDrive/Escritorio/seminario/benchmark/C125-9.mtx"
    elif(benchmark_var==2):
        ruta_archivo = "C:/Users/ricar/OneDrive/Escritorio/seminario/benchmark/keller4.mtx"
    else:
        ruta_archivo = "C:/Users/ricar/OneDrive/Escritorio/seminario/benchmark/keller5.mtx"

    num_vertices = leer_vertices(ruta_archivo)
    aristas = leer_aristas(ruta_archivo)

    apo = APO(funcion_objetivo, num_puffins=10, dimension=num_vertices, lower_bound=-6, upper_bound=6, max_iter=100)

    mejor_sol, mejor_val, tiempo = apo.optimizar(aristas)

    # Output final
    print("\nMejor solución encontrada:", mejor_sol)
    print("Vértices seleccionados:", [i + 1 for i, v in enumerate(mejor_sol) if v == 1])
    print("Cobertura de vértices:", funcion_objetivo(mejor_sol), '\n')

    print(f"Mejor solución encontrada en iteración {apo.iteracion_mejor}\nMejor solución encontrada en el tiempo: {apo.tiempo_mejor} [s]")

    print("\nTiempo de ejecución total:", tiempo, "[s]\n")

    if(benchmark_var == 1):
        with open('C:/Users/ricar/OneDrive/Escritorio/seminario/resultados/apo/c125-9/resultados-c125-9.txt', 'a') as file:
            file.write(f"{apo.mejor_valor} - {apo.tiempo_mejor} - {tiempo}\n")
    elif(benchmark_var == 2):
        with open('C:/Users/ricar/OneDrive/Escritorio/seminario/resultados/apo/keller4/resultados-keller4.txt', 'a') as file:
            file.write(f"{apo.mejor_valor} - {apo.tiempo_mejor} - {tiempo}\n")
    else:
        with open('C:/Users/ricar/OneDrive/Escritorio/seminario/resultados/apo/keller5/resultados-keller5.txt', 'a') as file:
            file.write(f"{apo.mejor_valor} - {apo.tiempo_mejor} - {tiempo}\n")


    #Grafica de convergencia
    plt.plot(apo.historial_convergencia)
    plt.title('Convergencia del algoritmo APO')
    plt.xlabel('Iteraciones')
    plt.ylabel('Valor de la función objetivo')
    plt.show()
