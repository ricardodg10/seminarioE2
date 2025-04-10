import random       # para las variables aletorias del algoritmo
import time         # para tiempo de ejecucion

class Particula:
    # inicializacion de la partícula con dimension del espacio, los limites del espacio de busqueda (lower bound LB y upper bound UB)
    def __init__(self, dimension, LB, UB):
        self.dimension = dimension  # dimension del espacio 
        self.lower_bound = LB       # limite inferior
        self.upper_bound = UB       # limite superior
        
        # generar vectores posicion y velocidad aleatoria dentro del rango [LB, UB]^D, donde D corresponde a la dimension del problema
        # vectores aleatorios distribuidos uniformemente en el rango definido
        self.posicion = [random.uniform(LB, UB) for _ in range(dimension)] 
        self.velocidad = [random.uniform(LB, UB) for _ in range(dimension)]
        
        # asignacion de la mejor posicion personal de la particula (p_best)
        self.p_best = self.posicion.copy()  # la mejor posición es la inicial
        self.p_best_valor = float('inf')    # valor alto al principio, para minimizarlo

    def actualizar_velocidad(self, g_best, w, c1, c2):
        # actualizacion de la velocidad de la particula en base a los coeficientes definidos

        '''
        w: peso de inercia
        c1: coeficiente de aceleración (cognitiva), para la mejor posicion personal
        c2: coeficiente de aceleración (social), para la mejor posicion global
        '''

        # valores randomicos distribuidos uniformemente entre 0 y 1
        r1 = random.random()
        r2 = random.random()

        for i in range(self.dimension):
            # fórmula para la actualización de la velocidad
            impulso = w * self.velocidad[i]                             # impulso
            cognitiva = c1 * r1 * (self.p_best[i] - self.posicion[i])   # parte cognitiva
            social = c2 * r2 * (g_best[i] - self.posicion[i])           # parte social
            self.velocidad[i] = impulso + cognitiva + social            # actualización

    def actualizar_posicion(self):
        # actualiza la posición de la partícula basándose en su velocidad.

        for i in range(self.dimension):
            self.posicion[i] += self.velocidad[i]

            # limitar la posición a los límites establecidos (lower bound, upper bound)
            self.posicion[i] = max(self.lower_bound, min(self.posicion[i], self.upper_bound))

    def evaluar(self, funcion_objetivo):
        #evalúa el valor de la función objetivo en la posición actual de la partícula.
        
        valor = funcion_objetivo(self.posicion)
        
        # si la nueva posición es mejor, se actualiza la mejor personal (p_best)
        if valor < self.p_best_valor:
            self.p_best_valor = valor
            self.p_best = self.posicion.copy()

        return valor


class PSO:
    #se inicializa el algoritmo PSO
    def __init__(self, funcion_objetivo, num_particulas, dimension, lower_bound, upper_bound, max_iter, w=0.5, c1=2.5, c2=2.5):

        """
        funcion objetivo: función objetivo del problema a optimizar
        num_particulas: número de partículas en el enjambre
        dimension: dimensió del problema
        lower_bound: límite inferior para las posiciones
        upper_bound: límite superior para las posiciones
        max_iter: número de iteraciones
        w: peso de inercia
        c1: coeficiente de aceleración (cognitiva), para la mejor posicion personal
        c2: coeficiente de aceleración (social), para la mejor posicion global
        """

        self.funcion_objetivo = funcion_objetivo
        self.num_particulas = num_particulas
        self.dimension = dimension
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.max_iter = max_iter
        self.w = w
        self.c1 = c1
        self.c2 = c2
        
        # crear el enjambre (se crea la cantidad de particulas correspondientes al número de particulas establecido)
        self.enjambre = [Particula(dimension, lower_bound, upper_bound) for _ in range(num_particulas)]
        
        # Inicializar el mejor global (gbest) con valores altos
        self.g_best = [random.uniform(lower_bound, upper_bound) for _ in range(dimension)]
        self.g_best_valor = float('inf')
    
    # ejecutar PSO para encontrar la mejor solución
    def optimizar(self):

        tiempo_inicio = time.time()

        for iteracion in range(1, self.max_iter+1):
            for particula in self.enjambre:
                # Evaluar la partícula
                valor = particula.evaluar(self.funcion_objetivo)

                # Actualizar el mejor global si es necesario
                if valor < self.g_best_valor:
                    self.g_best_valor = valor
                    self.g_best = particula.posicion.copy()

            # Actualizar las velocidades y posiciones de las partículas
            for particula in self.enjambre:
                particula.actualizar_velocidad(self.g_best, self.w, self.c1, self.c2)
                particula.actualizar_posicion()

            print(f'Iteración: {iteracion}. Mejor posicion: {self.g_best}. Mejor valor: {self.g_best_valor} . ')
        
        return self.g_best, self.g_best_valor, tiempo_inicio


# definir funcion objetivo (ej: funcion cuadrática)
def funcion_objetivo(posicion):
    return sum(x for x in posicion)  # suma de los valores en el vector posicion de la particula

if __name__ == "__main__":
    # para inicializar PSO con valores dados
    pso = PSO(funcion_objetivo, num_particulas=5, dimension=2, lower_bound=-10, upper_bound=10, max_iter=100)

    # ejecutar la optimizacion y obtener la mejor solución (vector posicion y valor de la solucion)
    g_best, g_best_valor, tiempo_inicial = pso.optimizar()
    tiempo_total = time.time() - tiempo_inicial

    print("\nMejor posición encontrada:", g_best)
    print("Valor de la función objetivo:", g_best_valor)
    print("Tiempo de ejecución: ", tiempo_total, "[s]\n")
