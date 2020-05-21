import socket
import datetime


class Client:

    def __init__(self):
        with socket.create_connection(("127.0.0.1", 8888)) as sock:
            while True:
                msg = sock.recv(1024)
                if len(msg) > 0:
                    print(msg)
                    sock.send(bytes(str(datetime.datetime.now()).encode('utf8')))
                msg = []
                        
                

if __name__ == "__main__":
    Client()