#!/usr/bin/env python
from datetime import datetime
from flask import Flask
from flask import request
from flask import json
import logging as log
import xmltodict
import uuid
import sys
import os

proj_root = os.path.dirname(os.path.dirname(os.getcwd()))
print('project root: ' + proj_root)
sys.path.append(proj_root)

from routes import *
from core import gateway

from lxml import etree
#import inspect
#import os

app = Flask(__name__)
#http://localhost:38181/viscus/cr/v1/payment/

# constants

GET = 'GET'
POST = 'POST'

msg_cache = {}

# decorators


"""def validate_json(f):
	@wraps(f)
	def wrapper(*args, **kw):
		try:
			request.json
		except BadRequest:
			msg = "payload must be a valid json"
			return jsonify({"error": msg}), 400
		return f(*args, **kw)
	return wrapper"""


def validate_schema(schema_name):
	def decorator(f):
		@wraps(f)
		def wrapper(*args, **kw):
			try:
				validate(request.json, current_app.config[schema_name])
			except ValidationError, e:
				return jsonify({"error": e.message}), 400
			return f(*args, **kw)
		return wrapper
	return decorator


def returns_xml(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		r = f(*args, **kwargs)
		return Response(r, content_type='text/xml; charset=utf-8')
	return decorated_function


def returns_json(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		r = f(*args, **kwargs)
		return Response(r, content_type='application/json; charset=utf-8')
	return decorated_function

# error handlers


@app.errorhandler(404)
def page_not_found(error):
	return 'This page does not exist', 404


@app.errorhandler(500)
def internal_error(error):
	return 'Internal server error', 500


@app.errorhandler(405)
def not_allowed(error):
	return 'Method not allowed', 405

# routes


"""def get_path():
	proj_path = os.path.dirname(
			os.path.abspath(inspect.getfile(inspect.currentframe())))
	print('proj_path: ' + proj_path)
	return proj_path"""


"""def path_to_routes():
	return os.getcwd()+'/routes'"""


"""def load_module(module):
	#path = get_path()
	try:
		print('module: ' + module)
		m = imp.find_module(module, [path_to_routes()])
		print('module found: ' + str(m))
		route = imp.load_module(
			module,
			m[0],
			m[1],
			('', '', 5))
		print('route successfully loaded')
		return route
	except ImportError, e:
		raise e"""


@app.route('/viscus/cr/v1/refund', methods=[POST])
def refund():
	data = {}
	response = None

	msg_guid = get_guid()

	return msg_guid


@app.route('/viscus/cr/v1/payment', methods=[POST])
def payment():
	data = {}
	response = None

	#logging.basicConfig(filename='example.log',level=logging.INFO)
	log.basicConfig(level=log.INFO, format='%(asctime)s %(message)s')

	server_date_time = datetime.now()
	log.info('server time: ' + str(server_date_time))
	message_guid = uuid.uuid4()
	log.info('message guid: ' + str(message_guid))
	#ksn = request.headers.get('ksn')
	#bdk = request.headers.get('bdk-index')

	if contains_json(request):
		log.info('received json')
		print('received json')
		data = json.loads(request.data)
		print('json data: ' + str(data))
		route_name = data['payment']['route'].lower()
		print('route_name: ' + route_name)

		response = (gateway.do_payment(route_name, data), 200)

	if contains_xml(request):
		log.info('received xml')
		if validate_xml(request.data):
			print('xml is valid')
			data = xmltodict.parse(request.data)
			print('data: ' + str(data))
			route_name = data['payment']['route'].lower()

			#do core stuff
			#make_response(render_template('error.html'), 404)
			response = (gateway.do_payment(route_name, data), 200)

			#todo: validate response

		else:
			print('xml invalid')
			response = ('invalid xml', 400)

	print('returning ' + str(response))
	return response


@app.route('/viscus/routestatus/<route>')
def route_status(route):
	try:
		sys.modules[route]
		return 'available'
	except KeyError:
		return 'not available'


@app.route('/viscus/loadroute/<route_name>', methods=[GET])
def index(route_name):
	#print('card_acceptor: ' + card_acceptor)
	print('route: ' + route_name)
	result = None
	#route = None

	if result is None:
		print('result == None')
		try:
			gateway.load_module(route_name)
			result = 'route ' + route_name + ' successfully loaded'
		except ImportError:
			result = 'route ' + route_name + ' not found'

	return (result, 200)

# utility methods


"""def module_exists(module, path):
	try:
		imp.find_module(module, [path])
		found = True
	except ImportError:
		found = False
	return found"""


def get_guid():
	return uuid.uuid4()


def contains_json(request):
	return request.headers['Content-Type'] == 'application/json'


def contains_xml(request):
	return request.headers['Content-Type'] == 'text/xml' \
		or request.headers['Content-Type'] == 'application/xml'


def validate_json(data):
	try:
		json.loads(data)
		return True
	except ValueError:
		return False


def validate_xml(data):
	print('xml: ' + data)
	#xsd = None
	"""with open("paymentrequest.xsd", "r") as f:
		xsd = f.read()"""
	try:
		#schema_root = etree.XML(xsd)
		#schema = etree.XMLSchema(schema_root)
		#parser = etree.XMLParser(schema=schema)
		parser = etree.XMLParser()
		etree.fromstring(data, parser)
		return True
	except etree.XMLSyntaxError:
		#log.warning('invalid xml - ' + str(e))
		print('invalid xml - ')
		return False

if __name__ == '__main__':
	app.run(debug=True)
