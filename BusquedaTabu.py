
import random
from collections import deque
from GreedyAleatorio import procesar_greedy_aleatorio
from Greedy import calcular_coste
from Archivodedatos import lector
from Configurador import load_config
from BusquedaLocal import calcular_delta_coste


# --- BusquedaTabu.py ---
import random
from collections import deque
# Importaciones de módulos locales del proyecto
from GreedyAleatorio import procesar_greedy_aleatorio  # Para generar la solución inicial
from Greedy import calcular_coste  # Para calcular el coste de una asignación
from Archivodedatos import lector  # Para leer los datos del problema
from Configurador import load_config  # Para cargar la configuración


def calcular_delta_coste(mat1, mat2, asignaciones, i, j):
    """
    Calcula el cambio en el coste al intercambiar las asignaciones de las ubicaciones i y j.
    
    Esta función utiliza factorización para calcular eficientemente el cambio en el coste
    sin necesidad de recalcular todo el coste de la solución. Solo se calculan las 
    contribuciones que cambian al intercambiar las asignaciones.
    
    Args:
        mat1: Matriz de distancias entre ubicaciones
        mat2: Matriz de flujos entre instalaciones
        asignaciones: Lista actual de asignaciones (instalación -> ubicación)
        i, j: Índices de las ubicaciones a intercambiar
        
    Returns:
        delta: Cambio en el coste total si se realiza el intercambio
    """
    n = len(asignaciones)
    delta = 0

    # Iterar sobre todas las otras ubicaciones para calcular el impacto del intercambio
    for k in range(n):
        if k != i and k != j:
            # Obtener las instalaciones asignadas (convertir a índices base 0)
            li = asignaciones[i] - 1  # Instalación asignada a ubicación i
            lj = asignaciones[j] - 1  # Instalación asignada a ubicación j  
            lk = asignaciones[k] - 1  # Instalación asignada a ubicación k

            # Calcular la diferencia en coste por intercambiar i y j
            # Considera tanto las conexiones de i->k como de k->i
            delta += (mat1[i][k] - mat1[j][k]) * (mat2[lj][lk] - mat2[li][lk])
            delta += (mat1[k][i] - mat1[k][j]) * (mat2[lk][lj] - mat2[lk][li])

    return delta


