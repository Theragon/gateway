from config import *
from baseclasses import RouteParser
print('evo client is being imported')


class Parser(RouteParser):
	pass


class Route():
	def __init__(self):
		self.client = Client()

	def do_payment(self, msg):
		print('payment logic')
		self.client.exchange_msg(msg)


class Client():
	def __init__(self, host=host, port=port, timeout=5):
		pass

	def exchange_msg(self, request):
		return 'exchanging msg'

	def validate(self, msg):
		return True


def get_client():
	return Client()
