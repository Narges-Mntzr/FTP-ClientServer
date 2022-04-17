from ast import For
import socket
from threading import Thread
import os
from datetime import datetime
import random
from tkinter import NONE
from colorama import Fore, Back, Style

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
                dataList = data.split(' ')
                command = dataList[0].upper()
                argument = dataList[1:]

                result = self.run_commands(command, argument)
                if command != 'DWLD':
                    self.comSock.send(result.encode())
                    self.log('success',f'{command} command DONE.')
                else:
                    self.log('success',f'{argument} uploaded.')                    
            except socket.error as e:
                self.log('error',f'{e} recieved.')

    def open_data_sock(self):
        dataPort = random.randint(3000, 50000)
        self.comSock.send(str(dataPort).encode('utf-8'))

        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSock.bind((HOST, dataPort))
        self.serverSock.listen(5)
        self.dataSock, _address = self.serverSock.accept()
        self.log('success',f'Client connected to data channel:{_address}')

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

    def DWLD(self,argument):
        self.open_data_sock()
        file_path = self.firstLocation+self.cwd+argument[0]
        f = open(file_path, 'rb')
        while True:
            data = f.read(2048)
            self.dataSock.send(data)
            if not data:
                break
        self.close_data_sock()
        return NONE

    def log(self, type , _msg):
        time = datetime.now().time()
        print(Fore.YELLOW + str(time))
        if type == 'success':
            print(Back.GREEN + Fore.BLACK + type.upper())
            print(Style.RESET_ALL)
            print(Fore.GREEN + _msg)
        elif type == 'error':
            print(Back.RED + Fore.BLACK + type.upper())
            print(Style.RESET_ALL)
            print(Fore.RED + _msg)

    

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
