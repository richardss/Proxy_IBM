from twisted.internet import reactor, protocol, threads
from twisted.web.client import Agent
from twisted.web.http_headers import Headers

class ProxyProtocol(protocol.Protocol):
    def __init__(self, agent):
        self.agent = agent
        self.buffer = []

    def connectionMade(self):
        self.buffer = []

    def dataReceived(self, data):
        self.buffer.append(data)
        self.forwardData()

    def forwardData(self):
        content = b''.join(self.buffer)
        d = threads.deferToThread(
            self.agent.request,
            b"POST",
            b"WEBHOOK_URL",
            Headers({"Content-Type": ["application/json"]}),
            content
        )
        d.addCallback(lambda _: self.transport.write(content))

class ProxyFactory(protocol.Factory):
    def __init__(self, agent):
        self.agent = agent

    def buildProtocol(self, addr):
        return ProxyProtocol(self.agent)

# Create an instance of the Agent to make HTTP requests
agent = Agent(reactor)

# Create the proxy factory instance
proxyFactory = ProxyFactory(agent)

# Start the proxy on localhost, port 5529
reactor.listenTCP(5529, proxyFactory)

# Start the Twisted reactor
reactor.run()
