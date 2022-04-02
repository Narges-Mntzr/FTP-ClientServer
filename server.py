import socket
from threading import Thread 
import os
import time

HOST = '127.0.0.1'
PORT = 2021 #command port

class Server(Thread):
    def __init__(self,comSock,address):
        Thread.__init__(self)
        self.comSock = comSock #command channel
        self.address = address

    def run(self): #override run method
        while True :
            try:
                data = self.comSock.recv(2048).decode('utf-8')
                print('recieved data:',data)
            except socket.error as e:
                print(f'{e} recieved.')

            #TODO: call the command based on data
        
    def open_data_sock(self):
        self.dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dataSock, self.address = self.serverSock.accept()
        
    def close_data_sock(self):
        self.dataSock.close()
        self.serverSock.close()

    # Commands -----------
    def PASV(self):
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSock.bind((HOST, 2020)) 
        self.serverSock.listen(5)
        addr, port = self.serverSock.getsockname( )
        cmd = ('227 Entering Passive Mode (%s,%u,%u).\r\n' %
                (','.join(addr.split('.')), port>>8&0xFF, port&0xFF))
        self.comSock.send(cmd.encode('utf-8'))


def main():
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_sock.bind((HOST, PORT))
    listen_sock.listen(5)
  
    while True:
        connection,_address =listen_sock.accept()
        S = Server(connection,_address)
        S.start()


main()