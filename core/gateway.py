from collections import OrderedDict

import pprint
import imp
import os

from exceptions import *

IREQ = 'IREQ'
IRES = 'IRES'
OREQ = 'OREQ'
ORES = 'ORES'


def path_to_routes():
	#return os.path.dirname(os.path.dirname(os.getcwd()))+'/routes'
	return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/routes'


class Gateway(object):
	"""docstring for Gateway"""
	msg_cache = {}

	def __init__(self, arg=None):
		super(Gateway, self).__init__()
		self.arg = arg

	def verify_type(self, msg):
		if type(msg) is not dict and type(msg) is not OrderedDict:
			raise TypeError('Message must be dictionary')

	def get_route_name(self, msg):
		try:
			if 'route' in msg:
				print('message contains route')
			route_name = msg['payment']['route'].lower()
		except KeyError, e:
			raise e
		return route_name

	def load_module(self, module):
		path = path_to_routes()
		print('path to routes: ' + path)
		try:
			print('module: ' + module)
			m = imp.find_module(module, [path])
			print('module found: ' + str(m))
			route = imp.load_module(module, m[0], m[1], ('', '', 5))
			print('route successfully loaded')
		except ImportError, e:
			raise e
		return route

	def add_to_msg_cache(self, direction, msg):
		self.msg_cache[direction] = msg
		print('message added to msg_cache')
		pprint.pprint(self.msg_cache)

	def do_payment(self, msg):
		response = None
		acq_msg = None

		try:
			#verify that message is a dictionary
			self.verify_type(msg)

			#get the route name to load from message
			route_name = self.get_route_name(msg)

			#load the module
			route = self.load_module(route_name)

			#instantiate the route parser
			parser = route.Parser()

			#make sure the message is parsable
			#get the message so that it can be stored
			acq_msg = parser.parse_payment(msg)
			print('acq_msg: ' + acq_msg)

		except (TypeError, ParseException, ImportError) as e:
			raise e

		try:
			#instantiate the route
			route1 = route.Route()

			self.add_to_msg_cache(IREQ, msg)
			self.add_to_msg_cache(OREQ, acq_msg)

			#do the payment and get the response back
			print('performing payment')
			response = route1.do_payment(acq_msg)

			#todo: make sure response is a dict
			self.add_to_msg_cache(IRES, response)

			#todo: create outgoing response (ORES)

		except Exception as e:
			raise e

		print('do_payment returning ' + str(response))
		return response

	def do_refund(self, msg):
		#route = loaded(route_name)
		pass

	def do_void(self, msg):
		pass

	def do_authorization(self, msg):
		pass

	def do_completion(self, msg):
		pass

	def do_cancellation(self, msg):
		pass
