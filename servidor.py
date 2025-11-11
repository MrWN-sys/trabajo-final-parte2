import socket
import pickle
import sys

class Servidor:
    def __init__(self, port: int):
        self.host = '127.0.0.1'
        self.port = port
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def begin(self):
        print('Arrancando servidor -/-')
        print('Procesando argumentos ---')
        self.servidor.bind((self.host, self.port))
        print(f'Argumentos correctos ip: {self.host} puerto: {self.port}')
        self.servidor.listen(1)

    def main(self):
        self.begin()
        cliente, addr = self.servidor.accept()
        print(f'Dude ringing: {addr}')
        while True:
            info = cliente.recv(1024)
            if not info:
                break
            info = pickle.loads(info)
            print(info)
            if info.count('u') == 10:
                cliente.sendall(pickle.dumps(True))
            else:
                if info == 'By dude':
                    break
                whasup = info.split()[-1][:-1] + 'up'
                cliente.sendall(pickle.dumps(whasup))
        print('Apagando el servidor ...')
        self.servidor.close()

if __name__ == '__main__':
    port = 12345
    servidor = Servidor(port)
    servidor.main()


