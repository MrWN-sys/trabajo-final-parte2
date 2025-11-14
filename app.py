#!/usr/bin/env python3
"""Interfaz por consola para la PlataformaMusical (parte 1)."""
from musica.plataforma import PlataformaMusical

# Tools
def pedir_int(sign: str):
    answer = input(sign)
    try:
        return int(answer)
    except ValueError:
        return None
    
def mostrar_choices(begin: str, choice: dict) -> None:
    print(begin)
    for key, value in choice.items():
        print(f'{key}) {value}')

def mostrar_canciones(canciones, begin=None, normal=True) -> None:
    if begin:
        print(begin)
    for i in range(len(canciones)):
        print(canciones[i].mostrar_infos(i + 1, normal))

# Operation of songs
def menu_canciones(plataforma: PlataformaMusical) -> None:
    while True:
        choices = {1: 'Añadir canción', 2: 'Modificar canción', 3: 'Eliminar canción', 
                   4: 'Listar canciones', 0: 'Volver'}
        mostrar_choices('\n--- Gestión de canciones ---', choices)
        opc = pedir_int('> ')
        funciones = [anadir_cancion, modificar_cancion, eliminar_cancion, listar_cancion]
        if opc != 0:
            try:
                funciones[opc - 1](plataforma)
            except Exception:
                print('Opción inválida')
        else:
            break

def anadir_cancion(plataforma: PlataformaMusical) -> None:
    print('\n--- Añadir canción ---')
    infos = [input('Título: '), input('Artista: '), input('Duración (segundos): '), input('Género: '), input('Ruta a archivo MP3: ')]
    try:
        if plataforma.registrar_cancion(infos[0], infos[1], int(infos[2]), infos[3], infos[4]):
            print('Canción añadida correctamente')
        else:
            print('No se pudo añadir la canción. La canción ya existe.')
    except Exception:
        print('Duracion tiene ser un numero entero.')


def modificar_cancion(plataforma: PlataformaMusical) -> None:
    mostrar_canciones(plataforma.canciones, '\n--- Modificar canción ---\nCanciones disponibles:', False)
    seq = pedir_int('Selecciona número de la canción (0 para cancelar): ')
    if seq != 0 and seq and 0 < seq < len(plataforma.canciones) + 1:
        question = ['título', 'artista', 'duración', 'género', 'ruta MP3']
        answers = [input(f'Nuevo {i} (enter para dejar): ') for i in question]
        if plataforma.editar_cancion(plataforma.canciones[seq - 1].id, answers[0], answers[1], answers[2], answers[3], answers[4]):
            print('Modificado')
    elif seq != 0:
        print('Opción inválida')
    

def eliminar_cancion(plataforma: PlataformaMusical) -> None:
    mostrar_canciones(plataforma.canciones, '\n--- Eliminar canción ---\nCanciones disponibles:', False)
    seq = pedir_int('Selecciona número de la canción (0 para cancelar): ')
    if seq != 0:
        if plataforma.eliminar_cancion(plataforma.canciones[seq - 1].id):
            print('Eliminada')

def listar_cancion(plataforma: PlataformaMusical) -> None:
    print('\n--- Listar canciones ---')
    mostrar_canciones(plataforma.canciones)

# Operation of playing list
def menu_listas(plataforma: PlataformaMusical) -> None:
    while True:
        operations = {1: 'Crear lista', 2: 'Eliminar lista', 3: 'Ver contenido de lista', 4: 'Añadir canciones a lista',
                      5: 'Eliminar canción de lista', 0: 'Volver'}
        mostrar_choices('\n--- Gestión de listas ---', operations)
        opc = pedir_int('> ')
        funciones = [crear_lista, eliminar_lista, ver_lista, 'añadir', 'eliminar']
        if opc != 0:
            try:
                if opc == 4 or opc == 5:
                    operation_cancion_lista(plataforma, funciones[opc - 1])
                else:
                    funciones[opc - 1](plataforma)
            except Exception:
                print('Opción inválida')
        else:
            break

def crear_lista(plataforma: PlataformaMusical) -> None:
    print('\n--- Crear lista ---')
    name = input('Nombre de la lista: ')
    if plataforma.crear_lista(name):
        print('Creada')
    else:
        print('No se pudo crear la lista. La lista ya existe.')

