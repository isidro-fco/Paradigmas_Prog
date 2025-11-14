import json
import os
from abc import ABC, abstractmethod

# --- Clases Base y Abstractas (Abstracción) ---

class ItemBiblioteca(ABC):
    """
    Clase abstracta base para todos los ítems de la biblioteca.
    Define la interfaz común (Abstracción).
    """
    def __init__(self, id_item, titulo, cantidad):
        # Encapsulamiento: Atributos protegidos
        self._id_item = id_item
        self._titulo = titulo
        self._cantidad = cantidad
        self._cantidad_disponible = cantidad

    # --- Encapsulamiento (Getters y Setters) ---
    def get_id(self):
        return self._id_item

    def get_titulo(self):
        return self._titulo

    def get_cantidad_disponible(self):
        return self._cantidad_disponible

    def prestar(self):
        """ Reduce la cantidad disponible si es posible. """
        if self._cantidad_disponible > 0:
            self._cantidad_disponible -= 1
            return True
        return False

    def devolver(self):
        """ Aumenta la cantidad disponible. """
        if self._cantidad_disponible < self._cantidad:
            self._cantidad_disponible += 1
            return True
        return False

    @abstractmethod
    def mostrar_detalles(self):
        """
        Método abstracto (Polimorfismo).
        Cada subclase DEBE implementar esto.
        """
        pass

    @abstractmethod
    def to_dict(self):
        """ Convierte el objeto a un diccionario para serialización JSON. """
        return {
            "id_item": self._id_item,
            "titulo": self._titulo,
            "cantidad": self._cantidad,
            "cantidad_disponible": self._cantidad_disponible,
            "tipo": self.__class__.__name__  # Guarda el nombre de la clase
        }

# --- Clases Derivadas (Herencia) ---

class Libro(ItemBiblioteca):
    """
    Clase para Libros, hereda de ItemBiblioteca (Herencia).
    """
    def __init__(self, id_item, titulo, cantidad, autor, anio_publicacion, genero):
        super().__init__(id_item, titulo, cantidad)
        self._autor = autor
        self._anio_publicacion = anio_publicacion
        self._genero = genero

    def mostrar_detalles(self):
        """
        Implementación específica para Libro (Polimorfismo).
        """
        print(f"--- LIBRO ---")
        print(f"  ID:       {self._id_item}")
        print(f"  Título:   {self._titulo}")
        print(f"  Autor:    {self._autor}")
        print(f"  Año:      {self._anio_publicacion}")
        print(f"  Género:   {self._genero}")
        print(f"  Disponibles: {self._cantidad_disponible}/{self._cantidad}")

    def to_dict(self):
        """ Extiende el to_dict base para incluir atributos de Libro. """
        data = super().to_dict()
        data.update({
            "autor": self._autor,
            "anio_publicacion": self._anio_publicacion,
            "genero": self._genero
        })
        return data

    @classmethod
    def from_dict(cls, data):
        """ Crea un objeto Libro desde un diccionario (para cargar desde JSON). """
        libro = cls(
            data['id_item'],
            data['titulo'],
            data['cantidad'],
            data['autor'],
            data['anio_publicacion'],
            data['genero']
        )
        # Restaura el estado de cantidad disponible
        libro._cantidad_disponible = data.get('cantidad_disponible', data['cantidad'])
        return libro


class Revista(ItemBiblioteca):
    """
    Clase para Revistas, hereda de ItemBiblioteca (Herencia).
    """
    def __init__(self, id_item, titulo, cantidad, editorial, numero, frecuencia):
        super().__init__(id_item, titulo, cantidad)
        self._editorial = editorial
        self._numero = numero
        self._frecuencia = frecuencia

    def mostrar_detalles(self):
        """
        Implementación específica para Revista (Polimorfismo).
        """
        print(f"--- REVISTA ---")
        print(f"  ID:         {self._id_item}")
        print(f"  Título:     {self._titulo}")
        print(f"  Editorial:  {self._editorial}")
        print(f"  Número:     {self._numero}")
        print(f"  Frecuencia: {self._frecuencia}")
        print(f"  Disponibles: {self._cantidad_disponible}/{self._cantidad}")

    def to_dict(self):
        """ Extiende el to_dict base para incluir atributos de Revista. """
        data = super().to_dict()
        data.update({
            "editorial": self._editorial,
            "numero": self._numero,
            "frecuencia": self._frecuencia
        })
        return data

    @classmethod
    def from_dict(cls, data):
        """ Crea un objeto Revista desde un diccionario (para cargar desde JSON). """
        revista = cls(
            data['id_item'],
            data['titulo'],
            data['cantidad'],
            data['editorial'],
            data['numero'],
            data['frecuencia']
        )
        revista._cantidad_disponible = data.get('cantidad_disponible', data['cantidad'])
        return revista

# --- Clase Usuario ---

