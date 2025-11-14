import pygame

class Cancion:
    id = 0

    def __init__(self, titulo: str,  artista: str, duracion: int, genero: str, archivo_mp3: str):
       Cancion.id += 1
       self.id = Cancion.id
       self.titulo = titulo
       self.artista = artista
       self.duracion = duracion
       self.genero = genero
       self.archivo = archivo_mp3
       self.changed = None

    def reproducir(self) -> None:
       # 初始化pygame
       pygame.init()
       pygame.mixer.init()
       # 下载并播放音乐
       pygame.mixer_music.load(self.archivo)
       pygame.mixer_music.play()
    
    def stop(self) -> None:
        pygame.mixer_music.pause()
       

    def edit_cancion(self, titulo: str, artista: str, duracion: int, genero: str, archivo:str):
       self.titulo = titulo if titulo else self.titulo
       self.artista = artista if artista else self.artista
       self.duracion = duracion if duracion else self.duracion
       self.genero = genero if genero else self.genero
       self.archivo = archivo if archivo else self.archivo
       self.changed = {'titulo': titulo, 'artista': artista, 'duracion': duracion, 'genero': genero, 'archivo_mp3': archivo}
    
    def mostrar_infos(self, sequence=None, normal=True) -> str:
        texto1 = f'{self.titulo} - {self.artista} ({round(float(self.duracion), 1)}s) '
        texto2 = f'[{self.genero}] -> {self.archivo}'
        if not normal:
            return f'{sequence}) ' + texto1
        else:
            return f'{self.id}) ' + texto1 + texto2
        
    def mostrar_data_parte2(self):
        data = {}
        keys = ['titulo', 'artista', 'duracion', 'genero', 'archivo_mp3']
        values = [self.titulo, self.artista, self.duracion, self.genero, self.archivo, self.id]
        for key, value in zip(keys, values):
            data[key] = value
        return data


class ListaReproduccion:
   def __init__(self, nombre:str):
       self.nombre = nombre
       self.canciones = []

   def anadir_cancion(self, id_cancion: int) -> bool:
       if id_cancion not in self.canciones:
           self.canciones.append(id_cancion)
           return True
       return False

   def quitar_cancion(self, id_cancion: int) -> bool:
       if id_cancion in self.canciones:
           self.canciones.remove(id_cancion)
           return True
       return False
   
   def mostrar_informacion(self) -> str:
       return f'{self.nombre} ({len(self.canciones)} canciones)'
   
   def mostrar_cancion(self, canciones: list[Cancion]) -> list[str]:
       return [cancion for cancion in canciones if cancion.id in self.canciones]


class PlataformaMusical:
   def __init__(self, canciones=[], listas=[], cancion_ids=[]):
       self.canciones = canciones
       self.listas = listas
       self.cancion_ids = cancion_ids

   def registrar_cancion(self, titulo: str, artista: str, duracion: int, genero: str, archivo:str) -> bool:
        for cancion in self.canciones:
           if cancion.titulo == titulo and cancion.artista == artista:
               return False
        cancion = Cancion(titulo, artista, duracion, genero, archivo)
        self.canciones.append(cancion)
        self.cancion_ids.append(cancion.id)
        return True
  
   def editar_cancion(self, id: int, titulo: str, artista: str, duracion: int, genero: str, archivo:str) -> bool:
       if id not in self.cancion_ids:
           return False
       for cancion in self.canciones:
           if cancion.id == id:
               song = cancion
       song.edit_cancion(titulo, artista, duracion, genero, archivo)
       return True
  
   def eliminar_cancion(self, id: int) -> bool:
       if id not in self.cancion_ids:
           return False
       self.canciones.remove([i for i in self.canciones if i.id == id][0])
       self.cancion_ids.remove(id)
       for lista in self.listas:
           if id in lista.canciones:
               lista.canciones.remove(id)
       return True
  
   def listar_canciones(self) -> list[Cancion]:
       return self.canciones
  
   def crear_lista(self, nombre: str) -> bool:
       if nombre not in [lista.nombre for lista in self.listas]:
           self.listas.append(ListaReproduccion(nombre))
           return True
       return False
  
   def borrar_lista(self, nombre: str) -> bool:
       for lista in self.listas:
           if lista.nombre == nombre:
               self.listas.remove(lista)
               return True
       return False
   
   def obtener_lista(self, nombre:str) -> ListaReproduccion:
       for lista in self.listas:
           if lista.nombre == nombre:
               return lista
