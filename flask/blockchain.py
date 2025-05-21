import hashlib
import time
from typing import List, Dict

# Clase para almacenar los datos de una transacción
class Transaccion:
    def __init__(self, pagador: str, receptor: str, cantidad: float):
        self.pagador = pagador
        self.receptor = receptor
        self.cantidad = cantidad

    # Convierto en un diccionario
    def convert_to_dict(self) -> Dict:
        return {
            'pagador': self.pagador,
            'receptor': self.receptor,
            'cantidad': self.cantidad
        }
    def __str__(self) -> str:
        return f"{self.pagador} envia a {self.receptor} la cantidad de {self.cantidad}"

# Lo vamos a implementar mediante un merkleTree, (Cada nodo es una combinación numérica de sus 2 hijos)
# De esta forma, el orden de operaciones de búsqueda de nodos es mucho menor a una búsqueda numérica por fuerza bruta clásica
class MerkleTree: 
    def __init__(self, l_transacciones: List[Transaccion]):
        self.l_transacciones = l_transacciones
        self.root, self.niveles = self.construir_merkle_tree()

    def construir_merkle_tree(self) -> tuple[str, List[List[str]]]:
        if not self.l_transacciones:
            return "", []

        # hashes 
        hojas = []
        for tx in self.l_transacciones:
            # Transacción -> Diccionario -> Cadena -> Bytes -> Hash y hexDigest()
            
            hash_transaccion = hashlib.sha256(str(tx.convert_to_dict()).encode()).hexdigest()

            
            hojas.append(hash_transaccion)

        # Guardo los niveles del árbol 
        niveles = [hojas]

        # Si hay más transacciones, se crea el árbol
        nivel_actual = hojas
        while len(nivel_actual) > 1:
            nivel_temp = []
            for i in range(0, len(nivel_actual), 2):
                if i + 1 < len(nivel_actual):
                    #Juntar pareja de hojas
                    combined = nivel_actual[i] + nivel_actual[i + 1]
                    nuevo_hash = hashlib.sha256(combined.encode()).hexdigest()
                    nivel_temp.append(nuevo_hash)
                else:
                    # Hoja impar 
                    nivel_temp.append(nivel_actual[i])
            niveles.append(nivel_temp)
            nivel_actual = nivel_temp

        return nivel_actual[0], niveles

    def mostrar_niveles(self) -> None:
        print("\nNiveles del Árbol de Merkle:")
        for idx, nivel in enumerate(reversed(self.niveles)):
            print(f"\tNivel {idx} (desde la raíz):")
            for hash in nivel:
                print(f"\t\t{hash}") 

class Bloque:
    def __init__(self, hash_anterior: str, l_transacciones: List[Transaccion], marca_de_tiempo: str):
        self.hash_anterior = hash_anterior
        self.marca_de_tiempo = marca_de_tiempo
        self.l_transacciones = l_transacciones
        self.merkle_tree = MerkleTree(l_transacciones)
        self.merkle_root = self.merkle_tree.root
        self.merkle_niveles = self.merkle_tree.niveles  # Se guardan los niveles del árbol
        self.nonce = 0
        self.hash = self.proof_of_work() # Calculo el hash válido, pero no se almacena (Prototipo , cambiar??)

    def calculate_hash(self) -> str:
        block_string = f"{self.hash_anterior}{self.marca_de_tiempo}{self.merkle_root}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()



#Método clave, a mayor dificultad (000s), mayor tiempo que tarda un atacante/interesado. 

    def proof_of_work(self) -> str:
        while True:
            hash_result = self.calculate_hash()
            if hash_result.startswith("000"):
                return hash_result
            self.nonce += 1

    def __str__(self) -> str:
       
        merkle_tree_str = "\nNiveles del Merkle Tree:\n"
        for i, level in enumerate(reversed(self.merkle_niveles)):
            merkle_tree_str += f"  Level {i}:\n"
            for hash_val in level:
                merkle_tree_str += f"    {hash_val}\n"

        return (
            f"Bloque--------------------------------------------------------------------------------\n"
            f"Hash previo: {self.hash_anterior}\n"
            f"Marca de tiempo: {self.marca_de_tiempo}\n"
            f"Raiz del Merkle Tree: {self.merkle_root}\n"
            f"Nonce: {self.nonce}\n"
            f"Hash: {self.hash}\n" # Guardamos el hash, aunque no sería necesario
            f"Listado de transacciones:\n" +
            "\n".join([f"  {tx}" for tx in self.l_transacciones]) + "\n" +
            merkle_tree_str + "\n" + f"Fin de bloque--------------------------------------------------------\n"
        )

    # REVISAR FORMATO
    @property
    def merkle_data(self) -> List[List[str]]:
        return list(reversed(self.merkle_niveles)) if self.merkle_niveles else []

# Clase central, Blockchain 
class Blockchain:
    def __init__(self):
        # Implemento una lista enlazada
        self.chain = [self.crea_bloque_genesis()]

    def crea_bloque_genesis(self) -> Bloque:
        return Bloque("00000000000000", [], time.strftime("%Y-%m-%d %H:%M:%S"))

    def obtener_ultimo_bloque(self) -> Bloque:
        return self.chain[-1]

    def append_bloque(self, l_transacciones: List[Transaccion]):
        nuevo_bloque = Bloque(
            hash_anterior = self.obtener_ultimo_bloque().hash,
            l_transacciones = l_transacciones,
            marca_de_tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        self.chain.append(nuevo_bloque)
        
        print("\nÁrbol de Merkle del nuevo bloque:")
        for i, nivel in enumerate(reversed(nuevo_bloque.merkle_niveles)):
            print(f"Nivel {i}:")
            for valor_de_hash in nivel:
                print(f"  {valor_de_hash}")
        print(f"Raíz de Merkle: {nuevo_bloque.merkle_root}\n")

    def __str__(self) -> str:
        return "\n".join([str(bloque) for bloque in self.chain])