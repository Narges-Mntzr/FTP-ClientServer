from socket import *
from colorama import Fore, Back, Style
from datetime import datetime
import os

HOST = '127.0.0.1'
PORT = 2121


class FTPclient:
    def __init__(self, address, port):
        self.address = address
        self.port = port

        try:
            self.sock = self.create_connection(address, port)
            self.get_id()
            self.dir = self.create_directory()
        except:
            self.log('error', 'Connection to '+ str(self.address) + ' : '+ str(self.port) + ' failed')
            self.close()

    def create_directory(self):
        parent_dir = os.getcwd()
        path = os.path.join(parent_dir, self.id)
        os.mkdir(path)
        os.chdir(path)

    def get_id(self):
        self.id = self.sock.recv(10).decode()

    def create_connection(self, address, port):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((address, port))
        self.log('success','Connected to '+ str(address) + ' : '+ str(port))
        return sock

    def start(self):
        try:
            while True:
                self.show_commands()
                commandStr = input('Enter command: ')

                commandList = commandStr.split(' ')

                if commandList[0].upper() not in ['HELP', 'LIST', 'DWLD', 'PWD', 'CD', 'QUIT']:
                    self.log('error', "Unknown command.")
                    continue

                if commandList[0].upper() == 'HELP':
                    # This command will show list of commands
                    continue
                elif commandList[0].upper() == 'QUIT':
                    self.close()
                elif commandList[0].upper() == 'DWLD':
                    self.download_file(commandList[1], commandStr)
                else:
                    self.sock.send(commandStr.encode())
                    data = self.sock.recv(2048).decode()
                    if data[:3] == "200":
                        self.log('success', data[3:])
                    else:
                        self.log('error', data[3:])
                    # TODO: add log here

        except Exception as e:
            self.log('error', f'{e} recieved.')

    def show_commands(self):
        print(Fore.CYAN+'\n-------------------------------------------------')
        print(Fore.MAGENTA+'''
        Call one of the following functions:
        1.HELP               : Show this commands
        2.LIST               : List files
        3.PWD                : Show current dir
        4.CD dir_name        : Change directory
        5.DWLD dir_name      : Download file
        6.QUIT               : Exit
         ''')
        print(Fore.CYAN+'-------------------------------------------------')
        print(Style.RESET_ALL)

    def download_file(self, filename, commandStr):
        self.log('success', 'Downloading ' + filename + ' from the server')

        self.sock.send(commandStr.encode())
        portnum = self.sock.recv(2048).decode()

        try:
            datasock = self.create_connection(self.address, int(portnum))

            downloaded = datasock.recv(3)
            if downloaded == "404".encode():
                self.log('error', filename+" not found.")
            else:
                size = int(datasock.recv(32).decode())
                downloaded = datasock.recv(size)
                f = open(filename, 'wb')
                f.write(downloaded)
                f.close()
                self.log('success', filename+" downloaded.")

            datasock.close()
        except Exception as e:
            self.log('error', f'{e} recieved.')
            self.log('error', 'Data connection to ' +
                     str(self.address) + ' : ' + str(portnum) + 'failed')

    def close(self):
        self.sock.close()
        print('FTP client terminating...')
        quit()

    def log(self, type, _msg):
        time = datetime.now().time()
        print(Fore.YELLOW + str(time))

        if type == 'success':
            print(Back.GREEN + Fore.BLACK + type.upper())
            print(Style.RESET_ALL, end="")
            print(Fore.GREEN + _msg, end="")

        elif type == 'error':
            print(Back.RED + Fore.BLACK + type.upper())
            print(Style.RESET_ALL, end="")
            print(Fore.RED + _msg, end="")

        print(Style.RESET_ALL)


ftpClient = FTPclient(HOST, PORT)
ftpClient.start()