def busqueda_tabu(mat1, mat2, asignaciones_inicial, max_iter=5000, tenencia_tabu=3, oscilacion_estrategica=0.50, estancamiento=0.05):
    """
    Implementa el algoritmo de Búsqueda Tabú para resolver el problema de asignación cuadrática.
        
    Args:
        mat1: Matriz de distancias entre ubicaciones
        mat2: Matriz de flujos entre instalaciones  
        asignaciones_inicial: Solución inicial
        max_iter: Número máximo de iteraciones
        tenencia_tabu: Tamaño de la lista tabú
        oscilacion_estrategica: Probabilidad de intensificar vs diversificar
        estancamiento: Porcentaje de iteraciones sin mejora para activar oscilación
        
    Returns:
        Tupla (mejor_asignaciones, mejor_coste)
    """
    # ===== INICIALIZACIÓN =====
    n = len(asignaciones_inicial)
    asignaciones = list(asignaciones_inicial)  # Solución actual
    coste_actual = calcular_coste(mat1, mat2, asignaciones)

    # Mejor solución encontrada hasta ahora
    mejor_asignaciones = list(asignaciones)
    mejor_coste = coste_actual

    # Don't Look Bits: optimización para evitar examinar movimientos que no mejoran
    dlb = [0] * n  # 0 = examinar, 1 = no examinar
    
    # Lista tabú: almacena los intercambios prohibidos temporalmente
    tabu = deque(maxlen=tenencia_tabu)

    # Matriz de frecuencias: cuenta cuántas veces cada instalación se asigna a cada ubicación
    frec = [[0] * n for _ in range(n)]

    # Contadores para el control del algoritmo
    iteraciones = 0
    no_mejora = 0  # Iteraciones consecutivas sin mejora
    max_no_mejora = int(max_iter * estancamiento)  # Umbral para activar oscilación estratégica

    # Factor de penalización/bonificación para la oscilación estratégica
    rho = 1.0

    # ===== BUCLE PRINCIPAL =====
    while iteraciones < max_iter:
        mejora = False  # Flag para indicar si se encontró un movimiento de mejora
        
        # Variables para tracking del mejor movimiento no-mejora (cuando no hay mejoras disponibles)
        best_delta = float('inf')     # Mejor delta encontrado
        mejor_efectivo = float('inf') # Mejor delta efectivo (incluyendo penalizaciones/bonificaciones)
        mejor_i = -1                  # Mejor par (i,j) para intercambiar
        best_j = -1

        # ===== OSCILACIÓN ESTRATÉGICA =====
        # Se activa cuando llevamos muchas iteraciones sin mejora
        activar_osci = (no_mejora > max_no_mejora)
        intensifi = None
        if activar_osci:
            # Decidir aleatoriamente entre intensificar o diversificar
            intensifi = random.random() < oscilacion_estrategica

        # ===== EXPLORACIÓN DEL VECINDARIO =====
        # Examinar todos los posibles intercambios de ubicaciones
        for i in range(n):
            # Don't Look Bits: si dlb[i] == 1, saltamos esta ubicación
            if dlb[i] == 1:
                continue
                
            flag_mejora = False  # Flag para esta ubicación específica
            
            for j in range(i + 1, n):
                # Calcular el cambio en coste por intercambiar ubicaciones i y j
                delta = calcular_delta_coste(mat1, mat2, asignaciones, i, j)
                
                # ===== CRITERIOS TABÚ Y ASPIRACIÓN =====
                pair = (min(i, j), max(i, j))  # Par ordenado para la lista tabú
                is_tabu = pair in tabu          # ¿Está este intercambio prohibido?
                aspiration = (coste_actual + delta < mejor_coste)  # ¿Mejora la mejor solución conocida?
                
                # Si el movimiento es tabú y no cumple el criterio de aspiración, saltarlo
                if is_tabu and not aspiration:
                    continue

                # ===== CALCULAR DELTA EFECTIVO (con oscilación estratégica) =====
                # Índices de las nuevas ubicaciones después del intercambio
                new_loc_idx_i = asignaciones[j] - 1  # Nueva ubicación para instalación i
                new_loc_idx_j = asignaciones[i] - 1  # Nueva ubicación para instalación j
                
                cambio_coste = delta  # Por defecto, usar el delta normal
                
                if activar_osci:
                    # Calcular la suma de frecuencias para las nuevas asignaciones
                    frec_sum = frec[i][new_loc_idx_i] + frec[j][new_loc_idx_j]
                    
                    if intensifi:
                        # INTENSIFICACIÓN: Favorecer movimientos a ubicaciones frecuentes (explotar)
                        cambio_coste = delta - rho * frec_sum
                    else:
                        # DIVERSIFICACIÓN: Penalizar movimientos a ubicaciones frecuentes (explorar)
                        cambio_coste = delta + rho * frec_sum

                # ===== PROCESAMIENTO DEL MOVIMIENTO =====
                if delta < 0:
                    # MOVIMIENTO DE MEJORA: aplicarlo inmediatamente (First Improvement)
                    asignaciones[i], asignaciones[j] = asignaciones[j], asignaciones[i]
                    coste_actual += delta
                    
                    # Añadir el intercambio a la lista tabú
                    tabu.append(pair)
                    
                    # Actualizar matriz de frecuencias para toda la solución actual
                    for k in range(n):
                        frec[k][asignaciones[k] - 1] += 1
                    
                    # Resetear Don't Look Bits para las ubicaciones intercambiadas
                    dlb[i] = dlb[j] = 0
                    
                    # Marcar que encontramos una mejora
                    flag_mejora = True
                    mejora = True
                    iteraciones += 1
                    
                    # Actualizar la mejor solución si es necesario
                    if coste_actual < mejor_coste:
                        mejor_coste = coste_actual
                        mejor_asignaciones = list(asignaciones)
                        no_mejora = 0  # Reiniciar contador de no mejora
                    else:
                        no_mejora += 1
                        
                    break  # Salir del bucle j (First Improvement)
                else:
                    # MOVIMIENTO SIN MEJORA: guardar el mejor de los peores para usar si es necesario
                    if cambio_coste < mejor_efectivo:
                        mejor_efectivo = cambio_coste
                        best_delta = delta
                        mejor_i = i
                        best_j = j

            # Si no se encontró mejora para esta ubicación i, activar Don't Look Bit
            if not flag_mejora:
                dlb[i] = 1
                
            # Si encontramos alguna mejora, reiniciar el bucle externo (First Improvement)
            if mejora:
                break

        # ===== MANEJO DE ITERACIONES SIN MEJORA =====
        if not mejora:
            # Si no encontramos ningún movimiento de mejora, aplicar el mejor movimiento de empeoramiento
            if mejor_i != -1:
                i = mejor_i
                j = best_j
                delta = best_delta
                
                # Aplicar el mejor movimiento de empeoramiento
                asignaciones[i], asignaciones[j] = asignaciones[j], asignaciones[i]
                coste_actual += delta
                
                # Añadir a la lista tabú
                pair = (min(i, j), max(i, j))
                tabu.append(pair)
                
                # Actualizar matriz de frecuencias
                for k in range(n):
                    frec[k][asignaciones[k] - 1] += 1
                
                iteraciones += 1
                no_mejora += 1
                
                # Resetear completamente los Don't Look Bits para la siguiente iteración
                dlb = [0] * n
            else:
                # No hay movimientos posibles (todos son tabú sin aspiración), terminar
                break


    return mejor_asignaciones, mejor_coste


