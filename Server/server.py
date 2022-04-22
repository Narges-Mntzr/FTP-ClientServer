import socket
from pyngrok import ngrok
from threading import Thread
import os
from datetime import datetime
import random
from tkinter import NONE
from colorama import Fore, Style

HOST = '127.0.0.1'
PORT = 2121  # command port


class Server(Thread):
    def __init__(self, comSock, address, id, firstLocation):
        Thread.__init__(self)
        self.id = id
        self.comSock = comSock  # command channel
        self.address = address

        self.cwd = self.firstLocation = firstLocation
        os.chdir(self.firstLocation)
        self.update_cwd()
        self.send_id()

    def run(self):  # override run method
        while True:
            try:
                data = self.comSock.recv(2048).decode('utf-8')
                dataList = data.split(' ')
                command = dataList[0].upper()
                argument = dataList[1:]
                result, text = self.run_commands(command, argument)

                if command != 'DWLD':
                    if result in ["400", "404"]:
                        self.log('error', text)
                        self.comSock.send((result + text).encode())
                    else:
                        self.log('success', f'{command} command DONE.')
                        self.comSock.send((result+text).encode())

                else:
                    if result == "200":
                        self.log('success', text)
                    elif result == "404":
                        self.log('error', text)

            except Exception as e:
                self.log('error', f'{e} recieved.')
                break

    def open_data_sock(self):
        dataPort = random.randint(3000, 50000)
        self.data_tunnel = ngrok.connect(dataPort,'tcp')
        self.comSock.send(str(self.data_tunnel).encode('utf-8'))

        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSock.bind((HOST, dataPort))
        self.serverSock.listen(5)
        self.dataSock, _address = self.serverSock.accept()
        self.log('success', f'Client connected to data channel:{_address}')

    def close_data_sock(self):
        ngrok.disconnect(self.data_tunnel)
        self.serverSock.close()
        self.dataSock.close()

    def update_cwd(self):
        self.cwd = os.getcwd()
        self.cwd = self.cwd.replace(self.firstLocation, "")
        self.cwd += "/"

    def run_commands(self, command, argument):
        if command == 'PWD':
            return "200", self.cwd

        elif command == 'CD':
            try:
                preCwd = self.firstLocation+self.cwd
                os.chdir(self.firstLocation+self.cwd+argument[0])
                
                if not os.getcwd().startswith(self.firstLocation):
                    os.chdir(preCwd)
                    self.update_cwd()
                    return '400', "Unable to access this folder."
                
                self.update_cwd()
                return "200", self.cwd
            except:
                return '404', f'{argument[0]} not found.'

        elif command == 'LIST':
            out = ""
            total_size = 0
            ls = os.listdir(self.firstLocation+self.cwd)
            for file in ls:
                total_size += os.path.getsize(self.firstLocation+self.cwd+file)
                if os.path.isdir(self.firstLocation+self.cwd+file):
                    out += ("> " + file + "\n")
                else:
                    out += (file + "\n")

            out += ("Total size: " + str(total_size))
            return "200", out

        elif command == 'DWLD':
            return self.DWLD(argument)

    def DWLD(self, argument):
        self.open_data_sock()

        try:
            file_path = self.firstLocation+self.cwd+argument[0]
            f = open(file_path, 'rb')
            self.dataSock.send("200".encode())
        except:
            self.dataSock.send("404".encode())
            self.close_data_sock()
            return '404', f'{argument} not found.'

        while True:
            data = f.read(2048)
            self.dataSock.send(data)
            if not data:
                break

        self.close_data_sock()
        return '200', f'{argument} uploaded.'

    def log(self, type, _msg):
        time = datetime.now().time()
        print(Fore.YELLOW + str(time))

        if type == 'success':
            print('\033[42m' + Fore.BLACK + type.upper()+'\033[0m')
            print(Fore.GREEN + f'Client{self.id}: ' + _msg)

        elif type == 'error':
            print('\033[41m' + Fore.BLACK + type.upper()+'\033[0m')
            print(Fore.RED + f'Client{self.id}: ' + _msg)
        print(Style.RESET_ALL)

    def send_id(self):
        self.comSock.send(str(self.id).encode())

    def __del__(self):
        self.comSock.close()


def main():
    os.chdir("Files")
    firstLocation = os.getcwd()

    ngrok.set_auth_token("286v8HrxqAl9O0Cg9d2aqyMaFG0_6ggrottX6UzwQxwCPyZfV")
    ssh_tunnel = ngrok.connect(2121,'tcp')
    print(ssh_tunnel)

    client_Id = 1

    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_sock.bind((HOST, PORT))
    listen_sock.listen(5)

    while True:
        connection, _address = listen_sock.accept()
        print(Style.RESET_ALL, end="")
        print(f'Client{client_Id} was connected\n')
        S = Server(connection, _address, client_Id, firstLocation)
        client_Id += 1
        S.start()


main()
