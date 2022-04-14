from socket import *

HOST = '127.0.0.1'
PORT = 2121


class FTPclient:
    def __init__(self, address, port):
        self.address = address
        self.port = port

        try:
            self.sock = self.create_connection(address, port)
        except:
            print('Connection to', self.address, ':', self.port, 'failed')
            self.close()

    def create_connection(self, address, port):
        print('Starting connection to', address, ':', port)

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

    # don't test
    def download_file(self, filename, commandStr):
        print('Downloading', filename, 'from the server')

        f = open(filename, 'w')

        self.sock.send(commandStr)
        portnum = self.sock.recv(2048)

        try:
            datasock = self.create_connection(self.address, portnum)

            while True:
                download = datasock.recv(2048)
                if not download:
                    break
                f.write(download)
            f.close()
            datasock.close()
        except:
            print('Data connection to', self.address, ':', portnum, 'failed')
            f.close()
            datasock.close()

    def close(self):
        self.sock.close()
        print('FTP client terminating...')
        quit()


ftpClient = FTPclient(HOST, PORT)
ftpClient.start()
