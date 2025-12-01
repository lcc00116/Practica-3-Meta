# --- GreedyAleatorio.py ---
import random
from Archivodedatos import lector
from Configurador import load_config
from Greedy import maximizar_flujos, minimizar_distancias, calcular_coste


def generar_asignaciones_aleatorias(flujos_ordenados, distancias_ordenadas, tam, k, seed=None):
    """Genera asignaciones usando el Greedy Aleatorio con factor k"""
    rnd = random.Random(seed)

    asignaciones = [0] * tam
    #Hacemos copia de las matrices (así no modificamos las originales)
    unidades_disp = flujos_ordenados.copy()
    locs_disp = distancias_ordenadas.copy()

    while unidades_disp:
        #Escogemos las k primeras posiciones
        k_unidades = unidades_disp[:min(k, len(unidades_disp))]
        k_locs = locs_disp[:min(k, len(locs_disp))]

        #Escogemos un valor aleatorio de los k seleccionados
        unidad_elegida = rnd.choice(k_unidades)
        loc_elegida = rnd.choice(k_locs)

        asignaciones[unidad_elegida[0] - 1] = loc_elegida[0]

        #Borramos la selección para evitar repetidos
        unidades_disp.remove(unidad_elegida)
        locs_disp.remove(loc_elegida)

    return asignaciones


def procesar_greedy_aleatorio(datos, k, seed=None):
    """Función principal: ejecuta el Greedy Aleatorio completo"""
    tam = datos.tam
    flujos_ordenados = maximizar_flujos(datos.mat1, tam)
    distancias_ordenadas = minimizar_distancias(datos.mat2, tam)

    asignaciones = generar_asignaciones_aleatorias(
        flujos_ordenados, distancias_ordenadas, tam, k, seed
    )
    coste = calcular_coste(datos.mat1, datos.mat2, asignaciones)
    return flujos_ordenados, distancias_ordenadas, asignaciones, coste


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


if __name__ == "__main__":
    config = load_config('config.txt')
    fac_aleatoriedad = config['Factor_aleatoriedad'] if config else 2

    datos = lector("ford01.dat")
    flujos, distancias, asignaciones, coste = procesar_greedy_aleatorio(
        datos, fac_aleatoriedad
    )
    mostrar_resultados(flujos, distancias, asignaciones, coste)
