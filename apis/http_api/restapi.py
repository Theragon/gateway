#!/usr/bin/env python
from xml.parsers.expat import ExpatError
from datetime import datetime
#from flask import Response
from flask import request
from flask import Flask
from flask import json
import logging as log
import xmltodict
#import redis
import uuid
import time
import sys
import os

proj_root = os.path.dirname(os.path.dirname(os.getcwd()))
print('project root: ' + proj_root)
sys.path.append(proj_root)

#from routes import *

from utils.decorators import timeit
import utils.dbutils as db
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

ps = db.red.pubsub(ignore_subscribe_messages=True)
ps.subscribe(rsp_sub_id)

debug = True
encryption = False if debug else True

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

def now():
	return time.time()


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
	if encryption:
		log.info('encryption is enabled')
		log.warn('THIS FEATURE IS NOT YET IMPLEMENTED')
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

	msg[txn_type]['status'] = 'received'

	try:
		db.add_to_queue('incoming', msg)
	except Exception as e:
		# Some serious database error needs to be handled
		raise e

	try:
		print('waiting for response for guid ' + msg_guid)
		core_rsp = db.wait_for_rsp(msg_guid)
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
		print('waiting for response from core')
		core_rsp = do_transaction(msg)
		print('core_rsp: ' + json.dumps(core_rsp))
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

	config_id = get_config_id(config)

	# move this to a wrapper function
	db.delete(config_id)

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


def exists(key):
	value = db.get_value(key)
	return value is not None


def terminal_config_exists(config):
	config_id = get_config_id(config)
	log.info('checking if config ' + config_id + ' exists')
	return exists(config_id)


def save_terminal_config(config):
	config_id = get_config_id(config)
	log.info('saving terminal config ' + config_id)
	db.save(config_id, config)


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
