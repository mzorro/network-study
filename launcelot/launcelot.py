import sys, socket

qa = (('What is your name?', 'My name is Sir Launcelot of Camelot.'), 
    ('What is your quest?', 'To seek the Holy Grail.'), 
    ('What is your favorite color?', 'Blue.')) 
qadict = dict(qa)

def recv_until(sock, suffix):
    message = ''
    while not message.endswith(suffix):
        data = sock.recv(4096)
        if not data:
            raise EOFError('socket closed before we saw %r' % suffix)
        message += data
    return message
