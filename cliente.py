import socket
import pickle
import os
import sys
from app import *
from musica.plataforma import PlataformaMusical, Cancion, ListaReproduccion


# 初始化数据，在刚开启的时候接收服务端的数据（元数据还有歌曲数据）

class Client:
    def __init__(self, host: str, port: int):
        self.name = self.ask_name()
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.info = None

    def ask_name(self):
        while True:
            name = input('Name (q to quit): ').strip()
            if name == 'q':
                print('Leave correctly.')
                exit(0)
            if name:
                return name
            
    def recv_data(self):
        length = pickle.loads(self.client.recv(1024))
        data = b''
        while len(data) < int(length):
            data += self.client.recv(2048)
        return data
    
    def send_data(self, data):
        self.client.sendall(pickle.dumps(len(data)))
        for i in range(len(data) // 2048 + 1):
            self.client.sendall(data[i * 2048: 2048 * (i + 1)])
        print(pickle.loads(self.client.recv(1024)))

    def iniciar_canciones(self):
        # 接收歌曲数据
        dir_path = os.path.join(os.path.dirname(__file__), 'client_library')
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        self.client.recv(1024) # True
        print('Begin loading songs...')
        for cancion in self.info['canciones'].values():
            # 发送歌曲名字.mp3请求获取歌曲数据流
            print(f"Loading 《{cancion['titulo']}》 ......")
            self.client.sendall(pickle.dumps(cancion['archivo_mp3'].split('\\')[-1]))
            data = self.recv_data()
            with open(os.path.join(dir_path, cancion['archivo_mp3'].split('\\')[-1]), 'wb') as f:
                f.write(data)
        self.client.sendall(pickle.dumps('final'))# 打招呼说明结束传输歌曲数据
        self.client.recv(1024) # True
        print('Loading songs correctly.')

    def iniciar_information(self):
        # 接收元数据
        print('Initting information...')
        self.client.sendall(pickle.dumps('OK')) # 打招呼说明开始传输数据流
        data = self.recv_data()
        self.info = pickle.loads(data) # diccionario
    
    def operate(self) -> tuple:
        canciones, listas = [], []
        for id, c in self.info['canciones'].items():
            cancion = Cancion(c['titulo'], c['artista'], int(c['duracion']), c['genero'], c['archivo_mp3'])
            cancion.id = id
            canciones.append(cancion)
        for nombre, c in self.info['listas'].items():
            lista = ListaReproduccion(nombre)
            lista.anadir_lista_de_cancion(c)
            listas.append(lista)
        canciones_ids = [c.id for c in canciones]
        plataforma = PlataformaMusical(canciones.copy(), listas, canciones_ids) # load information to plataforma
        while True:
            choices = {1: 'Gestionar canciones', 2: 'Gestionar listas', 3: 'Reproducción', 0: 'Volver'}
            mostrar_choices('\n=== Plataforma Musical ===', choices)
            opc = pedir_int('> ')
            funciones = [menu_canciones, menu_listas, menu_reproduccion, listar_cancion]
            if opc != 0:
                try:
                    funciones[opc - 1](plataforma)
                except Exception:
                    print('Opción inválida')
            else:
                print('Hasta luego')
                break
        return (plataforma, canciones, listas)

    def send_information(self, plataforma: PlataformaMusical, canciones:list[Cancion], listas:list[ListaReproduccion]): # json information
        # deal with the new informatinon
        self.client.sendall(pickle.dumps('OK'))
        print('Saving information...')
        cancion_l = [i for i in canciones if i not in plataforma.canciones] + plataforma.canciones
        lista_l = [i for i in listas if i not in plataforma.listas] + plataforma.listas
        data = {'canciones':{}, 'listas':[]} # data -> {'canciones': {'id': {titulo: '', 'eliminar:False}}}
        for c in cancion_l:
            if c in plataforma.canciones and c not in canciones:
                if c not in canciones:
                    info = c.mostrar_data_parte2()
                    info['eliminar'] = False
                    data['canciones'][c.id] = info
            elif c in canciones and c not in plataforma.canciones:
                data['canciones'][c.id] = {'eliminar': True}
            elif c.changed:
                info = c.changed
                info['eliminar'] = False
                data['canciones'][c.id] = info
        
        for l in lista_l:
            if l not in listas and l in plataforma.listas or l.changed:
                data['listas'].append({'nombre': l.nombre, 'canciones': l.canciones, 'eliminar': False})
            elif l in listas and l not in plataforma.listas:
                data['listas'].append({'nombre': l.nombre, 'eliminar': True})

        self.send_data(pickle.dumps(data))
        print('End of sending information')

    def send_canciones(self):
        self.client.recv(1024)
        print('Begin sending canciones')
        # begin to send music
        while True:
            path = pickle.loads(self.client.recv(1024))
            if path == False:
                break
            with open(path, 'rb') as f:
                info = f.read()
            self.send_data(info)
        print('End of sending canciones')

    def main_client(self):
        self.client.connect((self.host, self.port))
        self.client.sendall(pickle.dumps(self.name))
        info = pickle.loads(self.client.recv(1024))
        print(info)
        if info != 'The user is using.':
            # iniciar informacion 
            self.iniciar_information()
            self.iniciar_canciones()
            # operacion del cliente
            plataforma, canciones, listas = self.operate()
            # send informacion difference to service
            self.send_information(plataforma, canciones, listas)
            self.send_canciones()
        self.client.close()
 
if __name__ == '__main__':
    client = Client('127.0.0.1', 12345)
    client.main_client()