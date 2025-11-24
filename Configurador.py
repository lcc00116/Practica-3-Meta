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
    print(f"- Archivos: {variables['Archivos']}")
    print(f"- Algoritmos: {variables['Algoritmo']}")
    print(f"- Elite: {variables['Elite']}")
    print(f"- kBest: {variables['kBest']}")
    print(f"- kWorst: {variables['kWorst']}")
    print(f"- Cruces: {variables['Cruce']}")
    print(f"- Probabilidad de cruce: {variables['Prob_Cruce']}")
    print(f"- Probabilidad de mutación: {variables['Prob_mutacion']}")
    print(f"- Tamaño población: {variables['Tam']}")
    print(f"- Tiempo máximo: {variables['MaxTime']}")
    print(f"- Semillas: {variables['Semillas']}")
    print(f"- Máximo número de evaluaciones: {variables['MaxEv']}")
    
else:
    print("No se pudo cargar el config. Revisa el archivo.")