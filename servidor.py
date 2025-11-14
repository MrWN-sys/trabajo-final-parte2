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

    def send_data(self, data: bytes, client):
        length = len(data)
        client.sendall(pickle.dumps(length))
        while data:
            client.sendall(data[:2048])
            data = data[2048:]

    def load_service(self):
        self.service.bind((socket.gethostname(), self.port))
        self.service.listen()
    
    def check_name_is_using(self, client, name:str):
        if self.client_states.get(name, 0):
            client.sendall(pickle.dumps('The user is using.'))
            return False
        self.client_states[name] = 1
        client.sendall(pickle.dumps('Welcome.'))
        return True
    
    def transmit_song(self, client, path):
        client.sendall(pickle.dumps('Loading songs...'))
        print('Begin sending information...')
        while True:
            data = pickle.loads(client.recv(1024))
            if data == 'final':
                client.sendall(pickle.dumps('Loading songs correctly.'))
                print('End of sending information.')
                break
            with open(os.path.join(path, f'{data.lower()}.mp3'), 'rb') as f:
                data = f.read()
            self.send_data(data, client)
                

    def transmit_data(self, client, dir_path, client_path):        
        # 传输元数据
        with open(client_path, 'rb') as f:
            info = f.read()
        self.send_data(info, client)
        self.transmit_song(client, os.path.join(dir_path, 'biblioteca'))

    def receive_data(self, client, name: str, path: str): # 接受客户端数据，只需要接受元数据
        client.recv(1024) # 打招呼说明开始
        print('Begin receiving information...')
        length = pickle.loads(client.recv(1024))
        data = b''
        while len(data) < length:
            data += client.recv(2048)
        data = pickle.loads(data)
        with open(os.path.join(path, f'{name}.json'), 'w') as f:
                json.dump(data, f)

    def close_client(self, name: str, client):
        client.recv(1024)
        client.close()
        print(f'{name} is closed.')
        self.client_states[name] = 0

    def deal_client(self, name: str, client):
        dir_path = os.path.dirname(__file__)
        client_path = os.path.join(dir_path, 'datos_server', f'{name}.json')
        if not os.path.exists(client_path):
            with open(client_path, 'w') as f:
                json.dump({'canciones': [], 'listas': []}, f)
        self.transmit_data(client, dir_path, client_path) # 初始化数据
        self.receive_data(client, name, client_path)
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
    port = int(sys.argv[1])
    servidor = Servidor(port)
    servidor.main()
