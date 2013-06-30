# -*- coding:utf-8 -*-
import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = sys.argv.pop() if len(sys.argv) == 3 else '127.0.0.1'
PORT = 2000

# define a fixed-width recv_all function.
def recv_all(sock):
    data = ''
    fixed_len=16
    while len(data) < fixed_len:
        more = sock.recv(fixed_len - len(data))
        if not more:
            raise EOFError('recv error: receved %d bytes from a %d-bytes message' % fixed_len - len(data))
        data += more
    return data

if sys.argv[1:] == ['server']:
    s.bind((HOST, PORT))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.listen(1)
    while True:
        print 'Listening at:', s.getsockname()
        sock, addr = s.accept()
        print 'Accepted connection from:', addr
        data = recv_all(sock)
        print 'Receved:', repr(data), 'From:', addr
        reply = 'Got your message'
        print 'Sending:', repr(reply), 'To:', addr
        sock.sendall(reply)
        print 'Reply sent, closing socket:', addr
        sock.close()

elif sys.argv[1:] == ['client']:
    s.connect((HOST,PORT))
    print 'Socket:',s.getsockname(),'Connected to:',s.getpeername()
    data = 'Hi! How are you~'
    print 'Sending:',repr(data),'To:',s.getpeername()
    s.sendall(data)
    reply = recv_all(s)
    print 'Receved:',repr(reply),'From:',s.getpeername()
    s.close()

else:
    print >>sys.stderr, 'Usage: tcp_sixteen.py server|client'