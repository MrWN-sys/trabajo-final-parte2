import socket
import pickle
import os
import sys
import json
from app import main

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
                print('Leaved correctly.')
                exit(0)
            if name:
                return name
    
    def iniciar_canciones(self):
        # 接收歌曲数据
        dir_path = os.path.join(os.path.dirname(__file__), 'client_library')
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        print(pickle.loads(self.client.recv(1024)))
        for cancion in self.info['canciones']:
            # 发送歌曲名字请求获取歌曲数据流
            self.client.sendall(pickle.dumps(cancion['titulo']))
            length = pickle.loads(self.client.recv(1024))
            data = b''
            while len(data) < length:
                data += self.client.recv(2048)
            with open(os.path.join(dir_path, f'{cancion["titulo"]}'), 'wb') as f:
                f.write(data)
        self.client.sendall(pickle.dumps('final'))# 打招呼说明结束传输歌曲数据
        print(pickle.loads(self.client.recv(1024)))

    def iniciar_information(self):
        # 接收元数据
        print('Initting information...')
        self.client.sendall(pickle.dumps('OK')) # 打招呼说明开始传输数据流
        length = pickle.loads(self.client.recv(1024))
        data = b''
        while len(data) < length:
            data += self.client.recv(2048)
        self.info = json.loads(data) # diccionario
        dict.update

    def send_information(self):
        # 检查不同，并且修改不同
        # 。。。。。。
        self.client.sendall(pickle.dumps('OK'))
        print('Saving information...')
        data = pickle.dumps(self.info)
        length = len(data)
        self.client.sendall(pickle.dumps(length))
        while len(data) > 0:
            self.client.sendall(data[:2048])
            data = data[2048:]
    
    def send_canciones(self):
        pass

    def main_client(self):
        self.client.connect((self.host, self.port))
        self.iniciar_information()
        self.iniciar_canciones()
        self.info['canciones'], self.info['listas'] = main(self.info['canciones'], self.info['listas']) # 载入数据
        self.send_information()
        self.send_canciones()
        self.client.close()

if __name__ == '__main__':
    host, port = sys.argv[1], int(sys.argv[2])
    client = Client(host, port)
    client.main_client()