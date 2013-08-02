from twisted.internet.protocol import Protocol, ServerFactory
from twisted.internet import reactor
import launcelot

PORT = 1060

class Launcelot(Protocol):
    def connectionMade(self):
        self.question = ''

    def dataReceived(self, data):
        self.question += data
        if self.question.endswith('?'):
            self.transport.write(launcelot.qadict[self.question])
            self.question = ''

factory = ServerFactory()
factory.protocol = Launcelot
reactor.listenTCP(1060, factory)
print 'Ready and listening at %r port %d ...' % ('', PORT)
reactor.run()