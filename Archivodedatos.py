
class lector:
    tam = 0
    mat1 = []
    mat2 = []

    def __init__(self, ruta):
        #Abrimos el fichero en modo lectura
        with open(ruta, "r") as fichero:

            #Leemos la primera línea (tamaño de la matriz)
            self.tam = int(fichero.readline().strip())

            #Inicializamos las listas de matrices para que no se compartan entre instancias
            self.mat1 = []
            self.mat2 = []

            #Leemos la línea en blanco
            fichero.readline()

            # Leemos la primera matriz
            for i in range(self.tam):
                linea = fichero.readline().strip()  #Quitamos espacios al principio y final
                if linea:  #Comprobamos que la línea no esté vacía
                    valores_str = linea.split()  #Split sin argumento para múltiples espacios
                    fila = []
                    for valor in valores_str:
                        fila.append(int(valor))
                    self.mat1.append(fila)

            #Leemos la línea en blanco entre matrices
            fichero.readline()

            #Leemos la segunda matriz
            for i in range(self.tam):
                linea = fichero.readline().strip()
                if linea:
                    valores_str = linea.split()
                    fila = []
                    for valor in valores_str:
                        fila.append(int(valor))
                    self.mat2.append(fila)