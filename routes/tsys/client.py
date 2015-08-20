from baseclasses import RouteClient
from tsysconstants import *
from config import *
from socket import *
from ssl import *


class Client(RouteClient):
	#def __init__(self, host=host, port=port, timeout=5, debug=False):
	def __init__(self, host=host, port=port, **kwargs):
		self.ready = False
		self.host = host
		self.port = port

		self.timeout = kwargs.get('timeout', 5)
		print('tsys timeout: ' + str(self.timeout))
		self.debug = kwargs.get('debug', False)
		print('tsys debug: ' + str(self.debug))
		#self.timeout = timeout
		#self.debug = debug

		self.prot = PROTOCOL_TLSv1
		self.cert = CERT_NONE

		self.sock = self.create_socket()
		self.sock.settimeout(self.timeout)
		self.connect_to_host(self.sock)

		while not self.ready:
			self.ready = self.receive_enq()

	def create_socket(self):
		# print('creating socket')
		sock = socket(AF_INET, SOCK_STREAM)
		tls_socket = wrap_socket(sock, ssl_version=self.prot, cert_reqs=self.cert)

		return tls_socket

	def connect_to_host(self, sock):
		sock.connect((self.host, self.port))

	def receive(self):
		try:
			response = self.sock.recv(1024)
			return response.decode()
		except SSLError:
			raise SSLError

	def send(self, msg):
		msg_encoded = msg.encode()
		self.sock.send(msg_encoded)

	def receive_enq(self):
		return self.receive() == '\x05'

	def exchange_msg(self, request):
		if self.debug:
			return SALE_APPROVED_RSP
		self.send(request)
		try:
			response = self.receive()
			return response
		except SSLError:
			raise SSLError

	def close_connection(self):
		self.sock.shutdown(SHUT_RDWR)
		self.sock.close()
		# print('socket closed')

	"""def __del__(self):
		try:
			self.close_connection()
		except socket.error:
			pass"""

	def validate(self, msg):
		return True


def main2():
	host = sys.argv[1]
	to_send = int(sys.argv[2])

	client = TsysClient(host)

	all_msgs = get_all_messages()

	if client.ready:
		print('client is ready')
		resp = client.exchange_msg(all_msgs[to_send])
		if resp:
			print('response: ' + resp)
		client.close_connection()


def get_client():
	return Client()


#if __name__ == '__main__':
	#main2()
