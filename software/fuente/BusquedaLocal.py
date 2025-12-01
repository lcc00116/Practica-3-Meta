import random
from GreedyAleatorio import procesar_greedy_aleatorio
from Greedy import calcular_coste
from Archivodedatos import lector
from Configurador import load_config


def calcular_delta_coste(mat1, mat2, asignaciones, i, j): #Delta es la diferencia de costes
    """
    Calcula el cambio en el coste al intercambiar las asignaciones de i y j.
    Factorización: solo se recalculan las contribuciones de i y j.
    """
    n = len(asignaciones)
    delta = 0

    for k in range(n):
        if k != i and k != j:
            li = asignaciones[i] - 1
            lj = asignaciones[j] - 1
            lk = asignaciones[k] - 1

            #Diferencia por intercambiar i y j
            delta += (mat1[i][k] - mat1[j][k]) * (mat2[lj][lk] - mat2[li][lk])
            delta += (mat1[k][i] - mat1[k][j]) * (mat2[lk][lj] - mat2[lk][li])

    return delta


def busqueda_local(mat1, mat2, asignaciones, max_iter=5000):
    """
    Búsqueda local con Primero el mejor y operador DLB + 2-opt.
    """
    n = len(asignaciones)
    coste_actual = calcular_coste(mat1, mat2, asignaciones)

    #Vector DLB: 0 = activo, 1 = no prometedor
    dlb = [0] * n
    iteraciones = 0
    inicio_i = 0

    while iteraciones < max_iter:
        mejora = False

        for paso in range(n):
            i = (inicio_i + paso) % n #Se recorre de forma circular
            if dlb[i] == 0: #Si no es prometedor pasamos a la siguiente i
                improve_flag = False
                for j in range(i + 1, n): #Inicializamos j en i+1 para evitar repetidos e intercambios innecesarios
                    delta = calcular_delta_coste(mat1, mat2, asignaciones, i, j)
                    if delta < 0:  #Si hay mejora
                        iteraciones += 1
                        #Aplicar movimiento 2-opt
                        asignaciones[i], asignaciones[j] = asignaciones[j], asignaciones[i]
                        coste_actual += delta
                        dlb[i] = dlb[j] = 0 #Reinicializamos pq vuelven a ser prometedoras
                        improve_flag = True
                        mejora = True
                        inicio_i = i #Guardamos el índice de mejora para continuar desde aquí en la siguiente iteración
                        break  #Hemos encontrado la primera mejora: salimos del bucle
                if not improve_flag: #Si no mejora con ninguno lo marcamos como no prometedor
                    dlb[i] = 1
            if mejora:
                break  #Reiniciamos bucle externo en cuanto haya mejora(volvemos la i al principio del dlb)

        if not mejora:  #CONDICION DE PARADA: No hubo ninguna mejora recorriendo todas las i: terminamos
            break

    return asignaciones, coste_actual #Devuelve la lista de asignaciones actualizada y el coste final


if __name__ == "__main__":
    #Cargar config
    config = load_config('config.txt')
    fac_aleatoriedad = config['Factor_aleatoriedad'] if config else 2

    #Leer datos
    datos = lector("ford02.dat")

    #Generar solución inicial con Greedy Aleatorio
    _, _, asignaciones_inicial, coste_inicial = procesar_greedy_aleatorio(datos, fac_aleatoriedad, seed=123)

    print("Solución inicial:", tuple(asignaciones_inicial))
    print("Coste inicial:", coste_inicial)

    #Ejecutar búsqueda local
    asignaciones_final, coste_final = busqueda_local(datos.mat1, datos.mat2, asignaciones_inicial)

    print("\nSolución final:", tuple(asignaciones_final))
    print("Coste final:", coste_final)
