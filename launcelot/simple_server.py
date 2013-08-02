import launcelot, socket
ADDR = 'localhost'
PORT = 1060
def handle_client(client_sock):
    try:
        while True:
            question = launcelot.recv_until(client_sock, '?')
            answer = launcelot.qadict[question]
            client_sock.sendall(answer)
    except EOFError:
        client_sock.close()

def server_loop(listen_sock):
    while True:
        client_sock ,sockname = listen_sock.accept()
        handle_client(client_sock)

def setup_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ADDR, PORT))
    sock.listen(128)
    print 'Ready and listening at %r port %d ...' % (ADDR, PORT)
    return sock

if __name__ == '__main__':
    listen_sock = setup_server()
    server_loop(listen_sock)