class Usuario:
    """ Clase para representar a los usuarios de la biblioteca. """
    def __init__(self, id_usuario, nombre):
        self._id_usuario = id_usuario
        self._nombre = nombre
        self._items_prestados = [] # Lista de IDs de ítems

    def get_id(self):
        return self._id_usuario

    def get_nombre(self):
        return self._nombre

    def prestar_item(self, id_item):
        """ Agrega un ID de ítem a la lista de prestados del usuario. """
        if id_item not in self._items_prestados:
            self._items_prestados.append(id_item)
            return True
        return False # Ya lo tiene

    def devolver_item(self, id_item):
        """ Quita un ID de ítem de la lista de prestados. """
        if id_item in self._items_prestados:
            self._items_prestados.remove(id_item)
            return True
        return False # No lo tiene

    def mostrar_detalles(self):
        print(f"--- USUARIO ---")
        print(f"  ID:     {self._id_usuario}")
        print(f"  Nombre: {self._nombre}")
        print(f"  Items Prestados: {len(self._items_prestados)}")
        if self._items_prestados:
            print(f"    IDs: {', '.join(self._items_prestados)}")

    def to_dict(self):
        """ Convierte el objeto a un diccionario para serialización JSON. """
        return {
            "id_usuario": self._id_usuario,
            "nombre": self._nombre,
            "items_prestados": self._items_prestados
        }

    @classmethod
    def from_dict(cls, data):
        """ Crea un objeto Usuario desde un diccionario. """
        usuario = cls(data['id_usuario'], data['nombre'])
        usuario._items_prestados = data['items_prestados']
        return usuario

# --- Clase Principal de la Biblioteca (Controladora) ---

