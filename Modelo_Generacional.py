from typing import List, Tuple
import time
import random
from GreedyAleatorio import procesar_greedy_aleatorio
from Greedy import calcular_coste
from Archivodedatos import lector



def generar_individuo_aleatorio(tam: int, rnd: random.Random) -> List[int]:
    """
    Genera un individuo aleatorio factible para el problema.
    - tam: tamaño del individuo (igual al número de unidades/localizaciones)
    - rnd: objeto Random para control de semilla y reproducibilidad

    Devuelve una lista de enteros de 1..tam en permutación aleatoria.
    """
    ind = list(range(1, tam + 1))  # Creamos la lista [1,2,...,tam]
    rnd.shuffle(ind)               # Mezclamos la lista aleatoriamente
    return ind



def inicializar_poblacion(
    datos,
    tam_pob: int = 100,    # Tamaño total de la población
    k_greedy: int = 5,     # Factor de aleatoriedad para el Greedy Aleatorio
    porc_greedy: float = 0.20,  # Fracción de la población que se hace con Greedy
    seed: int = 78282932      # Semilla para reproducibilidad
) -> List[Tuple[List[int], int]]:
    """
    Inicializa la población para el algoritmo evolutivo generacional (GEN).
    Devuelve una lista de tuplas: (individuo, coste)
    """
    
    rnd = random.Random(seed)   # Creamos objeto Random con semilla para reproducibilidad
    poblacion: List[Tuple[List[int], int]] = []  # Lista vacía que contendrá toda la población

    # Número de individuos generados con Greedy Aleatorio y aleatorios
    n_greedy = int(tam_pob * porc_greedy)  # Por ejemplo, 20 si tam_pob=100 y porc_greedy=0.2
    n_random = tam_pob - n_greedy          # El resto (80 individuos) serán completamente aleatorios

    # ---------- Generar individuos con Greedy Aleatorio ----------
    for i in range(n_greedy):
        # Semilla distinta para cada ejecución de Greedy para que sean soluciones diferentes
        seed_local = rnd.randint(0, 2**31 - 1)
        
        # Ejecutamos el Greedy Aleatorio
        # Devuelve: (flujos_ordenados, distancias_ordenadas, asignaciones, coste)
        _, _, asignacion, coste = procesar_greedy_aleatorio(datos, k_greedy, seed=seed_local)

        #Verificación de factibilidad: debe ser una permutación de 1..tam
        assert sorted(asignacion) == list(range(1, datos.tam + 1)), \
            f"[Greedy] Individuo no válido: {asignacion}"

        #Añadimos el individuo a la población
        poblacion.append((asignacion, coste))

    # ---------- Generar individuos completamente aleatorios ----------
    for i in range(n_random):
        #Generamos un individuo como permutación aleatoria de 1..tam
        ind = generar_individuo_aleatorio(datos.tam, rnd)

        #Calculamos su coste usando la función de evaluación
        coste = calcular_coste(datos.mat1, datos.mat2, ind)

        # erificación de factibilidad
        assert sorted(ind) == list(range(1, datos.tam + 1)), \
            f"[Random] Individuo no válido: {ind}"

        #Añadimos el individuo a la población
        poblacion.append((ind, coste))

    # ---------- Devolvemos la población completa ----------
    #La población no está ordenada por coste; eso lo haremos en otra fase si hace falta
    return poblacion



def torneo(poblacion: List[Tuple[List[int], int]], k: int, rnd: random.Random) -> Tuple[List[int], int]:
    """
    Selección por torneo para escoger un padre
    
    Args:
        poblacion: lista de tuplas (individuo, coste)
        k: tamaño del torneo (por ejemplo, 2 o 3)
        rnd: objeto Random para reproducibilidad

    Returns:
        individuo ganador del torneo (lista de asignaciones, coste)
    """
    #Seleccionamos k individuos al azar sin repetición
    participantes = rnd.sample(poblacion, k)
    
    #Elegimos el individuo con menor coste (mejor fitness)
    ganador = min(participantes, key=lambda x: x[1])
    return ganador


