import matplotlib.pyplot as plt

# Función para leer los resultados del archivo
def leer_resultados(algoritmo, benchmark):
    # Rutas de los archivos según el algoritmo y benchmark seleccionados
    ruta_archivo = f"C:/Users/ricar/OneDrive/Escritorio/seminario/resultados/{algoritmo}/{benchmark}/{algoritmo}_ejecucion.txt"
    
    iteraciones = []
    fitness = []
    
    try:
        with open(ruta_archivo, 'r') as f:
            for line in f:
                # El formato es "x - y", donde x es la iteración y y es el fitness
                partes = line.strip().split(" - ")
                iteraciones.append(int(partes[0]))  # Iteración (x)
                fitness.append(float(partes[1]))  # Fitness (y)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo para {algoritmo} en el benchmark {benchmark}")
    
    return iteraciones, fitness

# Función para graficar los resultados de convergencia
def graficar_convergencia(benchmark_selector):
    # Definir los benchmarks disponibles
    benchmarks = {1: "c125-9", 2: "keller4", 3: "keller5"}
    
    # Seleccionar el benchmark según la entrada
    if benchmark_selector not in benchmarks:
        print("Benchmark inválido. Elige 1, 2 o 3.")
        return
    
    benchmark = benchmarks[benchmark_selector]
    
    # Leer los resultados de los tres algoritmos para el benchmark seleccionado
    iter_pso, fitness_pso = leer_resultados("pso", benchmark)
    iter_ga, fitness_ga = leer_resultados("ga", benchmark)
    iter_apo, fitness_apo = leer_resultados("apo", benchmark)
    
    # Graficar los resultados
    plt.plot(iter_pso, fitness_pso, label="PSO", linestyle='-', color='b')
    plt.plot(iter_ga, fitness_ga, label="GA", linestyle='--', color='g')
    plt.plot(iter_apo, fitness_apo, label="APO", linestyle='-.', color='r')

    # Configuración del gráfico
    plt.xlabel("Iteraciones")
    plt.ylabel("Fitness")
    plt.title(f"Convergencia de los Algoritmos en el Benchmark {benchmark}")
    plt.legend()
    plt.grid(True)

    # Mostrar la gráfica
    plt.show()

# Llamada a la función de graficado para el benchmark que elijas
benchmark_selector = 3  # Cambia este valor a 1, 2 o 3 para seleccionar el benchmark
graficar_convergencia(benchmark_selector)
