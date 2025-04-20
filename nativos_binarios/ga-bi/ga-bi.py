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

# Clase cromosoma
class Cromosoma:
    def __init__(self, longitud_cromosoma=None, solucion=None):
        if solucion is None:
            # generar un cromosoma aleatorio, al inicio de la ejecución cuando se crea la población
            self.solucion = [random.choice([0, 1]) for _ in range(longitud_cromosoma)]
        else:
            self.solucion = solucion

        self.vertices_cubiertos = self.calcular_fitness()

    def calcular_fitness(self):
        return sum(self.solucion) # retorna la suma de los vértices cubiertos → 1's en array "solucion"


# Clase del algoritmo genético
class GA:
    def __init__(self, tamanio_poblacion, longitud_cromosoma, max_iteraciones, prob_cruce, prob_mutacion, aristas, num_vertices):
        self.tamanio_poblacion = tamanio_poblacion
        self.longitud_cromosoma = longitud_cromosoma
        self.max_iteraciones = max_iteraciones
        self.prob_cruce = prob_cruce
        self.prob_mutacion = prob_mutacion
        self.aristas = aristas 
        self.num_vertices = num_vertices 
        self.poblacion = self.generar_poblacion_inicial()

        self.iteraciones = [] # [iteracion, mejor_solucion]
        self.mejor_cromosoma = None

    def generar_poblacion_inicial(self):
        """Genera la población inicial, asegurando que todas las soluciones son factibles"""

        cromosomas = 0
        poblacion = []

        while(cromosomas < self.tamanio_poblacion):
            c = Cromosoma(longitud_cromosoma=self.longitud_cromosoma)

            self.verificacionVertexCover(c, self.aristas)

            poblacion.append(c)
            cromosomas = cromosomas+1

        return poblacion
    
    def verificacionVertexCover(self, cromosoma, aristas):
        """Funcion que verifica si la solución cubre todas las aristas del grafo (Vertex Cover), y la repara de ser necesario"""

        # Itera sobre cada arista
        for v1, v2 in aristas:
            # Si ambos vértices están sin cubrir
            if (cromosoma.solucion[v1-1] == 0 and cromosoma.solucion[v2-1] == 0):
                # Elegir aleatoriamente entre v1 y v2 para cubrirlo
                vertice_a_cubrir = random.choice([v1])
                # Poner un 1 en el vértice elegido
                cromosoma.solucion[vertice_a_cubrir-1] = 1

    def mejorCromosoma(self, poblacion):
        min_fitness = min(cromosoma.calcular_fitness() for cromosoma in poblacion) # se rescata el fitness mínimo de la población
        mejores_cromosomas = [cromosoma for cromosoma in poblacion if cromosoma.calcular_fitness() == min_fitness] # se eligen los cromosomas con el fitness mínimo
        return random.choice(mejores_cromosomas) # si hay más de un cromosoma con el mismo fitness, se elige uno de forma aleatoria

    def seleccion_por_ruleta(self):
        '''Cromosomas padres son escogidos en función de su probabilidad proporcional a su fitness'''
        total_fitness = sum(cromosoma.calcular_fitness() for cromosoma in self.poblacion) # suma de fitness de todos los cromosomas
        probabilidad = [cromosoma.calcular_fitness() / total_fitness for cromosoma in self.poblacion] # calcular probabilidades de selección
        seleccionados = random.choices(self.poblacion, weights=probabilidad, k=2) # selección basada en su probabilidad
        return seleccionados # retorna los padres de la nueva poblacion 
    
    def cruce(self, cromosoma1, cromosoma2):
        """Se realiza el cruce de un punto respecto a un índice aleatorio"""
        indice_aleatorio = random.randint(1, self.num_vertices) # para definir el indice de cruce en las soluciones de los cromosomas
        hijo1 = Cromosoma(solucion=cromosoma1.solucion[:indice_aleatorio] + cromosoma2.solucion[indice_aleatorio:])
        hijo2 = Cromosoma(solucion=cromosoma2.solucion[:indice_aleatorio] + cromosoma1.solucion[indice_aleatorio:])
        # se verifica si las soluciones son factibles en contexto de Cobertura de Vértices y las repara si es necesario
        self.verificacionVertexCover(hijo1, self.aristas)
        self.verificacionVertexCover(hijo2, self.aristas)
        return hijo1, hijo2
    
    def mutacion(self):
        punto1 = random.randint(1, self.num_vertices)
        while(True):
            punto2 = random.randint(1, self.num_vertices)
            if(punto1 != punto2):
                break
        for cromosoma in self.poblacion:
            cromosoma.solucion[punto1-1] = 1 if cromosoma.solucion[punto1-1] == 0 else 0
            cromosoma.solucion[punto2-1] = 1 if cromosoma.solucion[punto2-1] == 0 else 0
            self.verificacionVertexCover(cromosoma, self.aristas) # se verifica si la solucion nueva por mutacion es una cobertura de vértices, y la repara de ser necesario

    def evolucionar(self):

        self.mejor_cromosoma = self.mejorCromosoma(self.poblacion) # se define el mejor cromosoma de la población inicial
        
        # resultado inicial
        print("\n--- RESULTADO INICIAL ---")
        print("→ Mejor solución:\n", self.mejor_cromosoma.solucion)
        print("→ Cobertura (vértices):", self.mejor_cromosoma.calcular_fitness())
        print("→ Vértices seleccionados:\n", [i + 1 for i, v in enumerate(self.mejor_cromosoma.solucion) if v == 1], "\n")

        nueva_poblacion = []

        print("--- ITERACIONES ---")

        for i in range(1, self.max_iteraciones+1):
            # seleccion de cromosomas que dará la siguiente población (de sus hijos)
            padres = self.seleccion_por_ruleta()

            # cruce (cruce de un punto)
            r1 = random.random() # valor que define la probabilidad de que exista cruce de los cromosomas seleccionados
            if(r1 < self.prob_cruce):
                """La siguiente generación estará dada por el cruce de los cromosomas seleccionados"""
                while(len(nueva_poblacion) < self.tamanio_poblacion):
                    hijos = self.cruce(padres[0], padres[1])
                    for hijo in hijos:
                        nueva_poblacion.append(hijo)
                self.poblacion = nueva_poblacion

            # mutacion (en dos puntos de la solución)
            r2 = random.random() # valor que define la probabilidad de que exista mutacion en la población
            if(r2 < self.prob_mutacion):
                self.mutacion()

            # guardar mejor cromosoma
            nuevo_mejor = self.mejorCromosoma(self.poblacion)
            if(nuevo_mejor.calcular_fitness() < self.mejor_cromosoma.calcular_fitness()):
                self.mejor_cromosoma = Cromosoma(solucion=nuevo_mejor.solucion[:])  # copia del nuevo mejor cromosoma

            print(f'Iteración: {i} - Fitness global (vértices cubiertos): {self.mejor_cromosoma.calcular_fitness()}')

        # Resultado final
        print("\n--- RESULTADO FINAL ---")
        print("→ Mejor solución:\n", self.mejor_cromosoma.solucion)
        print("→ Cobertura (vértices):", self.mejor_cromosoma.calcular_fitness())
        print("→ Vértices seleccionados:\n", [i + 1 for i, v in enumerate(self.mejor_cromosoma.solucion) if v == 1], "\n")


if __name__ == "__main__":
    ruta_archivo = "C:/Users/ricar/OneDrive/Escritorio/seminario/benchmark/C125-9.mtx"
    cantidad_vertices = leer_vertices(ruta_archivo)  
    aristas = leer_aristas(ruta_archivo)  

    tamanio_poblacion = 5
    longitud_cromosoma = cantidad_vertices  # Número de vértices
    max_iteraciones = 100
    prob_cruce = 0.8
    prob_mutacion = 0.07

    ga = GA(tamanio_poblacion, longitud_cromosoma, max_iteraciones, prob_cruce, prob_mutacion, aristas, cantidad_vertices)
    ga.evolucionar()
