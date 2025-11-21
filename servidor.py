import pickle
import socket
import threading
import json
import sys
import os


class Servidor:
    def __init__(self, port: int):
        self.port = port
        self.service = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client_states = {}
        self.lock = threading.Lock()

    def send_data(self, data: bytes, client):
        client.sendall(pickle.dumps(len(data)))
        while data:
            client.sendall(data[:2048])
            data = data[2048:]

    def recv_data(self, client):
        length = pickle.loads(client.recv(1024))
        data = b''
        while len(data) < int(length):
            data += client.recv(2048)
        return data
    
    def check_name_is_using(self, client, name:str):
        with self.lock:
            if self.client_states.get(name, 0):
                client.sendall(pickle.dumps('The user is using.'))
                return False
            self.client_states[name] = 1
            client.sendall(pickle.dumps('Welcome.'))
        return True
   
    def transmit_song(self, client, path, name):
        print(f'Begin sending information to {name}...')
        while True:
            song_name = pickle.loads(client.recv(2048))
            if song_name == 'final':
                client.sendall(pickle.dumps(True))
                print(f'End of sending information to {name}.')
                break
            with self.lock:
                with open(os.path.join(path, f'{song_name}'), 'rb') as f:
                    data = f.read()
            self.send_data(data, client)
               
    def transmit_data(self, client, dir_path, client_path, name):        
        # 传输元数据
        client.recv(1024)
        with open(client_path, 'r') as f:
            info = json.loads(f.read())
        self.send_data(pickle.dumps(info), client)
        self.transmit_song(client, os.path.join(dir_path, 'biblioteca'), name)

    def deal_with_old_data(self, old_data: dict, changed:dict):
        # deal with canciones
        for id, value in changed['canciones'].items():
            if not value['eliminar']:
                value.pop('eliminar')
                old_data['canciones'][id] = value
            else:
                path = os.path.join(os.path.dirname(__file__), 'biblioteca', old_data['canciones'][id]['archivo_mp3'].split('\\')[-1])
                old_data['canciones'].pop(id)
                with self.lock:
                    os.remove(path)
        
        # deal with listas
        for lista in changed['listas']:
            if lista['eliminar']:
                old_data['listas'].remove(lista['nombre'])
            else:
                old_data['listas'][lista['nombre']] = lista['canciones']
        return old_data

    def receive_data(self, client, name: str, path: str) -> list: # 接受客户端数据，只需要接受元数据
        print(f'Begin receiving information from {name}...')
        data = pickle.loads(self.recv_data(client)) # receive data -> {'canciones': [{titulo: '', 'eliminar:False}]}
        with open(path, 'r') as f:
            old_data = json.load(f)
        print(old_data)
        new_data = self.deal_with_old_data(old_data, data)
        print(new_data)
        with open(path, 'w') as f:
            json.dump(new_data, f)
        return [value for key, value in old_data['canciones'].items() if key not in new_data['canciones'].keys()]

    def receive_cancion(self, client, canciones: list, name: str):
        # send path
        for i in canciones:
            print(f'Receiving 《{i["titulo"]}》 from {name}')
            client.sendall(pickle.dumps(i['archivo_mp3']))
            data = self.recv_data(client)
            with self.lock:
                with open(os.path.join(os.path.dirname(__file__), 'biblioteca', i['archivo_mp3'].split('\\')[-1]), 'wb') as f:
                    f.write(data)
                    print(os.path.join(os.path.dirname(__file__), 'biblioteca', i['archivo_mp3'].split('\\')[-1]))
        client.sendall(pickle.dumps(False))

    def close_client(self, name: str, client):
        client.close()
        print(f'{name} is closed.')
        self.client_states[name] = 0

    def deal_client(self, name: str, client):
        dir_path = os.path.dirname(__file__)
        client_path = os.path.join(dir_path, 'datos_server', f'{name}.json')
        if not os.path.exists(client_path):
            with open(client_path, 'w') as f:
                json.dump({'canciones': {}, 'listas': {}}, f)
        self.transmit_data(client, dir_path, client_path, name) # 初始化数据
        canciones_new = self.receive_data(client, name, client_path)
        print(canciones_new)
        self.receive_cancion(client, canciones_new, name)
        self.close_client(name, client)

    def main(self):
        self.service.bind(('127.0.0.1', self.port))
        self.service.listen()
        try:
            while True:
                client, addr = self.service.accept()
                name = pickle.loads(client.recv(1024))
                if self.check_name_is_using(client, name):
                    threading.Thread(target=self.deal_client, args=[name, client]).start()
                else:
                    client.close()
        except KeyboardInterrupt:
            print('Closing the service...')
        self.service.close()

if __name__ == '__main__':
    port = 12345
    servidor = Servidor(port)
    servidor.main()
