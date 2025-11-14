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
        length = len(data)
        client.sendall(pickle.dumps(length))
        while data:
            client.sendall(data[:2048])
            data = data[2048:]
        client.recv(1024)

    def load_service(self):
        self.service.bind(('127.0.0.1', self.port))
        self.service.listen()
   
    def check_name_is_using(self, client, name:str):
        with self.lock:
            if self.client_states.get(name, 0):
                client.sendall(pickle.dumps('The user is using.'))
                return False
            self.client_states[name] = 1
            client.sendall(pickle.dumps('Welcome.'))
        return True
   
    def transmit_song(self, client, path, name):
        client.sendall(pickle.dumps('Loading songs...'))
        print('Begin sending information...')
        while True:
            data = pickle.loads(client.recv(2048))
            print(data)
            if data == 'final':
                client.sendall(pickle.dumps('Loading songs correctly.'))
                print('End of sending information.')
                break
            with open(os.path.join(path, f'{data}'), 'rb') as f:
                data = f.read()
            self.send_data(data, client)
               
    def transmit_data(self, client, dir_path, client_path, name):        
        # 传输元数据
        client.recv(1024)
        with open(client_path, 'r') as f:
            info = json.loads(f.read())
        self.send_data(pickle.dumps(info), client)
        print('////////////////')
        self.transmit_song(client, os.path.join(dir_path, 'biblioteca'), name)

    def deal_with_old_data(self, old_data: dict, changed:dict):
        # deal with canciones
        for id, value in changed['canciones'].items():
            if not value['eliminar']:
                value.pop('eliminar')
                old_data['canciones'][id] = value
            else:
                old_data['canciones'].pop(id)
                path = os.path.join(os.path.dirname(__file__), 'biblioteca', value['titulo'])
                with self.lock:
                    os.remove(path + '.mp3')
        
        # deal with listas
        for lista in changed['listas']:
            if lista['eliminar']:
                old_data['listas'].remove(lista['nombre'])
            else:
                old_data['listas'].append(lista['nombre'])
        return old_data

    def receive_data(self, client, name: str, path: str) -> dict: # 接受客户端数据，只需要接受元数据
        client.recv(1024) # 打招呼说明开始
        print('Begin receiving information...')
        length = pickle.loads(client.recv(1024))
        client.sendall(pickle.dumps(True))
        data = b''
        while len(data) < int(length):
            data += client.recv(2048)
        client.sendall(pickle.dumps('End of receiving information'))
        data = pickle.loads(data) # receive data -> {'canciones': [{titulo: '', 'eliminar:False}]}
        with open(path, 'r') as f:
            old_data = json.load(f)
        new_data = self.deal_with_old_data(old_data, data)
        with open(path, 'w') as f:
            print(new_data)
            json.dump(new_data, f)
        return [value for key, value in old_data['canciones'].items() if key not in new_data['canciones'].keys()]

    def receive_cancion(self, client, canciones: list):
        client.sendall(pickle.dumps(True))
        print('Begin receiving canciones')
        # send path
        print(canciones)
        for i in canciones:
            client.sendall(pickle.dumps(i['archivo_mp3']))
            length = pickle.loads(client.recv(2048))
            data = b''
            for i in range(int(length) // 2048 + 1):
                data += client.recv(2048)
            with open(os.path.join(os.path.dirname(__file__), 'biblioteca', f'{i["titulo"]}.mp3'), 'wb') as f:
                f.write(data)
            client.sendall(pickle.dumps('OK'))
        client.sendall(pickle.dumps(False))
        print('End of receiving information')

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
        self.receive_cancion(client, canciones_new)
        self.close_client(name, client)


    def main(self):
        self.load_service()
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
