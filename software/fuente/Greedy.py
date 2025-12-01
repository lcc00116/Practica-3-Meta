from Archivodedatos import lector

def maximizar_flujos(mat1, tam):
    """Calcula y ordena de mayor a menor la suma de los flujos"""
    # Creamos lista de tuplas (etiqueta, suma) con enumerate para obtener el índice
    flujos = [(i + 1, sum(fila)) for i, fila in enumerate(mat1)]
    # Ordenamos de mayor a menor por la suma (x[1])
    return sorted(flujos, key=lambda x: x[1], reverse=True)

def minimizar_distancias(mat2, tam):
    """Calcula y ordena de menor a mayor la suma de las distancias"""
    distancias = [(i + 1, sum(fila)) for i, fila in enumerate(mat2)]
    return sorted(distancias, key=lambda x: x[1])

def asignar_fabricas_localizaciones(flujos_ordenados, distancias_ordenadas, tam):
    """Asigna a cada fábrica la localización correspondiente"""
    asignaciones = [0] * tam
    for k in range(tam):
        # Obtenemos la etiqueta de la fábrica (U1, U2...)
        fabrica_etiqueta = flujos_ordenados[k][0]
        fabrica_idx = fabrica_etiqueta - 1  #Pasamos de etiqueta a índice (0-based)
        # Obtenemos la etiqueta de localización correspondiente
        loc_etiqueta = distancias_ordenadas[k][0]
        asignaciones[fabrica_idx] = loc_etiqueta
    return asignaciones

def calcular_coste(mat1, mat2, asignaciones):
    """Calcula el coste total de la solución"""
    coste = 0
    n = len(asignaciones)
    for i in range(n):
        for j in range(n):
            flujo = mat1[i][j]
            loc_i = asignaciones[i] - 1  # pasamos de etiqueta a índice
            loc_j = asignaciones[j] - 1
            distancia = mat2[loc_i][loc_j]
            coste += flujo * distancia
    return coste

def mostrar_resultados(flujos_ordenados, distancias_ordenadas, asignaciones, coste):
    """Muestra los resultados"""
    print("Sum F =", end=" ")
    for etiqueta, valor in flujos_ordenados:
        print(f"(U{etiqueta}, {valor})", end=" ")
    print()

    print("Sum D =", end=" ")
    for etiqueta, valor in distancias_ordenadas:
        print(f"(L{etiqueta}, {valor})", end=" ")
    print()

    print("Sol:", tuple(asignaciones))
    print("Coste:", coste)

def procesar_greedy(datos):
    """Función principal que llama a las demás"""
    tam = datos.tam
    flujos_ordenados = maximizar_flujos(datos.mat1, tam)
    distancias_ordenadas = minimizar_distancias(datos.mat2, tam)
    asignaciones = asignar_fabricas_localizaciones(flujos_ordenados, distancias_ordenadas, tam)
    coste = calcular_coste(datos.mat1, datos.mat2, asignaciones)
    return flujos_ordenados, distancias_ordenadas, asignaciones, coste

if __name__ == "__main__":
    datos = lector("ford01.dat")
    flujos_ordenados, distancias_ordenadas, asignaciones, coste = procesar_greedy(datos)
    mostrar_resultados(flujos_ordenados, distancias_ordenadas, asignaciones, coste)