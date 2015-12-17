#!/usr/bin/env python
#import utils.decorators as dec
from xml.parsers.expat import ExpatError
from datetime import datetime
#from flask import Response
from flask import request
from flask import Flask
from flask import json
import logging as log
import xmltodict
import redis
import uuid
import time
import sys
import os

proj_root = os.path.dirname(os.path.dirname(os.getcwd()))
print('project root: ' + proj_root)
sys.path.append(proj_root)

#from routes import *

from utils.decorators import timeit
#from core.gateway import Gateway

app = Flask(__name__)
#http://localhost:38181/viscus/cr/v1/payment/

# constants

GET = 'GET'
POST = 'POST'
DELETE = 'DELETE'

app_xml = {'Content-Type': 'application/xml'}
text_xml = {'Content-Type': 'text/xml'}
app_json = {'Content-Type': 'application/json'}

msg_cache = {}
gw = None
txn_cntr = 0

req_sub_id = 'requests'
rsp_sub_id = 'responses'
pub_sub_host = 'localhost'
pub_sub_port = 6379
pub_sub_db = 0

red = redis.StrictRedis(
	host=pub_sub_host,
	port=pub_sub_port,
	db=pub_sub_db
)

ps = red.pubsub(ignore_subscribe_messages=True)
ps.subscribe(rsp_sub_id)

debug = True

#logging.basicConfig(filename='example.log',level=logging.INFO)
log.basicConfig(level=log.INFO, format='%(asctime)s %(message)s')


def initialize():
	#do initialization
	pass


##################
# error handlers #
##################


@app.errorhandler(404)
def page_not_found(error):
	return 'This page does not exist', 404


@app.errorhandler(500)
def internal_error(error):
	return 'Internal server error', 500


@app.errorhandler(405)
def not_allowed(error):
	return 'Method not allowed', 405


##############
# Exceptions #
##############


class GatewayTimeoutException(Exception):
	"""docstring for GatewayTimeoutException"""
	def __init__(self, message):
		super(GatewayTimeoutException, self).__init__(message)
		#self.message = message
		self.status = 504


class InternalServerError(Exception):
	"""docstring for InternalServerError"""
	def __init__(self, message):
		super(InternalServerError, self).__init__(message)
		#self.message = message
		self.status = 500


class BadRequestException(Exception):
	"""docstring for BadRequestException"""
	def __init__(self, message):
		super(BadRequestException, self).__init__(message)
		#self.arg = arg
		self.status = 400


###################
# parsing methods #
###################


def convert_to_dict(request):
	log.info('converting to dict')
	msg = None
	if contains_json(request):
		try:
			msg = json_to_dict(request.data)
		except ValueError:
			log.info('ValueError')
			raise BadRequestException('Malformed json')
			#return ('Malformed json', 400)
	elif contains_xml(request):
		try:
			msg = xml_to_dict(request.data)
		except ExpatError:
			log.info('ExpatError')
			raise BadRequestException('Malformed xml')
			#return ('Malformed xml', 400)
	return msg


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
	except ExpatError as e:
		raise e
	return xml_dict


def dict_to_xml(dic):
	try:
		xml = xmltodict.unparse(dic, full_document=False)
	except Exception as e:
		raise e
	return xml


###################
# utility methods #
###################


def add_to_queue(key, value):
	print('adding message ' + json.dumps(value) + ' to queue ' + str(key))
	try:
		red.rpush(key, json.dumps(value))
	except Exception as e:
		raise e


def listen(msg):
	while True:
		m = red.get_message()
	return m


def now():
	return time.time()


def get_value(key):
	return red.get(key)


# All redis wrapper functions should be moved to a separate module
def save(key, value):
	result = red.set(key, value)
	log.info('result: ' + str(result))


def wait_for_rsp2(guid, timeout=None):
	print('waiting for guid ' + str(guid))
	rsp = None
	start = now()
	while rsp is None:
		rsp = get_value(guid)
		diff = now() - start
		if timeout and diff > timeout:
			raise GatewayTimeoutException('Operation timed out')

	red.delete(guid)
	return json.loads(rsp)


def wait_for_rsp(guid, timeout=0):
	rsp = red.blpop(guid, timeout=timeout)
	return json.loads(rsp[1])


