import imp
import os


def path_to_routes():
	#return os.path.dirname(os.path.dirname(os.getcwd()))+'/routes'
	return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/routes'


class Gateway(object):
	"""docstring for Gateway"""
	msg_cache = {}

	def __init__(self, arg=None):
		super(Gateway, self).__init__()
		self.arg = arg

	def load_module(self, module):
		path = path_to_routes()
		print('path to routes: ' + path)
		try:
			print('module: ' + module)
			m = imp.find_module(module, [path])
			print('module found: ' + str(m))
			route = imp.load_module(
				module,
				m[0],
				m[1],
				('', '', 5))
			print('route successfully loaded')
			return route
		except ImportError, e:
			raise e

	def do_payment(self, route_name, data):
		acq_msg = None

		try:
			route = self.load_module(route_name)
			#pull information from TMS
			parser = route.Parser()
			acq_msg = parser.parse(data)
			print('acq_msg: ' + acq_msg)
			#client = route.Client()
			route1 = route.Route()
			response = route1.do_payment(acq_msg)
		except Exception, e:
			print('could not parse request - ' + str(e))
			raise e

		print('do_payment returning ' + str(response))
		return response

	def do_refund(self, route_name, data):
		#route = loaded(route_name)
		pass

	def do_void(self, route_name, data):
		pass

	def do_authorization(self, route_name, data):
		pass

	def do_completion(self, route_name, data):
		pass

	def do_cancellation(self, route_name, data):
		pass
