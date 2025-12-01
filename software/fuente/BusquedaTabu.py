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



def busqueda_tabu_memetica(mat1, mat2, asignaciones_inicial, tenencia_tabu, max_iteraciones):
    """
    Implementación MODIFICADA y SIMPLIFICADA de Búsqueda Tabú para el AG Híbrido.
    
    Solo usa Memoria a Corto Plazo (Tabú), Aspiración y DLB.
    IGNORA Memoria a Largo Plazo y Oscilación.
    Condición de parada: estricta por 'max_iteraciones'.
    
    Args:
        mat1: Matriz de distancias.
        mat2: Matriz de flujos.
        asignaciones_inicial: Solución inicial (el élite).
        tenencia_tabu: Tamaño de la lista tabú.
        max_iteraciones: Límite estricto de iteraciones (10, 50, o 100).
        
    Returns:
        Tupla (mejor_asignaciones, mejor_coste)
    """
    # ===== INICIALIZACIÓN =====
    n = len(asignaciones_inicial)
    asignaciones = list(asignaciones_inicial)
    coste_actual = calcular_coste(mat1, mat2, asignaciones)

    mejor_asignaciones = list(asignaciones)
    mejor_coste = coste_actual

    dlb = [0] * n
    tabu = deque(maxlen=tenencia_tabu)

    #NOTA: Se omite la Matriz de Frecuencias (Memoria a Largo Plazo)

    iteraciones = 0

    # ===== BUCLE PRINCIPAL (Parada por iteraciones) =====
    while iteraciones < max_iteraciones:
        
        mejora = False
        best_delta = float('inf')
        mejor_i = -1
        best_j = -1

        # ===== EXPLORACIÓN DEL VECINDARIO =====
        for i in range(n):
            if dlb[i] == 1:
                continue
            
            flag_mejora = False
            
            for j in range(i + 1, n):
                delta = calcular_delta_coste(mat1, mat2, asignaciones, i, j)
                
                # Criterios Tabú y Aspiración
                pair = (min(i, j), max(i, j))
                is_tabu = pair in tabu
                aspiration = (coste_actual + delta < mejor_coste)
                
                if is_tabu and not aspiration:
                    continue
                
                # NO se considera Oscilación Estratégica, el coste efectivo es el delta
                cambio_coste = delta 
                
                # --- Aplicar Criterio Best-Improvement ---
                if cambio_coste < best_delta:
                    best_delta = cambio_coste
                    mejor_i = i
                    best_j = j
                    
        # Aplicar el MEJOR movimiento encontrado (Best-Improvement)
        if mejor_i != -1:
            i = mejor_i
            j = best_j
            delta = best_delta
            
            # Aplicar el movimiento
            asignaciones[i], asignaciones[j] = asignaciones[j], asignaciones[i]
            coste_actual += delta
            
            # Añadir a la lista tabú
            pair = (min(i, j), max(i, j))
            tabu.append(pair)
            
            iteraciones += 1
            
            # Actualizar la mejor solución si es necesario
            if coste_actual < mejor_coste:
                mejor_coste = coste_actual
                mejor_asignaciones = list(asignaciones)
            
            # Resetear Don't Look Bits
            # Si el movimiento era de empeoramiento, reseteamos todos los DLB (como en tu original)
            if best_delta >= 0:
                dlb = [0] * n
            else:
                dlb[i] = dlb[j] = 0 # Mejorar la eficiencia, solo reseteamos los implicados
        
        else:
            # No hay movimientos posibles (todos son tabú sin aspiración), terminar
            break

    return mejor_asignaciones, mejor_coste


if __name__ == "__main__":
    # 1. Cargar Configuración y Definir Parámetros
    config = load_config('config.txt')
    
    # Valores de configuración
    fac_aleatoriedad = config.get('Factor_aleatoriedad', 2)
    tenencia_tabu = config.get('Tenencia_tabu', 3)
    # Definimos la profundidad de la BT memética para la prueba
    max_iteraciones_prueba = 100 

    # 2. Cargar Datos
    archivo_datos = "ford01.dat" 
    print("=" * 60)
    print(f"Prueba de Búsqueda Tabú Memética")
    print("=" * 60)
    print(f"Cargando datos: {archivo_datos}")
    datos = lector(archivo_datos)

    # 3. Generar Solución Inicial (Greedy Aleatorio)
    semilla = 123 
    print(f"-> Generando solución inicial (Greedy Aleatorio, Semilla: {semilla})...")
    
    # procesar_greedy_aleatorio devuelve (..., asignaciones, coste_total)
    _, _, asignaciones_inicial, coste_inicial = procesar_greedy_aleatorio(
        datos, 
        k=fac_aleatoriedad, 
        seed=semilla
    )

    # 4. Ejecutar Búsqueda Tabú Memética
    print("\n" + "-" * 30)
    print(f"Coste inicial: {coste_inicial}")
    print(f"Asignaciones iniciales: {tuple(asignaciones_inicial)}")
    print(f"Parámetros BT: Tenencia={tenencia_tabu}, Iteraciones={max_iteraciones_prueba}")
    print("-" * 30)
    
    
    asignaciones_final, coste_final = busqueda_tabu_memetica(
        datos.mat1, 
        datos.mat2, 
        asignaciones_inicial, 
        tenencia_tabu=tenencia_tabu, 
        max_iteraciones=max_iteraciones_prueba
    )
    
    # 5. Mostrar Resultados Finales y Estadísticas
    mejora_absoluta = coste_inicial - coste_final
    mejora_porcentual = (mejora_absoluta / coste_inicial) * 100 if coste_inicial != 0 else 0
    
    print("\n" + "=" * 60)
    print(" RESULTADOS BT MEMÉTICA ")
    print("=" * 60)
    print(f"Costo Final:              **{coste_final}**")
    print(f"Asignaciones Finales:     {tuple(asignaciones_final)}")
    print("-" * 60)
    print(f"Mejora Absoluta:          {mejora_absoluta:.2f}")
    print(f"Mejora Porcentual:        {mejora_porcentual:.2f}%")