def seleccionar_padres(poblacion: List[Tuple[List[int], int]], kBest: int, rnd: random.Random) -> List[Tuple[Tuple[List[int], int], Tuple[List[int], int]]]:
    """
    Selecciona pares de padres para toda la población mediante torneo binario
    
    Args:
        poblacion: población inicial
        kBest: tamaño del torneo
        rnd: objeto Random para reproducibilidad

    Returns:
        lista de pares de padres [(padre1, padre2), ...]
    """
    tam_pob = len(poblacion)
    padres = []

    for i in range(tam_pob // 2):
        padre1 = torneo(poblacion, kBest, rnd)
        padre2 = torneo(poblacion, kBest, rnd)
        padres.append((padre1, padre2))

    return padres


def cruce_OX2(p1: List[int], p2: List[int], mat1, mat2, rnd: random.Random) -> Tuple[List[int], int]:
    """
    Operador de cruce OX2
    
    Args:
        p1, p2: padres (listas de enteros)
        mat1, mat2: matrices de flujo y distancia para calcular coste
        rnd: objeto Random para reproducibilidad
    
    Returns:
        hijo: tupla (individuo resultante, coste)
    """
    tam = len(p1)
    
    # 1. Inicializamos el hijo con -1 en todas las posiciones
    hijo = [-1] * tam

    # 2. Copiamos aleatoriamente posiciones de p1
    for i in range(tam):
        if rnd.choice([True, False]):  # 50% de probabilidad
            hijo[i] = p1[i]

    # 3. Insertamos los elementos de p2 que aún no están en el hijo
    for elem in p2:
        if elem not in hijo:
            #Buscar la primera posición vacía (-1) y colocar el elemento
            for i in range(tam):
                if hijo[i] == -1:
                    hijo[i] = elem
                    break

    # 4. Calculamos el coste del hijo usando la función ya implementada
    coste_hijo = calcular_coste(mat1, mat2, hijo)
    
    return hijo, coste_hijo



def cruce_MOC(p1: List[int], p2: List[int], mat1, mat2, rnd: random.Random) -> Tuple[List[int], int]:
    """
    Cruce MOC:
    - Elegimos un punto de corte c (1..n-1)
    - Definimos los elementos fijos: E1 = p1[0:c], E2 = p2[0:c]
    - Hijo1: coloca los elementos de E1 en las posiciones de P2 donde aparecen
    y rellena el resto siguiendo el orden de P2 (como OX2)
    - Hijo2: coloca los elementos de E2 en las posiciones de P1 donde aparecen
    y rellena el resto siguiendo el orden de P1 (como OX2)
    """
    n = len(p1)
    c = rnd.randint(1, n - 1)  # punto de corte

    # Elementos fijos
    E1 = set(p1[:c])
    E2 = set(p2[:c])

    # --- Hijo 1 ---
    hijo1 = [-1] * n
    # Fijamos los elementos de E1 en las posiciones donde aparecen en p2
    for idx, val in enumerate(p2):
        if val in E1:
            hijo1[idx] = val

    # Rellenamos el resto siguiendo el orden de p2
    idx = 0
    for val in p2:
        if val not in hijo1:
            while hijo1[idx] != -1:
                idx += 1
            hijo1[idx] = val

    # --- Hijo 2 ---
    hijo2 = [-1] * n
    # Fijamos los elementos de E2 en las posiciones donde aparecen en p1
    for idx, val in enumerate(p1):
        if val in E2:
            hijo2[idx] = val

    # Rellenamos el resto siguiendo el orden de p1
    idx = 0
    for val in p1:
        if val not in hijo2:
            while hijo2[idx] != -1:
                idx += 1
            hijo2[idx] = val

    # Verificación de permutación válida
    assert sorted(hijo1) == list(range(1, n + 1)), f"[MOC] Hijo1 no válido: {hijo1}"
    assert sorted(hijo2) == list(range(1, n + 1)), f"[MOC] Hijo2 no válido: {hijo2}"

    # Calcular costes
    coste_hijo1 = calcular_coste(mat1, mat2, hijo1)
    coste_hijo2 = calcular_coste(mat1, mat2, hijo2)

    return (hijo1, coste_hijo1), (hijo2, coste_hijo2)



def mutacion_2opt(ind: List[int], prob: float, rnd: random.Random) -> Tuple[List[int], bool]:
    """
    Operador de mutación 2-opt:
    - Con probabilidad `prob`, selecciona dos posiciones distintas al azar y las intercambia.
    
    Args:
        ind: individuo (lista de enteros)
        prob: probabilidad de mutar (0..1)
        rnd: objeto Random para reproducibilidad
    
    Returns:
        Tupla: (individuo mutado o igual, True si mutó, False si no)
    """
    n = len(ind)
    mutado = False
    
    # Hacemos una copia para no modificar el original in-place
    nuevo_ind = ind[:] 
    
    if rnd.random() <= prob:
        # Si muta
        # Elegimos dos posiciones distintas
        i, j = rnd.sample(range(n), 2)
        # Intercambiamos los elementos
        nuevo_ind[i], nuevo_ind[j] = nuevo_ind[j], nuevo_ind[i]
        mutado = True
        
    return nuevo_ind, mutado




# ----------------------------
# Función de evaluación de la población
# ----------------------------
def evaluar_poblacion(poblacion: List[Tuple[List[int], int]]) -> dict:
    """
    Calcula estadísticas de una población: mejor, peor y media de costes.
    """
    costes = [c for _, c in poblacion]
    return {
        "mejor": min(costes),
        "peor": max(costes),
        "media": sum(costes) / len(costes)
    }


# ----------------------------
# Función principal: algoritmo generacional
# ----------------------------

def procesaGeneracional(
    archivo: str,
    tam_pob: int,
    porc_greedy: float,
    k_greedy: int,
    elite: int,
    kBest: int,
    kWorst: int,
    prob_cruce: float,
    prob_mutacion: float,
    max_evaluaciones: int,
    tiempo_max: int,
    semilla: int,
    nombre_cruce: str # ¡NUEVO PARÁMETRO!
):
    """
    Algoritmo evolutivo generacional (GEN) con un único operador de cruce (OX2 o MOC).
    """
    
    datos = lector(archivo)
    rnd = random.Random(semilla)

    # 1. Inicialización de la población
    poblacion = inicializar_poblacion(datos, tam_pob, k_greedy, porc_greedy, semilla)
    evaluaciones = len(poblacion)  # Contamos las evaluaciones de la población inicial
    inicio = time.time()
    gen = 0

    # Identificamos el élite inicial
    poblacion.sort(key=lambda x: x[1])
    mejores_elite = poblacion[:elite]
    mejor_elite = poblacion[0]

    print(f"Población inicial generada (tamaño {tam_pob})")
    stats = evaluar_poblacion(poblacion)
    print(f"  Mejor: {stats['mejor']}, Peor: {stats['peor']}, Media: {stats['media']:.2f}")

    # 2. Bucle de evolución generacional
    while evaluaciones < max_evaluaciones and (time.time() - inicio) < tiempo_max:
        gen += 1
        print(f"\n--- Generación {gen} ---")

        # a. Selección de padres
        padres = seleccionar_padres(poblacion, kBest, rnd)
        hijos = []

        # b. Cruce y Mutación para generar la población descendiente
        for idx, ((padre1, coste1), (padre2, coste2)) in enumerate(padres, start=1):
            
            hijo1, coste_hijo1 = padre1, coste1
            hijo2, coste_hijo2 = padre2, coste2
            
            hijo1_por_cruce = False
            hijo2_por_cruce = False
            
            # --- CRUCE CONDICIONAL (prob_cruce) ---
            if rnd.random() <= prob_cruce:
                # Comprobamos qué operador de cruce usar (solo uno por ejecución)
                if nombre_cruce == "OX2":
                    hijo1, coste_hijo1 = cruce_OX2(padre1, padre2, datos.mat1, datos.mat2, rnd)
                    hijo2, coste_hijo2 = cruce_OX2(padre2, padre1, datos.mat1, datos.mat2, rnd)
                elif nombre_cruce == "MOC":
                    (hijo1, coste_hijo1), (hijo2, coste_hijo2) = cruce_MOC(padre1, padre2, datos.mat1, datos.mat2, rnd)
                else:
                    # Este caso no debería ocurrir si el configurador es correcto
                    raise ValueError(f"Operador de cruce no reconocido: {nombre_cruce}")
                
                hijo1_por_cruce = True
                hijo2_por_cruce = True
            
            
            # --- MUTACIÓN y EVALUACIÓN CONDICIONAL ---
            
            # 1. Individuo 1
            hijo1_final, muto1 = mutacion_2opt(hijo1, prob_mutacion, rnd)
            
            if muto1 or hijo1_por_cruce:
                if evaluaciones >= max_evaluaciones: break
                
                coste_hijo1_final = calcular_coste(datos.mat1, datos.mat2, hijo1_final)
                evaluaciones += 1
            else:
                coste_hijo1_final = coste_hijo1
            
            hijos.append((hijo1_final, coste_hijo1_final))


            # 2. Individuo 2
            if evaluaciones >= max_evaluaciones: break
            
            hijo2_final, muto2 = mutacion_2opt(hijo2, prob_mutacion, rnd)

            if muto2 or hijo2_por_cruce:
                coste_hijo2_final = calcular_coste(datos.mat1, datos.mat2, hijo2_final)
                evaluaciones += 1
            else:
                coste_hijo2_final = coste_hijo2

            hijos.append((hijo2_final, coste_hijo2_final))

        # Si el bucle de hijos se detuvo por la condición de parada
        if evaluaciones >= max_evaluaciones:
            break
        
        # c. Reemplazo generacional completo con Elitismo
        poblacion_candidata = hijos + mejores_elite 
        poblacion_candidata.sort(key=lambda x: x[1])
        poblacion = poblacion_candidata[:tam_pob]

        # d. Protección del mejor élite
        if mejor_elite not in poblacion:
            torneo_perdedores = rnd.sample(poblacion, kWorst)
            peor_torneo = max(torneo_perdedores, key=lambda x: x[1]) 
            idx_peor = poblacion.index(peor_torneo)
            poblacion[idx_peor] = mejor_elite

        # e. Actualizamos el élite
        poblacion.sort(key=lambda x: x[1])
        mejores_elite = poblacion[:elite]
        mejor_elite = poblacion[0]

        # Estadísticas de la generación
        stats = evaluar_poblacion(poblacion)
        print(f"  Mejor: {stats['mejor']}, Peor: {stats['peor']}, Media: {stats['media']:.2f}")
        print(f"  Evaluaciones acumuladas: {evaluaciones}")

    print("\n--- Fin de la ejecución ---")
    print(f"Generaciones completadas: {gen}")
    stats = evaluar_poblacion(poblacion)
    print(f"Mejor coste final: {stats['mejor']}")
    print(f"Media final: {stats['media']:.2f}")

    return poblacion

def resumenGeneracional(
    archivo: str,
    tam_pob: int,
    porc_greedy: float,
    k_greedy: int,
    elite: int,
    kBest: int,
    kWorst: int,
    prob_cruce: float,
    prob_mutacion: float,
    max_evaluaciones: int,
    tiempo_max: int,
    semilla: int,
    nombre_cruce: str  # ¡NUEVO PARÁMETRO!
):
    """
    Algoritmo evolutivo generacional (GEN) para generar solo un resumen de los resultados finales.
    Utiliza el operador de cruce especificado (OX2 o MOC).
    """
    
    # Se omiten las importaciones por brevedad, asumiendo que están al inicio del archivo.
    
    datos = lector(archivo)
    rnd = random.Random(semilla)

    # 1. Inicialización de la población
    poblacion = inicializar_poblacion(datos, tam_pob, k_greedy, porc_greedy, semilla)
    evaluaciones = len(poblacion)  # Contamos las evaluaciones de la población inicial
    inicio = time.time()
    gen = 0

    # Identificamos el élite inicial
    poblacion.sort(key=lambda x: x[1])
    mejores_elite = poblacion[:elite] # Guardamos los E mejores
    mejor_elite = poblacion[0]        # El mejor individuo, para la protección

    print("------------------------------------------------------------------")
    print(f"RESUMEN GENERACIONAL: {archivo} | Cruce: {nombre_cruce} (Semilla: {semilla})")
    print(f"Población inicial generada (tamaño {tam_pob})")
    stats = evaluar_poblacion(poblacion)
    print(f"  Mejor Inicial: {stats['mejor']}, Peor Inicial: {stats['peor']}, Media Inicial: {stats['media']:.2f}")
    print("------------------------------------------------------------------")

    # 2. Bucle de evolución generacional (sin impresiones intermedias)
    while evaluaciones < max_evaluaciones and (time.time() - inicio) < tiempo_max:
        gen += 1

        # a. Selección de padres
        padres = seleccionar_padres(poblacion, kBest, rnd)
        hijos = []

        # b. Cruce y Mutación para generar la población descendiente
        for idx, ((padre1, coste1), (padre2, coste2)) in enumerate(padres, start=1):
            
            hijo1, coste_hijo1 = padre1, coste1
            hijo2, coste_hijo2 = padre2, coste2
            
            hijo1_por_cruce = False
            hijo2_por_cruce = False
            
            # --- CRUCE CONDICIONAL (prob_cruce) ---
            if rnd.random() <= prob_cruce:
                # Comprobamos qué operador de cruce usar
                if nombre_cruce == "OX2":
                    hijo1, coste_hijo1 = cruce_OX2(padre1, padre2, datos.mat1, datos.mat2, rnd)
                    hijo2, coste_hijo2 = cruce_OX2(padre2, padre1, datos.mat1, datos.mat2, rnd)
                elif nombre_cruce == "MOC":
                    (hijo1, coste_hijo1), (hijo2, coste_hijo2) = cruce_MOC(padre1, padre2, datos.mat1, datos.mat2, rnd)
                else:
                    # En caso de error de configuración, lanzamos una excepción
                    raise ValueError(f"Operador de cruce no reconocido: {nombre_cruce}")
                
                hijo1_por_cruce = True
                hijo2_por_cruce = True
            
            
            # --- MUTACIÓN y EVALUACIÓN CONDICIONAL ---
            
            # 1. Individuo 1
            hijo1_final, muto1 = mutacion_2opt(hijo1, prob_mutacion, rnd)
            
            if muto1 or hijo1_por_cruce:
                if evaluaciones >= max_evaluaciones: break
                
                coste_hijo1_final = calcular_coste(datos.mat1, datos.mat2, hijo1_final)
                evaluaciones += 1
            else:
                coste_hijo1_final = coste_hijo1
            
            hijos.append((hijo1_final, coste_hijo1_final))


            # 2. Individuo 2
            if evaluaciones >= max_evaluaciones: break
            
            hijo2_final, muto2 = mutacion_2opt(hijo2, prob_mutacion, rnd)

            if muto2 or hijo2_por_cruce:
                coste_hijo2_final = calcular_coste(datos.mat1, datos.mat2, hijo2_final)
                evaluaciones += 1
            else:
                coste_hijo2_final = coste_hijo2

            hijos.append((hijo2_final, coste_hijo2_final))

        # Si el bucle de hijos se detuvo por la condición de parada
        if evaluaciones >= max_evaluaciones:
            break
        
        # c. Reemplazo generacional completo con Elitismo
        poblacion_candidata = hijos + mejores_elite 
        poblacion_candidata.sort(key=lambda x: x[1])
        poblacion = poblacion_candidata[:tam_pob]

        # d. Protección del mejor élite
        if mejor_elite not in poblacion:
            torneo_perdedores = rnd.sample(poblacion, kWorst)
            peor_torneo = max(torneo_perdedores, key=lambda x: x[1]) 
            idx_peor = poblacion.index(peor_torneo)
            poblacion[idx_peor] = mejor_elite

        # e. Actualizamos el élite
        poblacion.sort(key=lambda x: x[1])
        mejores_elite = poblacion[:elite]
        mejor_elite = poblacion[0]


    # 3. Impresión de los resultados finales
    tiempo_total = time.time() - inicio
    stats = evaluar_poblacion(poblacion)
    
    print("\n--- RESULTADOS FINALES ---")
    print(f"Generaciones completadas: {gen}")
    print(f"Evaluaciones totales: {evaluaciones}")
    print(f"Tiempo total (s): {tiempo_total:.4f}")
    print(f"Mejor Coste Final: {stats['mejor']}")
    print(f"Media Final: {stats['media']:.2f}")
    print(f"Cruce utilizado: {nombre_cruce}")
    print("------------------------------------------------------------------")

    return poblacion

# ----------------------------
# Main para ejecutar el ejemplo
# ----------------------------
if __name__ == "__main__":
    poblacion_final = procesaGeneracional(
        archivo="ford01.dat",
        tam_pob=100,
        porc_greedy=0.2,
        k_greedy=5,
        elite=1,
        kBest=2,
        kWorst=3,
        prob_cruce=0.7,
        prob_mutacion=0.1,
        max_evaluaciones=50000,
        tiempo_max=60,
        semilla=78282932,
        nombre_cruce="OX2"
    )

