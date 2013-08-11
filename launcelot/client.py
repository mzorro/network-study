import socket, sys, launcelot

def client(hostname, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, port))
    for i in range(20):
        question,answer = launcelot.qa[i % len(launcelot.qa)]
        sock.sendall(question)
        reply = launcelot.recv_until(sock, '.') # answers end with '.'
        yield reply==answer
        if __name__== '__main__':
            print answer
    sock.close()

if __name__ == '__main__':
    if not 2 <= len(sys.argv) <= 3:
        print >>sys.stderr, 'usage: client.py hostname [port]'
        sys.exit(2)
    port = int(sys.argv[2]) if len(sys.argv) > 2 else launcelot.PORT
    for success in client(sys.argv[1], port):
        pass