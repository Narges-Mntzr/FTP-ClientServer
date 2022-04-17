import socket
from threading import Thread
import os
import time
import random

HOST = '127.0.0.1'
PORT = 2121  # command port


class Server(Thread):
    def __init__(self, comSock, address):
        Thread.__init__(self)
        self.comSock = comSock  # command channel
        self.address = address

        os.chdir("Files") #FIXME: 
        self.cwd = self.firstLocation = os.getcwd()
        self.update_cwd()

    def run(self):  # override run method
        while True:
            try:
                data = self.comSock.recv(2048).decode('utf-8')
                print('recieved data:', data)

                dataList = data.split(' ')
                command = dataList[0].upper()
                argument = dataList[1:]

                result = self.run_commands(command, argument)
                print(result)
                if command != 'DWLD':
                    self.comSock.send(result.encode())
            except socket.error as e:
                print(f'{e} recieved.')

            # TODO: call the command based on data

    def open_data_sock(self):
        dataPort = random.randint(3000, 50000)
        self.comSock.send(str(dataPort).encode('utf-8'))

        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSock.bind((HOST, dataPort))
        self.serverSock.listen(5)
        self.dataSock, _address = self.serverSock.accept()
        print("Client was connected to data channel")

    def close_data_sock(self):
        self.serverSock.close()
        self.dataSock.close()

    def update_cwd(self):
        self.cwd = os.getcwd()
        self.cwd = self.cwd.replace(self.firstLocation, "")
        self.cwd += "/"

    def run_commands(self, command, argument):
        if command == 'PWD':
            return "\t"+self.cwd
        elif command == 'CD':
            os.chdir(self.firstLocation+self.cwd+argument[0])
            self.update_cwd()
            return "\t"+self.cwd
        elif command == 'LIST':
            out = ""
            total_size = 0
            ls = os.listdir(self.firstLocation+self.cwd)
            for file in ls:
                total_size += os.path.getsize(self.firstLocation+self.cwd+file)
                if os.path.isdir(self.firstLocation+self.cwd+file):
                    out += ("\t> " + file + "\n")
                else:
                    out += ("\t" + file + "\n")

            out += ("\tTotal size: " + str(total_size) + "\n")
            return out
        elif command == 'DWLD':
            return(self.DWLD(argument))
    # Commands -----------

    def DWLD(self,argument):
        self.open_data_sock()
        file_path = self.firstLocation+self.cwd+argument[0]
        f = open(file_path, 'rb')
        while True:
            data = f.read(2048)
            self.dataSock.send(data)
            if not data:
                break
        print()
        self.close_data_sock()
        return '200'

        


def main():
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_sock.bind((HOST, PORT))
    listen_sock.listen(5)
    

    while True:
        connection, _address = listen_sock.accept()
        print("Client was connected")
        S = Server(connection, _address)
        S.start()


main()
