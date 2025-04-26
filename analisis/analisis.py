
import pandas as pd
import matplotlib.pyplot as plt
import os

# Variables de archivo
benchmark = 1    # 1.- C125-9, 2.- keller4, 3.- keller5
algoritmos= [1, 2, 3]  # 1.- PSO, 2.- GA, 3.- APO, [4.- APO+IL]

# Rutas de los resultados para cada algoritmo
rutas = {
    (1, 1): 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\pso\\c125-9\\resultados-c125-9.txt',
    (1, 2): 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\ga\\c125-9\\resultados-c125-9.txt',
    (1, 3): 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\apo\\c125-9\\resultados-c125-9.txt',
    (2, 1): 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\pso\\keller4\\resultados-keller4.txt',
    (2, 2): 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\ga\\keller4\\resultados-keller4.txt',
    (2, 3): 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\apo\\keller4\\resultados-keller4.txt',
    (3, 1): 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\pso\\keller5\\resultados-keller5.txt',
    (3, 2): 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\ga\\keller5\\resultados-keller5.txt',
    (3, 3): 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\apo\\keller5\\resultados-keller5.txt'
}

# Crear un diccionario para almacenar los resultados de los algoritmos
data_dict = {}

# Definir el nombre del benchmark
benchmark_names = {1: 'c125-9', 2: 'keller4', 3: 'keller5'}
benchmark_name = benchmark_names.get(benchmark, 'unknown')

# Leer los resultados de los algoritmos
for algoritmo in algoritmos:

    if(algoritmo==1):
        alg = 'pso'
    elif(algoritmo==2):
        alg = 'ga'
    else:
        alg = "apo"
        
    ruta = rutas[(benchmark, algoritmo)]
    data = pd.read_csv(ruta, sep=" - ", header=None, names=["Fitness", "Tiempo_fitness", "Tiempo_total"], skiprows=1)
    data_dict[algoritmo] = data
    
    # Crear la ruta para guardar el archivo .txt directamente en 'resultados'
    resultado_dir = f'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados'
    if not os.path.exists(resultado_dir):
        os.makedirs(resultado_dir)  # Crear el directorio 'resultados' si no existe

    # Guardar la descripción en un archivo .txt dentro de 'resultados'
    describe_filename = os.path.join(resultado_dir, f'data_describe_{benchmark_names.get(benchmark)}_{alg}.txt')
    with open(describe_filename, 'w') as f:
        f.write(str(data.describe()))  # Guardar la descripción como texto en el archivo .txt

    print(f'Descripción guardada en: {describe_filename}')

# Crear la carpeta resultados si no existe
resultados_path = f'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados'
if not os.path.exists(resultados_path):
    os.makedirs(resultados_path)

# Función para generar el boxplot y guardarlo en el directorio
def generar_boxplot(data_dict, columna, titulo, ylabel, filename):
    plt.figure(figsize=(10, 6))
    plt.boxplot([data_dict[alg]['Fitness'] for alg in algoritmos] if columna == 'Fitness' else
                [data_dict[alg]['Tiempo_fitness'] for alg in algoritmos] if columna == 'Tiempo_fitness' else
                [data_dict[alg]['Tiempo_total'] for alg in algoritmos], labels=['PSO', 'GA', 'APO'])
    plt.title(titulo)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(os.path.join(resultados_path, filename))  # Guardar en el directorio
    plt.show()

if(benchmark==1):
    complemento_titulo = " [C125-9]"
elif(benchmark==2):
    complemento_titulo = " [keller4]"
else:
    complemento_titulo = " [keller5]"

# Boxplot para Fitness
generar_boxplot(data_dict, 'Fitness', 'Distribución del Fitness encontrado'+complemento_titulo, 'Fitness', f'boxplot_fitness_{benchmark_name}.png')

# Boxplot para Tiempo de ejecución para encontrar Fitness
generar_boxplot(data_dict, 'Tiempo_fitness', 'Distribución del Tiempo de ejecución para encontrar el Fitness'+complemento_titulo, 'Tiempo (s)', f'boxplot_tiempo_fitness_{benchmark_name}.png')

# Boxplot para Tiempo total del algoritmo
generar_boxplot(data_dict, 'Tiempo_total', 'Distribución del Tiempo de ejecución Total del Algoritmo'+complemento_titulo, 'Tiempo (s)', f'boxplot_tiempo_total_{benchmark_name}.png')
