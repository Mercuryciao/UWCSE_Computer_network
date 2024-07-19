import socket
from _thread import *
import sys
import select

BUFFER_SIZE = 1024
def modify_request_headers(request):
    lines = request.split('\n')
    lines[0] = lines[0].replace("HTTP/1.1", "HTTP/1.0")
    headers = []
    for line in lines[1:]:
        # print('line:', line)
        if 'connection:' in line.lower():
            continue
        elif 'proxy-connection:'in line.lower():
            continue
        else:
            headers.append(line)
    headers.append('Connection: close')
    headers.append('Proxy-Connection: close')

    modified_request = '\r\n'.join([lines[0]] + headers)
    return modified_request+'\r\n'

def parse_address(request):
    request_lines = request.split('\n')
    first_line = request_lines[0]
    host = ""
    first_line_element = first_line.split(' ')
    
    if ('443' or 'https://') in first_line_element[1].lower():
        port = 443
    else:
        port = 80
    for line in request_lines[1:]:
        if 'host:' in line.lower():
            line_element = line.split(':')
            host = line_element[1].strip()
    return host, port

def handle_connect(client_socket, request):
    host, port = parse_address(request)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # print(host, port)
        server_socket.connect((host, port))
        client_socket.send(b"HTTP 200 OK\r\n\r\n")
        # print('ok')
    except:
        client_socket.send(b"HTTP 502 Bad Gateway\r\n\r\n")
        print('bad')
        client_socket.close()
        server_socket.close()
        return

    sockets = [client_socket, server_socket]
    while True:
        ready_sockets, _, _ = select.select(sockets, [], sockets)
        if not ready_sockets:
            break
        for s in ready_sockets:
            
            data = s.recv(BUFFER_SIZE)
            if not data:
                return
            if s is client_socket:
                server_socket.send(data)
            else:
                client_socket.send(data)

    client_socket.close()
    server_socket.close()

def handle_non_connect(client_socket, request):
    host, port = parse_address(request)
    # print('request: ', request)
    if host is None or not request:
        client_socket.close()
        return

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((host, port))
    modified_request = modify_request_headers(request)
    # print('modified_request: ', modified_request)
    server_socket.send(modified_request.encode('ISO-8859-1'))
    
    sockets = [client_socket, server_socket]
    while True:
        ready_sockets, _, _ = select.select(sockets, [], sockets)
        if not ready_sockets:
            break
        for s in ready_sockets:
            data = s.recv(BUFFER_SIZE)
            if not data:
                return
            if s is client_socket:
                server_socket.send(data)
            else:
                client_socket.send(data)

def handle_client(client_socket):
    try:
        request = client_socket.recv(BUFFER_SIZE).decode('ISO-8859-1')

        first_line = request.split('\n')[0]
        if not first_line:
            return

        print(f">>> {first_line.strip()}")

        if "connect" in first_line[:7].lower():
            handle_connect(client_socket, request)
        else:
            handle_non_connect(client_socket, request)
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

def main():
    port = int(sys.argv[1])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(10)

    while True:
        client_socket, addr = server_socket.accept()
        start_new_thread(handle_client, (client_socket, ))

if __name__ == '__main__':
    main()