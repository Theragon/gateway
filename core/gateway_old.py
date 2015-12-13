from collections import OrderedDict

import multiprocessing as mp
import pprint
import redis
import json
import imp
import os

from time import time


def timeit(method):
	def timed(*args, **kw):
		print('STARTING TIMER')
		start = time()
		result = method(*args, **kw)
		end = time()
		delta = end - start

		if delta >= 1:
			print('%s function took %0.3f s' % (method.__name__, delta))
		else:
			print('%s function took %0.3f ms' % (method.__name__, (delta)*1000.0))
		return result
	return timed


class ParseException(Exception):
	pass


IREQ = 'IREQ'
IRES = 'IRES'
OREQ = 'OREQ'
ORES = 'ORES'

MAX_PROCS = mp.cpu_count()


def path_to_routes():
	#return os.path.dirname(os.path.dirname(os.getcwd()))+'/routes'
	return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/routes'


class Gateway(mp.Process):
	"""docstring for Gateway"""
	msg_cache = {}
	red = redis.StrictRedis(host='localhost', port=6379, db=0)
	ps = red.pubsub()
	# MAX_PROCS variable should be set in config
	pool = mp.Pool(MAX_PROCS)
	# target variable should also be set in config
	target = None
	# callback function is None unless otherwise specified
	cb_func = None

	def __init__(self, msg=None):
		super(Gateway, self).__init__()
		self.msg = msg
		self.target = process_msg

	def call(self, *args, **kwargs):
		self.pool.apply_async(self.target, args, kwargs, self.cb_func)

	# This function should not be needed
	def wait(self):
		self.pool.close()
		self.pool.join()

	def run(self):
		self.process_msg(self.msg)

	def process_msg(self, msg):
		print('Gateway processing message')
		print(msg)
		txn_type = msg.iterkeys().next()
		print('type: ' + txn_type)

		if txn_type == 'payment':
			self.do_payment(msg)

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
		txn_type = msg.iterkeys().next()

		try:
			route = msg.get(txn_type).get('route')
		except KeyError as e:
			# Invalid message, missing route field
			raise e

		queue_name = route + ':OREQ'
		self.red.rpush(queue_name, msg)
		print('message put to queue ' + queue_name)

	@timeit
	def do_payment2(self, msg):
		response = None
		#acq_msg = None
		print('Gateway doing payment')

		try:
			#verify that message is a dictionary
			self.verify_type(msg)

			#get the route name to load from message
			route_name = self.get_route_name(msg)

			#load the module
			route = self.load_module(route_name)

			#instantiate the route parser
			#parser = route.Parser()

			#make sure the message is parsable
			#get the message so that it can be stored
			#acq_msg = parser.parse_payment(msg)
			#print('acq_msg: ' + acq_msg)

		except (TypeError, ParseException, ImportError) as e:
			raise e

		try:
			#instantiate the route
			route1 = route.Route()

			self.add_to_msg_cache(IREQ, msg)
			#self.add_to_msg_cache(OREQ, acq_msg)

			#do the payment and get the response back
			print('performing payment')
			response, request = route1.do_payment(msg)

			#todo: make sure response is a dict
			self.add_to_msg_cache(IRES, response)
			self.add_to_msg_cache(OREQ, request)

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


def process_msg(msg):
	gw = Gateway()
	txn_type = msg['type']

	if txn_type == 'payment':
		try:
			response = gw.do_payment(msg)
			assert response is not None
			# TODO: send response back
		except Exception as e:
			# TODO: define how error is handled
			raise e



def dispatch(msg):
	data = json.loads(msg['data'])
	p = mp.Process(target=process_msg, args=(data,))
	p.start()


def main():
	#from dispatcher import Dispatcher
	#d = Dispatcher()
	pass

if __name__ == '__main__':
	main()
