#!/usr/bin/env python
from datetime import datetime
#from flask import Response
from flask import request
from flask import Flask
from flask import json
import logging as log
import xmltodict
import uuid
import sys
import os

proj_root = os.path.dirname(os.path.dirname(os.getcwd()))
#print('project root: ' + proj_root)
sys.path.append(proj_root)

#from routes import *
from core.gateway import Gateway
from utils.decorators import timeit

from lxml import etree
#import inspect
#import os

app = Flask(__name__)
#http://localhost:38181/viscus/cr/v1/payment/

# constants

GET = 'GET'
POST = 'POST'

app_xml = {'Content-Type': 'application/xml'}
text_xml = {'Content-Type': 'text/xml'}
app_json = {'Content-Type': 'application/json'}

msg_cache = {}
gw = None
txn_cntr = 0


def initialize():
	#do initialization
	pass

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


"""def validate_schema(schema_name):
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
	return decorated_function"""

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


def json_to_dict(jso):
	try:
		json_dict = json.loads(jso)
	except ValueError as e:
		raise e
	return json_dict


def dict_to_json(dic):
	try:
		dict_json = json.dumps(dic)
	except ValueError as e:
		raise e
	return dict_json


def xml_to_dict(xml):
	try:
		xml_dict = xmltodict.parse(xml)
	except Exception, e:
		raise e
	return xml_dict


def dict_to_xml(dic):
	try:
		xml = xmltodict.unparse(dic, full_document=False)
	except Exception as e:
		raise e
	return xml


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
	gw = Gateway()
	#data = {}
	#response = None

	msg_guid = get_guid()

	return msg_guid


@app.route('/viscus/cr/v1/payment', methods=[POST])
@timeit
def payment():
	gw = Gateway()
	global msg_cache
	global txn_cntr
	txn_cntr += 1
	msg = {}
	response = None

	#logging.basicConfig(filename='example.log',level=logging.INFO)
	log.basicConfig(level=log.INFO, format='%(asctime)s %(message)s')

	server_date_time = datetime.now()
	log.info('server time: ' + str(server_date_time))
	msg_guid = get_guid()
	log.info('message guid: ' + str(msg_guid))
	#ksn = request.headers.get('ksn')
	#bdk = request.headers.get('bdk-index')

	if contains_json(request):
		print('received json')
		try:
			msg = json_to_dict(request.data)
		except Exception, e:
			return (e, 400)
	elif contains_xml(request):
		print('received xml')
		try:
			msg = xml_to_dict(request.data)
		except Exception, e:
			return (e, 400)

	msg_cache[msg_guid] = msg
	print('msg_cache: ' + str(msg_cache))
	print('txn_cntr: ' + str(txn_cntr))

	try:
		gw_response = gw.do_payment(msg)
		#make sure gw_response is dict

		if contains_json(request):
			json_response = dict_to_json(gw_response)
			response = (json_response, 200, app_json)

		elif contains_xml(request):
			xml_response = dict_to_xml(gw_response)
			response = (xml_response, 200, text_xml)

	except Exception, e:
		print('caught exception ' + str(e) + ' from gateway')
		response = (e, 500)

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
			gw.load_module(route_name)
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
	try:
		parser = etree.XMLParser()
		etree.fromstring(data, parser)
		return True
	except etree.XMLSyntaxError:
		#log.warning('invalid xml - ' + str(e))
		print('invalid xml - ')
		return False

if __name__ == '__main__':
	initialize()
	app.run(debug=True)
