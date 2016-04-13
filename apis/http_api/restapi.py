#!/usr/bin/env python

####################
# external modules #
####################

from flask_negotiate import consumes, produces
from datetime import datetime
from flask import Response
from flask import request
from flask import Flask
from flask import json
import logging as log
import ConfigParser
import uuid
import time
import sys
import os
import io

proj_root = os.path.dirname(os.path.dirname(os.getcwd()))
print('project root: ' + proj_root)
sys.path.append(proj_root)
sys.path.append('/home/logi/repos/gateway')

###################
# project modules #
###################

from utils.decorators import timeit
from utils import dbutils as db
from utils import httputils as http
from utils.parseutils import *
import utils.queueutils as q
import utils.messageutils as mu

app = Flask(__name__)

# constants

config = None

ACCEPTED_MIMETYPES = \
	[
		http.MimeType.app_xml,
		http.MimeType.text_xml,
		http.MimeType.app_json
	]

txn_cntr = 0

req_sub_id = 'requests'
rsp_sub_id = 'responses'

ps = db.red.pubsub(ignore_subscribe_messages=True)
ps.subscribe(rsp_sub_id)

debug = True
encryption = False
#encryption = False if debug else True

#logging.basicConfig(filename='example.log',level=logging.INFO)
log.basicConfig(level=log.DEBUG, format='%(asctime)s %(message)s')


def read_config():
	global debug
	global config
	global encryption
	try:
		with open(sys.argv[1]) as f:
			data = f.read()
		config = ConfigParser.RawConfigParser(allow_no_value=True)
		config.readfp(io.BytesIO(data))
		debug = config.get('basic', 'debug')
		encryption = config.get('basic', 'encryption')
		print('debug from config: ' + debug)
		print('encryption from config: ' + encryption)
	except Exception as e:
		print(e.message)
		log.warn('Failed to read config, using default values')


def initialize():
	#do initialization
	read_config()
	# if connection with disque is not established
	if not q.connect():
		# use redis as fallback
		q.switch_to_engine('redis')


##################
# error handlers #
##################


@app.errorhandler(404)
def page_not_found(error):
	nfe = http.NotFoundException()
	return (nfe.message, nfe.status)


@app.errorhandler(500)
def internal_error(error):
	return 'Internal server error', 500


@app.errorhandler(405)
def not_allowed(error):
	return 'Method not allowed', 405


###################
# parsing methods #
###################


def convert_to_dict(request):
	log.info('converting to dict')
	msg = None
	if http.contains_json(request):
		try:
			msg = json_to_dict(request.data)
		except ValueError:
			log.info('ValueError')
			raise http.BadRequestException('Malformed json')
	elif http.contains_xml(request):
		try:
			msg = xml_to_dict(request.data)
		except ExpatError:
			log.info('ExpatError')
			raise http.BadRequestException('Malformed xml')
	log.info(
		'accepted response formats:' +
		str(request.accept_mimetypes.values()))

	msg['response_format'] = request.accept_mimetypes.best

	log.info(
		'chosen response format: ' +
		str(msg.get('response_format')))
	return msg


###############
# http routes #
###############


@app.route('/viscus/cr/v1/refund', methods=[http.POST])
def refund():
	try:
		msg = convert_to_dict(request)
	except http.BadRequestException as e:
		return (e.message, e.status)

	try:
		core_rsp = do_transaction(msg)
	except http.GatewayTimeoutException as e:
		return (e.message, e.status)

	try:
		http_rsp = create_http_rsp(
			core_rsp, msg.get('response_format'))
	except http.InternalServerError as e:
		return (e.message, e.status)

	print('returning ' + str(http_rsp))
	return http_rsp


@app.route('/viscus/cr/v1/payment', methods=[http.POST])
def payment():
	if encryption:
		log.info('encryption is enabled')
		log.warn('THIS FEATURE IS NOT YET IMPLEMENTED')
	try:
		msg = convert_to_dict(request)
	except http.BadRequestException as e:
		return (e.message, e.status)

	try:
		core_rsp = do_transaction(msg)
	except http.GatewayTimeoutException as e:
		return (e.message, e.status)

	try:
		http_rsp = create_http_rsp(
			core_rsp, msg.get('response_format'))
	except http.InternalServerError as e:
		return (e.message, e.status)

	print('returning ' + str(http_rsp))
	return http_rsp


