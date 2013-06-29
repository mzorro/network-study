import select
import socket
import Queue

# create a non-blocking socket
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.setblocking(0)

server_addr = ('',2000)
server.bind(server_addr)

server.listen(10)

# sockets from which we except to read
inputs = [server]

# sockets to which we except to write
outputs = []

# exceptional conditions
exceptions = []

# seconds before timeout
timeout = 10

# those are the receved messages
# (every socket is corresponded to a Queue)
messages = {}

while inputs:
    print 'waiting for next event...'
    read_list,write_list,exception_list = select.select(inputs,outputs,exceptions,timeout)

    if not (read_list or write_list or exception_list):
        print 'Time out!!!'
        break
    for s in read_list:# to do accept() or recv() operation
        if s is server:
            # server is ready to accept a connection
            clientsock, clientaddr = s.accept()
            print 'Accepted connection from',clientaddr
            clientsock.setblocking(0)
            # we except to read from this client socket
            inputs.append(clientsock)
            # create a Queue for this client socket
            messages[clientsock] = Queue.Queue()
        else:
            # means we can read data from this client socket
            data = s.recv(1024)
            if data:
                # we successfully read data
                print 'receved:',data,' from:',s.getpeername()
                messages[s].put(data)
                # add a output channel for response
                if s not in outputs:
                    outputs.append(s)

            else:
                # we get empty result, close the connection
                print 'Closing connection with',s.getpeername()
                # we should not response to is anymore
                if s in outputs:
                    outputs.remove(s)
                # we should not expect to read from it anymore
                inputs.remove(s)
                # close the connection
                s.close()
                # remove it's message queue
                del messages[s]

    for s in write_list:# to do send() operation
        # means we should write(response) to this client socket
        # note: we don't need to write to the server scoket
        try:
            next_msg = messages[s].get_nowait()
        except Queue.Empty:
            print s.getpeername(),':queue empty!'
            outputs.remove(s)
        else:
            # if not excption occured
            next_msg = next_msg.upper()
            print 'Sending:',next_msg,' to:',s.getpeername()
            s.send(next_msg)

    for s in exception_list:
        print 'Exception condition from:',s.getpeername()
        # stop listening from the connection
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()
        # remove it's message queue
        del messages[s]
