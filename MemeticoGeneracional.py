import time
import random
from collections import deque
from typing import List, Tuple

from Modelo_Generacional import (
    inicializar_poblacion,
    seleccionar_padres,
    cruce_OX2,
    cruce_MOC,
    mutacion_2opt,
    evaluar_poblacion,
)
from Greedy import calcular_coste
from Archivodedatos import lector
from BusquedaTabu import calcular_delta_coste


def busqueda_tabu_modificada(mat1, mat2, asignaciones_inicial: List[int], max_iter: int = 50, tenencia_tabu: int = 3) -> Tuple[List[int], int]:
    """
    Búsqueda Tabú modificada (sin memoria a largo plazo, sin oscilación estratégica).

    - Usa lista tabú para intercambios prohibidos temporales.
    - No usa matriz de frecuencias ni parámetros de oscilación.
    - Realiza hasta `max_iter` iteraciones (profundidad).

    Args:
        mat1, mat2: matrices de distancia y flujo
        asignaciones_inicial: solución inicial (valores 1..n)
        max_iter: número máximo de iteraciones de la BT
        tenencia_tabu: tamaño de la lista tabú (en intercambios)

    Returns:
        mejor_asignacion, mejor_coste
    """
    n = len(asignaciones_inicial)
    asign = list(asignaciones_inicial)
    coste_actual = calcular_coste(mat1, mat2, asign)

    mejor_asign = list(asign)
    mejor_coste = coste_actual

    tabu = deque(maxlen=tenencia_tabu)

    for it in range(max_iter):
        best_delta = float('inf')
        best_pair = None

        # Buscar el mejor movimiento permitido (mejor delta)
        for i in range(n):
            for j in range(i + 1, n):
                pair = (min(i, j), max(i, j))
                if pair in tabu:
                    continue

                delta = calcular_delta_coste(mat1, mat2, asign, i, j)
                if delta < best_delta:
                    best_delta = delta
                    best_pair = (i, j)

        if best_pair is None:
            # No hay movimientos factibles (rara vez ocurre)
            break

        i, j = best_pair
        # Aplicar el intercambio seleccionado
        asign[i], asign[j] = asign[j], asign[i]
        coste_actual += best_delta

        # Actualizar lista tabú
        tabu.append((min(i, j), max(i, j)))

        # Actualizar mejor solución si corresponde
        if coste_actual < mejor_coste:
            mejor_coste = coste_actual
            mejor_asign = list(asign)

    return mejor_asign, mejor_coste