@timeit
def do_transaction(msg):
	server_date_time = datetime.now()
	log.info('server time: ' + str(server_date_time))
	msg_guid = str(get_guid())
	log.info('message guid: ' + str(msg_guid))

	txn_type = mu.get_type(msg)
	mu.set_guid(msg, msg_guid)
	log.info('type: ' + txn_type)

	mu.set_status(msg, 'received')

	try:
		send_to_core(msg)
	except Exception as e:
		# Some serious database error needs to be handled
		raise e

	try:
		print('waiting for response for guid ' + msg_guid)
		core_rsp = recv_from_core(msg_guid)
	except http.GatewayTimeoutException as e:
		raise e

	return core_rsp


@app.route('/viscus/cr/v1/transaction', methods=[http.POST])
# list of media types expanded to parameters
@consumes(*ACCEPTED_MIMETYPES)
@produces(*ACCEPTED_MIMETYPES)
def transaction():
	try:
		msg = convert_to_dict(request)
	except http.BadRequestException as e:
		return (e.message, e.status)

	try:
		core_rsp = do_transaction(msg)
		print('core_rsp: ' + json.dumps(core_rsp))
	except http.GatewayTimeoutException as e:
		return (e.message, e.status)

	try:
		http_rsp = create_http_rsp(
			core_rsp, msg.get('response_format'))
	except http.InternalServerError as ise:
		return ise.response
	except http.NotImplementedException as nie:
		return nie.response

	#print(dir(http_rsp))
	print('returning data: ' + str(http_rsp.data))
	return http_rsp


# this method should later be moved to separate module
@app.route('/viscus/data/v1/terminalconfig', methods=[http.POST])
def post_terminal_config():
	try:
		config = convert_to_dict(request)
	except http.BadRequestException as bre:
		return bre.response

	if terminal_config_exists(config):
		return ('Data already exists', 409)

	try:
		save_terminal_config(config)
	except Exception, e:
		return (e.message, e.status)

	return ('Created', 201)


# this method should later be moved to separate module
@app.route('/viscus/data/v1/terminalconfig', methods=[http.DELETE])
def delete_terminal_config():
	try:
		config = convert_to_dict(request)
	except http.BadRequestException as bre:
		return bre.response

	config_id = get_config_id(config)

	db.delete(config_id)

	return ('No content', 204)


@app.route('/viscus/routestatus/<route>')
def route_status(route):
	nie = http.NotImplementedException()
	return nie.response


###################
# utility methods #
###################

def recv_from_core(guid):
	rsp = q.dequeue(guid, 0)
	print('response received')
	print(rsp)
	if isinstance(rsp, str):
		rsp = json_to_dict(rsp)
	return rsp


def send_to_core(msg):
	if isinstance(msg, dict):
		msg = dict_to_json(msg)
	log.info('sending message ' + msg + ' to queue incoming')

	q.enqueue('incoming', msg, 0)


def now():
	return time.time()


def create_response(data, status, mimetype):
	return Response(data, status, mimetype=mimetype)


def create_http_rsp(core_rsp, rsp_format):
	if http.is_xml(rsp_format):
		try:
			xml_rsp = dict_to_xml(core_rsp)
			http_rsp = create_response(
				xml_rsp, 200, http.MimeType.app_xml)
		except Exception:
			log.info('Error converting core response to xml')
			raise http.InternalServerError('Internal server error')

	elif http.is_json(rsp_format):
		try:
			json_rsp = dict_to_json(core_rsp)
			http_rsp = create_response(
				json_rsp, 200, http.MimeType.app_json)
		except Exception:
			log.info('Error converting core response to json')
			raise http.InternalServerError('Internal server error')

	elif http.is_yaml(rsp_format):
		raise http.NotImplementedException

	return http_rsp


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

initialize()


if __name__ == '__main__':
	initialize()
	app.run(debug=debug, processes=4)