if __name__ == "__main__":
    # Cargar config
    config = load_config('config.txt')

    fac_aleatoriedad = config.get('Factor_aleatoriedad', 2)
    tenencia_tabu = config.get('Tenencia_tabu', 3)
    oscilacion = config.get('Oscilacion_estrategica', 0.50)
    estancamiento = config.get('Estancamiento', 0.05)

    # Leer datos
    datos = lector("_ejemplo.txt")

    # Generar solución inicial con Greedy Aleatorio
    _, _, asignaciones_inicial, coste_inicial = procesar_greedy_aleatorio(datos, fac_aleatoriedad, seed=123)

    print("Solución inicial:", tuple(asignaciones_inicial))
    print("Coste inicial:", coste_inicial)

    # Ejecutar búsqueda tabú
    asignaciones_final, coste_final = busqueda_tabu(datos.mat1, datos.mat2, asignaciones_inicial,
                                                    tenencia_tabu=tenencia_tabu,
                                                    oscilacion=oscilacion,
                                                    estancamiento=estancamiento)

    print("\nSolución final:", tuple(asignaciones_final))
    print("Coste final:", coste_final)

    # Parámetros con valores por defecto si no están en el archivo de configuración
    fac_aleatoriedad = config['Factor_aleatoriedad'] if config else 2
    tenencia_tabu = config.get('Tenencia_tabu', 3)
    oscilacion_estrategica = config.get('Oscilacion_estrategica', 0.50)
    estancamiento = config.get('Estancamiento', 0.05)

    # ===== CARGA DE DATOS =====
    # Leer las matrices de distancia y flujo desde archivo
    datos = lector("ford02.dat")

    # ===== GENERACIÓN DE SOLUCIÓN INICIAL =====
    # Usar el algoritmo Greedy Aleatorio para obtener una buena solución inicial
    _, _, asignaciones_inicial, coste_inicial = procesar_greedy_aleatorio(datos, fac_aleatoriedad, seed=123)

    print("=== BÚSQUEDA TABÚ ===")
    print("Solución inicial:", tuple(asignaciones_inicial))
    print("Coste inicial:", coste_inicial)

    # ===== EJECUCIÓN DE BÚSQUEDA TABÚ =====
    asignaciones_final, coste_final = busqueda_tabu(
        datos.mat1, datos.mat2, asignaciones_inicial, 
        tenencia_tabu=tenencia_tabu, 
        oscilacion_estrategica=oscilacion_estrategica, 
        estancamiento=estancamiento
    )

    # ===== RESULTADOS =====
    print("\nSolución final:", tuple(asignaciones_final))
    print("Coste final:", coste_final)
    print("Mejora:", coste_inicial - coste_final, f"({((coste_inicial - coste_final) / coste_inicial * 100):.2f}%)")

