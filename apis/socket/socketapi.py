from twisted.internet import ssl, protocol, reactor
from twisted.python import log
import inspect
import os

proj_path = os.path.dirname(
	os.path.abspath(inspect.getfile(inspect.currentframe())))
log.startLogging(open(proj_path+'/server.log', 'w'), setStdout=False)


def sanitize_msg(msg):
	return msg.replace(' ', '').replace('\t', '').replace('\n', '')


class SocketProtocol(protocol.Protocol):

	def connectionMade(self):
		log.msg('client connected')

	def dataReceived(self, client_msg):
		log.msg('dataReceived')

		self.factory.msg_received(client_msg)

		def on_error(failure):
			log.msg('Error handler caught exception')
			failure.trap(Exception)
			return 'Internal server error'

		def writeResponse(response):
			resp_sanitized = sanitize_msg(response)
			log.msg('writing response: ' + str(resp_sanitized))
			if resp_sanitized != 'timeout':
				self.transport.write(resp_sanitized)
			# self.transport.loseConnection()


class SocketFactory(protocol.ServerFactory):
	protocol = SocketProtocol

	def msg_received(self):
		log.msg('validate xml')
		log.msg('validate json')


"""reactor.listenSSL(
	15005,
	SocketFactory(),
	ssl.DefaultOpenSSLContextFactory(
		proj_path+'/keys/server.key',
		proj_path+'/keys/server.crt')
	)

reactor.run()"""
