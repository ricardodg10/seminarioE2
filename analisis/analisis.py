import pandas as pd
import matplotlib.pyplot as plt

# variables de archivo
benchmark = 3      # 1.- C125-9, 2.- keller4, 3.- keller5
algoritmo = 3     # 1.- PSO, 2.- GA, 3.- APO, [4.- APO+IL]

# rutas
if(benchmark==1 and algoritmo==1):
    ruta = 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\pso\\c125-9\\resultados-c125-9.txt'
    complemento_titulo = ' [PSO , C125-9]'
elif(benchmark==1 and algoritmo==2):
    ruta = 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\ga\\c125-9\\resultados-c125-9.txt'
    complemento_titulo = ' [GA , C125-9]'
elif(benchmark==1 and algoritmo==3):
    ruta = 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\apo\\c125-9\\resultados-c125-9.txt'
    complemento_titulo = ' [APO , C125-9]'
elif(benchmark==2 and algoritmo==1):
    ruta = 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\pso\\keller4\\resultados-keller4.txt'
    complemento_titulo = ' [PSO , keller4]'
elif(benchmark==2 and algoritmo==2):
    ruta = 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\ga\\keller4\\resultados-keller4.txt'
    complemento_titulo = ' [GA , keller4]'
elif(benchmark==2 and algoritmo==3):
    ruta = 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\apo\\keller4\\resultados-keller4.txt'
    complemento_titulo = ' [APO , keller4]'
elif(benchmark==3 and algoritmo==1):
    ruta = 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\pso\\keller5\\resultados-keller5.txt'
    complemento_titulo = ' [PSO , keller5]'
elif(benchmark==3 and algoritmo==2):
    ruta = 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\ga\\keller5\\resultados-keller5.txt'
    complemento_titulo = ' [GA , keller5]'
else:
    ruta = 'C:\\Users\\ricar\\OneDrive\\Escritorio\\seminario\\resultados\\apo\\keller5\\resultados-keller5.txt'
    complemento_titulo = ' [APO , keller5]'

# leer archivo
data = pd.read_csv(ruta, sep=" - ", header=None, names=["Fitness", "Tiempo_fitness", "Tiempo_total"], skiprows=1)
# descripción de la data
print(data.describe())

# variables gráfica boxplot
titulo_fitness = 'Distribución del Fitness entre las ejecuciones'
titulo_tiempo_fitness = 'Distribución del Tiempo de ejecución para encontrar el Fitness'
titulo_tiempo_total = "Distribución del Tiempo Total del Algoritmo"
# variables gráfica histogramas
titulo_histograma = 'Histograma de Fitness'

'''
# Boxplot (fitness)
plt.figure(figsize=(10,6))
data.boxplot(column=["Fitness"])
plt.title(titulo_fitness + complemento_titulo)
plt.ylabel("Fitness")
plt.show()

# Boxplot (tiempo para encontrar fitness)
plt.figure(figsize=(10,6))
data.boxplot(column=["Tiempo_fitness"])
plt.title(titulo_tiempo_fitness+ complemento_titulo)
plt.ylabel("Tiempo (s)")
plt.show()

# Boxplot (tiempo de ejecución total)
plt.figure(figsize=(10,6))
data.boxplot(column=["Tiempo_total"])
plt.title(titulo_tiempo_total+ complemento_titulo)
plt.ylabel("Tiempo (s)")
plt.show()

# Histograma
plt.hist(data['Fitness'], bins=10, color='skyblue', edgecolor='black')
plt.title(titulo_histograma + complemento_titulo)
plt.xlabel('Fitness')
plt.ylabel('Frecuencia')
plt.show()

'''