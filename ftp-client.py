import socket

HOST = 'localhost'
PORT = 9090

while True:
    cmd = input("ftp> ")
    if not cmd:
        continue
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(cmd.encode())
        response = s.recv(4096).decode()
        print(response)
    
    if cmd.strip() == 'exit':
        break