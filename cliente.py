import socket
import pickle
import sys

class Client:
    def __init__(self, host:str, port: int):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def begin(self):
        print('Arrancando cliente -/-')
        print('Procesando argumentos ---')
        self.client.connect((self.host, self.port))
        print(f'Argumentos correctos ip: {self.host} puerto: {self.port}')
        print('Conectado al servidor')

    def main(self):
        self.begin()
        self.client.sendall(pickle.dumps('Hey Yo Whasuup'))
        while True:
            info = self.client.recv(1024)
            if not info:
                print('Dude gone')
                break
            info = pickle.loads(info)
            if info == True or info.count('u') == 10:
                self.client.sendall(pickle.dumps('By dude'))
            else:
                whasup = info.split()[-1][:-1] + 'up'
                self.client.sendall(pickle.dumps(whasup))

        print('Cerrado la conexión con el servidor')
        self.client.close()

if __name__ == '__main__':
    host, port = '127.0.0.1', 55555
    client = Client(host, port)
    client.main()