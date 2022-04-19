from socket import *
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
            print('Connection to', self.address, ':', self.port, 'failed')
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
        print('Connected to', address, ':', port)
        return sock

    def start(self):
        try:
            while True:
                self.show_commands()
                commandStr = input('Enter command: ')

                commandList = commandStr.split(' ')

                if commandList[0].upper() not in ['HELP','LIST','DWLD','PWD','CD','QUIT']:
                    print("Unknown command.\n\n")
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
                    print(data, "\n\n")
        except Exception as e:
            print(f'{e} recieved.')

    def show_commands(self):
        print('''    -------------------------------------------------
    -------------------------------------------------
        Call one of the following functions:
        1.HELP               : Show this commands
        2.LIST               : List files
        3.PWD                : Show current dir
        4.CD dir_name        : Change directory
        5.DWLD dir_name      : Download file
        6.QUIT               : Exit
    --------------------------------------------------
    --------------------------------------------------
         ''')

    def download_file(self, filename, commandStr):
        print('Downloading', filename, 'from the server')

        self.sock.send(commandStr.encode())
        portnum = self.sock.recv(2048).decode()

        try:
            datasock = self.create_connection(self.address, int(portnum))
            
            downloaded = datasock.recv(3)
            print(downloaded.decode())
            if downloaded=="404".encode():
                print(filename,"not found.\n\n")
            else:
                size = int(datasock.recv(32).decode())
                print(size)
                downloaded = datasock.recv(size)
                f = open(filename, 'wb')
                f.write(downloaded)
                f.close()

            datasock.close()   
        except Exception as e:
            print(f'{e} recieved.')
            print('Data connection to', self.address, ':', portnum, 'failed')                  

    def close(self):
        self.sock.close()
        print('FTP client terminating...')
        quit()


ftpClient = FTPclient(HOST, PORT)
ftpClient.start()
