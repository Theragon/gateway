import imp
import os


def path_to_routes():
	return os.path.dirname(os.path.dirname(os.getcwd()))+'/routes'


def load_module(module):
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


def do_payment(route_name, data):
	acq_msg = None

	route = load_module(route_name)
	parser = route.Parser()
	try:
		acq_msg = parser.parse(data)
		print('acq_msg: ' + acq_msg)
	except Exception, e:
		print('could not parse request - ' + str(e))
		raise e
	#client = route.Client()
	route1 = route.Route()
	response = route1.do_payment(acq_msg)
	print('do_payment returning ' + str(response))
	return response


def do_refund(route_name, data):
	#route = loaded(route_name)
	pass


def do_void(route_name, data):
	pass


def do_authorization(route_name, data):
	pass


def do_completion(route_name, data):
	pass
