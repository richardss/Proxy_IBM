from twisted.internet import reactor, protocol, threads
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
import threading

class ProxyProtocol(protocol.Protocol):
    def __init__(self, agent):
        self.agent = agent

    def connectionMade(self):
        self.buffer = []

    def dataReceived(self, data):
        self.buffer.append(data)
        self.forwardData(data)

    def forwardData(self, data):
        d = threads.deferToThread(
            agent.request,
            b"POST",
            b"WEBHOOK_URL",
            Headers({"Content-Type": ["application/json"]}),
            b''.join(self.buffer)
        )
        d.addCallback(lambda _: self.transport.write(data))

class ProxyFactory(protocol.Factory):
    def __init__(self, agent):
        self.agent = agent

    def buildProtocol(self, addr):
        return ProxyProtocol(self.agent)

# Crea l'oggetto Agent per effettuare le richieste HTTP
agent = Agent(reactor)

# Crea l'istanza del factory del proxy
proxyFactory = ProxyFactory(agent)

# Avvia il proxy su localhost, porta 5529
reactor.listenTCP(5529, proxyFactory)

# Avvia il reactor di Twisted in un thread separato
reactor_thread = threading.Thread(target=reactor.run, args=(False,))
reactor_thread.start()
