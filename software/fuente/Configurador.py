import json
import os

def load_config(file_path='config.txt'):
    if not os.path.exists(file_path):
        print(f"Error: El archivo '{file_path}' no existe.")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            variables = json.load(file)
        
        return variables
    
    except json.JSONDecodeError as e:
        print(f"Error: JSON inválido en '{file_path}': {e}")
        print("Tip: Verifica comillas, comas y llaves.")
        return None
    except IOError as e:
        print(f"Error al leer '{file_path}': {e}")
        return None

#Carga y procesa
variables = load_config()
if variables:
    print("Config cargado exitosamente:")
    print(f"- Archivos: {variables.get('Archivos')}")
    print(f"- Algoritmo: {variables.get('Algoritmo')}")
    print(f"- Elite: {variables.get('Elite')}")
    print(f"- kBest: {variables.get('kBest')}")
    print(f"- kWorst: {variables.get('kWorst')}")
    print(f"- Cruce: {variables.get('Cruce')}")
    print(f"- Probabilidad de cruce: {variables.get('Prob_Cruce')}")
    print(f"- Probabilidad de mutación: {variables.get('Prob_mutacion')}")
    print(f"- Tamaño población: {variables.get('Tam')}")
    print(f"- Semillas: {variables.get('Semillas')}")
    print(f"- Máximo número de evaluaciones: {variables.get('MaxEv')}")
        
        # --- NUEVOS PARÁMETROS AÑADIDOS ---
    print(f"- Tenencia Tabú: {variables.get('Tenencia_tabu', 'No definido')}")
    print(f"- Frecuencia BT: {variables.get('Frecuencia_BT', 'No definido')}")
    print(f"- Profundidad BT: {variables.get('Profundidad_BT', 'No definido')}")
        
else:
    print("No se pudo cargar el config. Revisa el archivo.")