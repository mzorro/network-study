import time, launcelot
from threading import Thread
from simple_server import setup_server
from simple_server import handle_client
def make_thread(client_sock):
    thread = Thread(target=handle_client, args=(client_sock,))
    thread.daemon = True
    thread.start()
    return thread

listen_sock = setup_server()

while True:
    client_sock, sockname = listen_sock.accept()
    make_thread(client_sock)