def eliminar_lista(plataforma: PlataformaMusical) -> None:
    begin = '\n--- Eliminar lista ---\nListas disponibles: '
    mostrar_choices(begin, {i + 1: f'{plataforma.listas[i].nombre} ({len(plataforma.listas[i].canciones)} canciones)' for i in range(len(plataforma.listas))})
    seq = pedir_int('Selecciona número de la lista (0 para cancelar): ')
    if seq != 0:
        if plataforma.borrar_lista(plataforma.listas[seq - 1].nombre):
            print('Eliminada')

def ver_lista(plataforma: PlataformaMusical) -> None:
    begin = '\n--- Ver contenido de una lista ---\nListas disponibles: '
    mostrar_choices(begin, {i + 1: plataforma.listas[i].mostrar_informacion() for i in range(len(plataforma.listas))})
    seq = pedir_int('Selecciona número de la lista (0 para cancelar): ')
    if seq != 0:
        mostrar_canciones([cancion for cancion in plataforma.listas[seq - 1].mostrar_cancion(plataforma.canciones)], normal=False)

def operation_cancion_lista(plataforma: PlataformaMusical, choise: str):
    if choise == 'eliminar':
        begin = '\n--- Eliminar canciones de una lista ---\nListas disponibles: '
    else:
        begin = '\n--- Añadir canciones a una lista ---\nListas disponibles: '
    mostrar_choices(begin, {i + 1: plataforma.listas[i].mostrar_informacion() for i in range(len(plataforma.listas))})
    seq = pedir_int('Selecciona número de la lista (0 para cancelar): ')
    if seq != 0:
        cancion_list = plataforma.listas[seq - 1].mostrar_cancion(plataforma.canciones)
        cancion_list = cancion_list if choise == 'eliminar' else [i for i in plataforma.canciones if i not in cancion_list]
        mostrar_canciones(cancion_list, f'Canciones disponibles para {choise}: ', False)
        question = pedir_int(f'Selecciona número de la canción a {choise} (0 para cancelar): ')
        if question != 0:
                if choise == 'añadir':
                    if plataforma.listas[seq - 1].anadir_cancion(cancion_list[question - 1].id):
                        print('Añadida')
                else:
                    if plataforma.listas[seq - 1].quitar_cancion(cancion_list[question - 1].id):
                        print('Eliminada')

# Operation of playing music
def menu_reproduccion(plataforma: PlataformaMusical):
    while True:
        choices = {i + 1: f'{plataforma.listas[i].nombre} ({len(plataforma.listas[i].canciones)} canciones)' for i in range(len(plataforma.listas))}
        choices[0] = 'Volver'
        mostrar_choices('\n--- Reproducción ---', choices)
        seq_lista = pedir_int('Selecciona lista: ')
        if seq_lista != 0:
            try:
                canciones = [cancion for cancion in plataforma.listas[seq_lista - 1].mostrar_cancion(plataforma.canciones)]
                reproduccion_cancion(canciones)
            except Exception:
                print('Opción inválida')
        else:
            break

def reproduccion_cancion(canciones: list):
    running = True
    while running:
        r = 0
        if not len(canciones):
            print('En la lista no hay canciones para reproducir.')
            break
        while r < len(canciones):
            print(f'\nReproduciendo: {canciones[r].titulo} - {canciones[r].artista} ({float(canciones[r].duracion)}s)')
            print('n) Siguiente, p) Anterior, s) Salir reproducción')
            try:
                canciones[r].reproducir()
                question = input('> ')
                canciones[r].stop()
                if question == 'n':
                    r += 1
                elif question == 'p':
                    r -= 1
                elif question == 's':
                    running = False
                    break
            except Exception:
                print('El fichero de la musica no existe')
                r += 1

# The main code
def main():
    plataforma = PlataformaMusical()
    while True:
        print('\n=== Plataforma Musical ===')
        print('1) Gestionar canciones')
        print('2) Gestionar listas')
        print('3) Reproducción')
        print('0) Salir')
        opc = pedir_int('> ')
        if opc == 1:
            menu_canciones(plataforma)
        elif opc == 2:
            menu_listas(plataforma)
        elif opc == 3:
            menu_reproduccion(plataforma)
        elif opc == 0:
            print('Hasta luego')
            break
        else:
            print('Opción inválida')
            

if __name__ == '__main__':
    main()
