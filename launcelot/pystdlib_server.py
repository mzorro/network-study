from SocketServer import ThreadingMixIn, TCPServer, BaseRequestHandler
import launcelot, simple_server, socket
class MyHandler(BaseRequestHandler):
    def handle(self):
        simple_server.handle_client(self.request)
class MyServer(ThreadingMixIn, TCPServer):
    allow_reuse_address = 1
    # address_family = socket.AF_INET6 # if you need IPv6

server = MyServer(('', simple_server.PORT), MyHandler)
print 'Ready and listening at %r port %d ...' % (simple_server.ADDR, simple_server.PORT)
server.serve_forever()