def create_http_rsp(core_rsp, http_req):
	if contains_xml(http_req):
		try:
			xml_response = dict_to_xml(core_rsp)
			http_rsp = (xml_response, 200, app_xml)
		except Exception:
			log.info('Error converting core response to xml')
			raise InternalServerError('Internal server error')

	elif contains_json(http_req):
		try:
			json_response = dict_to_json(core_rsp)
			http_rsp = (json_response, 200, app_json)
		except Exception:
			log.info('Error converting core response to json')
			raise InternalServerError('Internal server error')

	return http_rsp

###############
# http routes #
###############


@app.route('/viscus/cr/v1/refund', methods=[POST])
def refund():
	try:
		msg = convert_to_dict(request)
	except BadRequestException as e:
		return (e.message, e.status)

	try:
		core_rsp = do_transaction(msg)
	except GatewayTimeoutException as e:
		return (e.message, e.status)

	try:
		http_rsp = create_http_rsp(core_rsp, request)
	except InternalServerError as e:
		return (e.message, e.status)

	print('returning ' + str(http_rsp))
	return http_rsp


@app.route('/viscus/cr/v1/payment', methods=[POST])
def payment():
	try:
		msg = convert_to_dict(request)
	except BadRequestException as e:
		return (e.message, e.status)

	try:
		core_rsp = do_transaction(msg)
	except GatewayTimeoutException as e:
		return (e.message, e.status)

	try:
		http_rsp = create_http_rsp(core_rsp, request)
	except InternalServerError as e:
		return (e.message, e.status)

	print('returning ' + str(http_rsp))
	return http_rsp


@timeit
def do_transaction(msg):
	server_date_time = datetime.now()
	log.info('server time: ' + str(server_date_time))
	msg_guid = str(get_guid())
	log.info('message guid: ' + str(msg_guid))

	txn_type = msg.iterkeys().next()
	msg[txn_type]['guid'] = msg_guid
	log.info('type: ' + txn_type)

	try:
		add_to_queue('incoming', msg)
	except Exception as e:
		# Some serious database error needs to be handled
		raise e

	try:
		core_rsp = wait_for_rsp(msg_guid)
	except GatewayTimeoutException as e:
		raise e

	return core_rsp


@app.route('/viscus/cr/v1/transaction', methods=[POST])
def transaction():
	try:
		msg = convert_to_dict(request)
	except BadRequestException as e:
		return (e.message, e.status)

	try:
		core_rsp = do_transaction(msg)
	except GatewayTimeoutException as e:
		return (e.message, e.status)

	try:
		http_rsp = create_http_rsp(core_rsp, request)
	except InternalServerError as e:
		return (e.message, e.status)

	print('returning ' + str(http_rsp))
	return http_rsp


# this method should later be moved to separate module
@app.route('/viscus/data/v1/terminalconfig', methods=[POST])
def post_terminal_config():
	try:
		config = convert_to_dict(request)
	except BadRequestException as e:
		return (e.message, e.status)

	if terminal_config_exists(config):
		return ('Data already exists', 409)

	try:
		save_terminal_config(config)
	except Exception, e:
		return (e.message, e.status)

	return ('Created', 201)


# this method should later be moved to separate module
@app.route('/viscus/data/v1/terminalconfig', methods=[DELETE])
def delete_terminal_config():
	try:
		config = convert_to_dict(request)
	except BadRequestException as e:
		return (e.message, e.status)

	# move this to a wrapper function
	red.delete(config['serialNumber'])

	return ('No content', 204)


@app.route('/viscus/routestatus/<route>')
def route_status(route):
	try:
		sys.modules[route]
		return 'available'
	except KeyError:
		return 'not available'


#####################
# more util methods #
#####################


"""def module_exists(module, path):
	try:
		imp.find_module(module, [path])
		found = True
	except ImportError:
		found = False
	return found"""


def exists(key):
	value = get_value(key)
	return value is not None


def terminal_config_exists(config):
	config_id = get_config_id(config)
	log.info('checking if config ' + config_id + ' exists')
	return exists(config_id)


def save_terminal_config(config):
	config_id = get_config_id(config)
	log.info('saving terminal config ' + config_id)
	save(config_id, config)


def get_config_id(config):
	device_type = config.get('terminalType')
	serial_number = config.get('serialNumber', None)
	return device_type + serial_number


def get_guid():
	return uuid.uuid4()


def contains_json(request):
	return request.headers['Content-Type'] == 'application/json'


def contains_xml(request):
	return request.headers['Content-Type'] == 'text/xml' \
		or request.headers['Content-Type'] == 'application/xml'


if __name__ == '__main__':
	initialize()
	app.run(debug=debug, processes=4)
