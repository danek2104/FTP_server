import os
import shutil
import socket
import threading

# Конфигурация сервера
HOST = 'localhost'
PORT = 9090
WORK_DIR = os.path.abspath('server_workspace')

# Создаем рабочую директорию, если не существует
if not os.path.exists(WORK_DIR):
    os.makedirs(WORK_DIR)

def resolve_path(path):
    """Преобразует относительный путь в абсолютный внутри WORK_DIR"""
    return os.path.abspath(os.path.join(WORK_DIR, path))

def is_safe_path(path):
    """Проверяет, находится ли путь в разрешенной директории"""
    return resolve_path(path).startswith(WORK_DIR)

def process(request):
    """Обработка команд от клиента"""
    tokens = request.split(maxsplit=2)
    if not tokens:
        return "Error: Empty command"
    
    cmd = tokens[0]
    args = tokens[1:] if len(tokens) > 1 else []

    try:
        if cmd == 'pwd':
            return WORK_DIR
        
        elif cmd == 'ls':
            return '\n'.join(os.listdir(WORK_DIR))
        
        elif cmd == 'mkdir':
            if not args:
                return "Error: Missing directory name"
            dir_path = resolve_path(args[0])
            if not is_safe_path(args[0]):
                return "Error: Invalid path"
            os.mkdir(dir_path)
            return "OK"
        
        elif cmd == 'rmdir':
            if not args:
                return "Error: Missing directory name"
            dir_path = resolve_path(args[0])
            if not is_safe_path(args[0]):
                return "Error: Invalid path"
            shutil.rmtree(dir_path)
            return "OK"
        
        elif cmd == 'rm':
            if not args:
                return "Error: Missing filename"
            file_path = resolve_path(args[0])
            if not is_safe_path(args[0]):
                return "Error: Invalid path"
            os.remove(file_path)
            return "OK"
        
        elif cmd == 'rename':
            if len(args) < 2:
                return "Error: Missing arguments (oldname newname)"
            old_path = resolve_path(args[0])
            new_path = resolve_path(args[1])
            if not (is_safe_path(args[0]) and is_safe_path(args[1])):
                return "Error: Invalid path"
            os.rename(old_path, new_path)
            return "OK"
        
        elif cmd == 'upload':
            if len(args) < 2:
                return "Error: Missing arguments (filename content)"
            file_path = resolve_path(args[0])
            if not is_safe_path(args[0]):
                return "Error: Invalid path"
            with open(file_path, 'w') as f:
                f.write(args[1])
            return "OK"
        
        elif cmd == 'download':
            if not args:
                return "Error: Missing filename"
            file_path = resolve_path(args[0])
            if not is_safe_path(args[0]):
                return "Error: Invalid path"
            if not os.path.isfile(file_path):
                return "Error: File not found"
            with open(file_path, 'r') as f:
                return f.read()
        
        elif cmd == 'cp':
            if len(args) < 2:
                return "Error: Missing arguments (source destination)"
            src = resolve_path(args[0])
            dst = resolve_path(args[1])
            if not (is_safe_path(args[0]) and is_safe_path(args[1])):
                return "Error: Invalid path"
            shutil.copyfile(src, dst)
            return "OK"
        
        elif cmd == 'exit':
            return "Goodbye!"
        
        else:
            return "Error: Unknown command"
    
    except Exception as e:
        return f"Error: {str(e)}"

def handle_client(conn):
    """Обработка подключения клиента"""
    with conn:
        data = conn.recv(4096).decode()
        if not data:
            return
        response = process(data)
        conn.sendall(response.encode())

# Запуск сервера
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server started at {HOST}:{PORT}")
    
    while True:
        conn, addr = s.accept()
        print(f"Connected: {addr}")
        client_thread = threading.Thread(target=handle_client, args=(conn,))
        client_thread.start()