def procesaMemetico(
    archivo: str,
    tam_pob: int = 100,
    porc_greedy: float = 0.2,
    k_greedy: int = 5,
    elite: int = 1,
    kBest: int = 2,
    kWorst: int = 3,
    prob_cruce: float = 0.7,
    prob_mutacion: float = 0.1,
    max_evaluaciones: int = 10000,
    tiempo_max: int = 60,
    semilla: int = 78282932,
    trigger_eval: int = 1000,
    bt_iter: int = 10,
    tenencia_tabu: int = 3,
):
    """
    Algoritmo memético generacional. Es una versión del GEN que aplica la
    `busqueda_tabu_modificada` sobre el individuo élite cuando se alcanza
    `trigger_eval` evaluaciones (una única vez durante la ejecución).

    Devuelve la población final.
    """
    datos = lector(archivo)
    rnd = random.Random(semilla)

    poblacion = inicializar_poblacion(datos, tam_pob, k_greedy, porc_greedy, semilla)
    evaluaciones = len(poblacion)
    inicio = time.time()

    poblacion.sort(key=lambda x: x[1])
    mejores_elite = poblacion[:elite]
    mejor_elite = poblacion[0]

    trigger_aplicado = False

    gen = 0
    print(f"Iniciando memético: archivo={archivo} trigger={trigger_eval} bt_iter={bt_iter}")

    while evaluaciones < max_evaluaciones and (time.time() - inicio) < tiempo_max:
        gen += 1

        padres = seleccionar_padres(poblacion, kBest, rnd)
        hijos = []

        for ((padre1, coste1), (padre2, coste2)) in padres:
            hijo1, coste_hijo1 = padre1, coste1
            hijo2, coste_hijo2 = padre2, coste2

            hijo1_por_cruce = False
            hijo2_por_cruce = False

            if rnd.random() <= prob_cruce:
                hijo1, coste_hijo1 = cruce_OX2(padre1, padre2, datos.mat1, datos.mat2, rnd)
                hijo2, coste_hijo2 = cruce_OX2(padre2, padre1, datos.mat1, datos.mat2, rnd)
                hijo1_por_cruce = True
                hijo2_por_cruce = True

            # Mutación e evaluación condicional
            hijo1_final, m1 = mutacion_2opt(hijo1, prob_mutacion, rnd)
            if m1 or hijo1_por_cruce:
                if evaluaciones >= max_evaluaciones:
                    break
                coste_hijo1_final = calcular_coste(datos.mat1, datos.mat2, hijo1_final)
                evaluaciones += 1
            else:
                coste_hijo1_final = coste_hijo1
            hijos.append((hijo1_final, coste_hijo1_final))

            if evaluaciones >= max_evaluaciones:
                break

            hijo2_final, m2 = mutacion_2opt(hijo2, prob_mutacion, rnd)
            if m2 or hijo2_por_cruce:
                coste_hijo2_final = calcular_coste(datos.mat1, datos.mat2, hijo2_final)
                evaluaciones += 1
            else:
                coste_hijo2_final = coste_hijo2
            hijos.append((hijo2_final, coste_hijo2_final))

        if evaluaciones >= max_evaluaciones:
            break

        # Reemplazo con elitismo
        poblacion_cand = hijos + mejores_elite
        poblacion_cand.sort(key=lambda x: x[1])
        poblacion = poblacion_cand[:tam_pob]

        # Protección del mejor élite
        if mejor_elite not in poblacion:
            torneo_perdedores = rnd.sample(poblacion, kWorst)
            peor_torneo = max(torneo_perdedores, key=lambda x: x[1])
            idx_peor = poblacion.index(peor_torneo)
            poblacion[idx_peor] = mejor_elite

        poblacion.sort(key=lambda x: x[1])
        mejores_elite = poblacion[:elite]
        mejor_elite = poblacion[0]

        # Aquí: activar la BT modificada cuando se alcanza trigger_eval (una vez)
        if (not trigger_aplicado) and evaluaciones >= trigger_eval:
            asign_elite = mejor_elite[0]
            coste_elite = mejor_elite[1]

            print(f"Aplicando BT modificada sobre élite en eval={evaluaciones} (prof={bt_iter})")
            nueva_asig, nuevo_coste = busqueda_tabu_modificada(datos.mat1, datos.mat2, asign_elite, max_iter=bt_iter, tenencia_tabu=tenencia_tabu)

            # Si mejora, sustituimos el élite en la población
            if nuevo_coste < coste_elite:
                print(f"  Mejora encontrada: {coste_elite} -> {nuevo_coste}")
                # sustituir el mejor élite por la nueva solución
                # buscar índice del mejor_elite en poblacion
                try:
                    idx = poblacion.index(mejor_elite)
                    poblacion[idx] = (nueva_asig, nuevo_coste)
                except ValueError:
                    # si no está (caso improbable), insertar y recortar
                    poblacion.append((nueva_asig, nuevo_coste))
                    poblacion.sort(key=lambda x: x[1])
                    poblacion = poblacion[:tam_pob]

                poblacion.sort(key=lambda x: x[1])
                mejores_elite = poblacion[:elite]
                mejor_elite = poblacion[0]
            else:
                print(f"  Sin mejora por BT (elitismo conservado: {coste_elite} <= {nuevo_coste})")

            trigger_aplicado = True

        # Estadísticas por generación (resumen)
        stats = evaluar_poblacion(poblacion)
        print(f"Gen {gen}: Mejor={stats['mejor']} Media={stats['media']:.2f} Eval={evaluaciones}")

    print("-- Fin memético --")
    stats = evaluar_poblacion(poblacion)
    print(f"Mejor final: {stats['mejor']} (Eval={evaluaciones})")

    return poblacion


def ejecutar_variantes(archivo: str = "ford01.dat"):
    # Definimos las variantes solicitadas (trigger, profundidad BT)
    triggers = [1000, 2000, 5000]
    profundidades = [10, 50, 100]

    resultados = []
    for trig in triggers:
        for prof in profundidades:
            print("=================================================================")
            print(f"Versión MGen: Cruce=OX2, M=100, E=1, kBest=2, kWorst=3, evals={trig}, BT_iter={prof}")
            pobl = procesaMemetico(
                archivo=archivo,
                tam_pob=100,
                porc_greedy=0.2,
                k_greedy=5,
                elite=1,
                kBest=2,
                kWorst=3,
                prob_cruce=0.7,
                prob_mutacion=0.1,
                max_evaluaciones=10000,
                tiempo_max=60,
                semilla=78282932,
                trigger_eval=trig,
                bt_iter=prof,
                tenencia_tabu=3,
            )
            pobl.sort(key=lambda x: x[1])
            resultados.append(((trig, prof), pobl[0]))

    print("\nResumen de variantes:")
    for (trig, prof), (ind, coste) in resultados:
        print(f"Trigger={trig}, BT_iter={prof} -> Mejor coste: {coste}")


if __name__ == "__main__":
    ejecutar_variantes("ford01.dat")
