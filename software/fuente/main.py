# --- main.py ---
from Configurador import load_config
from Modelo_Generacional import resumenGeneracional
import time
import os

def main():
    # 1. Cargar configuración desde el archivo externo
    config = load_config("../bin/config.txt") 

    archivos = config["Archivos"]
    
    # Parámetros básicos
    elite = config["Elite"]
    kBest = config["kBest"]
    kWorst = config["kWorst"] 
    
    prob_cruce = config["Prob_Cruce"]
    prob_mutacion = config["Prob_mutacion"]
    tam_pob = config["Tam"]
    
    semillas = config["Semillas"]
    max_evaluaciones = config["MaxEv"]
    porc_greedy = config["Porc_Greedy"]
    k_greedy = config["Factor_aleatoriedad"]
    
    # --- PARÁMETROS DE LA BÚSQUEDA TABÚ (Hibridación) ---
    tenencia_tabu = config["Tenencia_tabu"]
    
    # Leemos los valores individuales del JSON
    frecuencia_bt = config["Frecuencia_BT"]   # Ej: 1000
    profundidad_bt = config["Profundidad_BT"] # Ej: 10
    
    # Creamos la lista de tuplas con UN SOLO evento de BT
    # Esto asegura que solo se ejecute una vez al llegar a esas evaluaciones
    bt_configuracion = [(frecuencia_bt, profundidad_bt)]

    # 2. Bucle de ejecución
    print(f"\n==================================================")
    print(f"=== INICIANDO GEN HÍBRIDO (BT MODIFICADA) ===")
    print(f"==================================================")
    print(f"Configuración BT -> Tenencia: {tenencia_tabu}")
    print(f"Evento BT programado -> A las {frecuencia_bt} evals, Profundidad: {profundidad_bt}")

    for archivo_base in archivos:
        ruta_archivo_datos = os.path.join("..", "bin", archivo_base)
        print(f"\n--- Procesando archivo: {ruta_archivo_datos} ---")

        for i, semilla_actual in enumerate(semillas):
            print(f"\n---- Ejecución {i+1}/{len(semillas)} con Semilla: **{semilla_actual}** ----")
            
            start_ns = time.perf_counter_ns()
            
            # Llamada al Generacional Híbrido
            poblacion = resumenGeneracional( 
                archivo=ruta_archivo_datos,
                tam_pob=tam_pob,
                porc_greedy=porc_greedy,
                k_greedy=k_greedy,
                elite=elite,
                kBest=kBest,
                kWorst = kWorst,
                prob_cruce=prob_cruce,
                prob_mutacion=prob_mutacion,
                max_evaluaciones=max_evaluaciones,
                semilla=semilla_actual,
                # Pasamos los parámetros de BT
                tamano_lista_tabu=tenencia_tabu,
                bt_frec_profundidad=bt_configuracion # Pasamos la lista [(1000, 10)]
            )

            end_ns = time.perf_counter_ns()
            print(f"Tiempo total (s): {(end_ns - start_ns)/1_000_000_000:.4f}")
            print("-" * 50) 

if __name__ == "__main__":
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    os.chdir(script_dir)
    main()