class Biblioteca:
    """
    Clase que gestiona todos los ítems, usuarios y operaciones.
    (Encapsulamiento de la lógica de negocio).
    """
    def __init__(self, archivo_json="biblioteca.json"):
        self._items = {} # Diccionario para acceso rápido por ID
        self._usuarios = {} # Diccionario para acceso rápido por ID
        self._archivo_json = archivo_json

    def registrar_libro(self):
        """ Pide datos y crea un nuevo objeto Libro. """
        try:
            id_item = input("ID (único): ")
            if id_item in self._items:
                print("Error: Ya existe un ítem con ese ID.")
                return
            titulo = input("Título: ")
            cantidad = int(input("Cantidad: "))
            autor = input("Autor: ")
            anio = int(input("Año de Publicación: "))
            genero = input("Género: ")

            libro = Libro(id_item, titulo, cantidad, autor, anio, genero)
            self._items[id_item] = libro
            print(f"Libro '{titulo}' registrado exitosamente.")
        except ValueError:
            print("Error: Entrada inválida. Cantidad y Año deben ser números.")
        except Exception as e:
            print(f"Error inesperado: {e}")

    def registrar_revista(self):
        """ Pide datos y crea un nuevo objeto Revista. """
        try:
            id_item = input("ID (único): ")
            if id_item in self._items:
                print("Error: Ya existe un ítem con ese ID.")
                return
            titulo = input("Título: ")
            cantidad = int(input("Cantidad: "))
            editorial = input("Editorial: ")
            numero = int(input("Número: "))
            frecuencia = input("Frecuencia (Ej. Mensual): ")

            revista = Revista(id_item, titulo, cantidad, editorial, numero, frecuencia)
            self._items[id_item] = revista
            print(f"Revista '{titulo}' registrada exitosamente.")
        except ValueError:
            print("Error: Entrada inválida. Cantidad y Número deben ser números.")
        except Exception as e:
            print(f"Error inesperado: {e}")

    def registrar_usuario(self):
        """ Pide datos y crea un nuevo objeto Usuario. """
        try:
            id_usuario = input("ID de Usuario (único): ")
            if id_usuario in self._usuarios:
                print("Error: Ya existe un usuario con ese ID.")
                return
            nombre = input("Nombre: ")
            
            usuario = Usuario(id_usuario, nombre)
            self._usuarios[id_usuario] = usuario
            print(f"Usuario '{nombre}' registrado exitosamente.")
        except Exception as e:
            print(f"Error inesperado: {e}")

    def buscar_item(self, id_item):
        return self._items.get(id_item)

    def buscar_usuario(self, id_usuario):
        return self._usuarios.get(id_usuario)

    def realizar_prestamo(self):
        """ Lógica de negocio para prestar un ítem a un usuario. """
        id_usuario = input("ID del Usuario: ")
        id_item = input("ID del Ítem a prestar: ")

        usuario = self.buscar_usuario(id_usuario)
        item = self.buscar_item(id_item)

        if not usuario:
            print("Error: Usuario no encontrado.")
            return
        if not item:
            print("Error: Ítem no encontrado.")
            return

        # 1. Intentar prestar el ítem (reduce cantidad disponible)
        if item.prestar():
            # 2. Asignar ítem al usuario
            if usuario.prestar_item(id_item):
                print(f"Préstamo exitoso: '{item.get_titulo()}' a '{usuario.get_nombre()}'.")
            else:
                # Caso raro: el usuario ya lo tenía, revertir
                item.devolver()
                print("Error: El usuario ya tiene este ítem prestado.")
        else:
            print(f"Error: No hay copias disponibles de '{item.get_titulo()}'.")

    def realizar_devolucion(self):
        """ Lógica de negocio para devolver un ítem. """
        id_usuario = input("ID del Usuario: ")
        id_item = input("ID del Ítem a devolver: ")

        usuario = self.buscar_usuario(id_usuario)
        item = self.buscar_item(id_item)

        if not usuario:
            print("Error: Usuario no encontrado.")
            return
        if not item:
            print("Error: Ítem no encontrado.")
            return

        # 1. Quitar ítem del usuario
        if usuario.devolver_item(id_item):
            # 2. Devolver ítem al inventario
            item.devolver()
            print(f"Devolución exitosa: '{item.get_titulo()}' de '{usuario.get_nombre()}'.")
        else:
            print("Error: El usuario no tenía este ítem prestado.")

    def mostrar_items(self):
        """
        Muestra detalles de todos los ítems.
        (Demuestra Polimorfismo en acción).
        """
        if not self._items:
            print("\nNo hay ítems registrados en la biblioteca.")
            return
        
        print("\n--- INVENTARIO DE LA BIBLIOTECA ---")
        # Itera sobre los objetos y llama a su método polimórfico
        for item in self._items.values():
            item.mostrar_detalles()
            print("-" * 20)

    def mostrar_usuarios(self):
        """ Muestra detalles de todos los usuarios. """
        if not self._usuarios:
            print("\nNo hay usuarios registrados.")
            return
        
        print("\n--- USUARIOS DE LA BIBLIOTECA ---")
        for usuario in self._usuarios.values():
            usuario.mostrar_detalles()
            print("-" * 20)

    def guardar_datos(self):
        """ Serializa el estado actual de la biblioteca a JSON. """
        try:
            data_to_save = {
                "items": [item.to_dict() for item in self._items.values()],
                "usuarios": [user.to_dict() for user in self._usuarios.values()]
            }
            with open(self._archivo_json, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=4, ensure_ascii=False)
            print(f"Datos guardados exitosamente en '{self._archivo_json}'.")
        except IOError as e:
            print(f"Error al guardar datos: {e}")
        except Exception as e:
            print(f"Error inesperado al serializar datos: {e}")

    def cargar_datos(self):
        """ Deserializa el estado desde JSON al iniciar. """
        if not os.path.exists(self._archivo_json):
            print("No se encontró archivo de datos. Iniciando biblioteca vacía.")
            return

        try:
            with open(self._archivo_json, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Diccionario de mapeo para reconstruir objetos
            constructores = {
                "Libro": Libro.from_dict,
                "Revista": Revista.from_dict
            }

            # Cargar ítems
            for item_data in data.get("items", []):
                tipo = item_data.get("tipo")
                constructor = constructores.get(tipo)
                if constructor:
                    item = constructor(item_data)
                    self._items[item.get_id()] = item
                else:
                    print(f"Advertencia: Tipo de ítem desconocido '{tipo}' encontrado en JSON.")

            # Cargar usuarios
            for user_data in data.get("usuarios", []):
                usuario = Usuario.from_dict(user_data)
                self._usuarios[usuario.get_id()] = usuario
            
            print(f"Datos cargados exitosamente desde '{self._archivo_json}'.")
        except json.JSONDecodeError:
            print(f"Error: El archivo '{self._archivo_json}' está corrupto o mal formateado.")
        except Exception as e:
            print(f"Error inesperado al cargar datos: {e}")

# --- Menú Principal de Interacción ---

def mostrar_menu():
    print("\n--- MENÚ SISTEMA DE BIBLIOTECA (POO) ---")
    print("1. Registrar nuevo Libro")
    print("2. Registrar nueva Revista")
    print("3. Registrar nuevo Usuario")
    print("4. Realizar Préstamo")
    print("5. Realizar Devolución")
    print("6. Mostrar todos los Ítems (Inventario)")
    print("7. Mostrar todos los Usuarios")
    print("8. Guardar y Salir")
    print("-----------------------------------------")

def main():
    """ Función principal que ejecuta el bucle del menú. """
    biblioteca = Biblioteca(archivo_json="biblioteca_data.json")
    biblioteca.cargar_datos()
    while True:
        mostrar_menu()
        try:
            opcion = input("Seleccione una opción: ")
            if opcion == '1':
                biblioteca.registrar_libro()
            elif opcion == '2':
                biblioteca.registrar_revista()
            elif opcion == '3':
                biblioteca.registrar_usuario()
            elif opcion == '4':
                biblioteca.realizar_prestamo()
            elif opcion == '5':
                biblioteca.realizar_devolucion()
            elif opcion == '6':
                biblioteca.mostrar_items()
            elif opcion == '7':
                biblioteca.mostrar_usuarios()
            elif opcion == '8':
                biblioteca.guardar_datos()
                print("Saliendo del sistema. ¡Hasta pronto!")
                break
            else:
                print("Opción no válida. Por favor, intente de nuevo.")
        except KeyboardInterrupt:
            print("\nInterrupción detectada. Guardando datos antes de salir...")
            biblioteca.guardar_datos()
            break
        except Exception as e:
            print(f"Ha ocurrido un error inesperado: {e}")
            # Opcionalmente, guardar antes de un error crítico
            # biblioteca.guardar_datos()

if __name__ == "__main__":
    main()