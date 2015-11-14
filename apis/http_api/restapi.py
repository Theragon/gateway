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

r = redis.StrictRedis(
	host=pub_sub_host,
	port=pub_sub_port,
	db=pub_sub_db
)

sub = r.pubsub(ignore_subscribe_messages=True)
sub.subscribe(rsp_sub_id)

debug = True


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


class InternalServerError(Exception):
	"""docstring for InternalServerError"""
	def __init__(self, message):
		super(InternalServerError, self).__init__(message)
		#self.message = message


class BadRequestException(Exception):
	"""docstring for BadRequestException"""
	def __init__(self, message):
		super(BadRequestException, self).__init__(message)
		#self.arg = arg


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


def add_to_queue(key, value):
	print('adding message ' + json.dumps(value) + ' to queue ' + str(key))
	r.rpush(key, json.dumps(value))


def listen(msg):
	while True:
		m = r.get_message()
	return m


def wait_for_rsp2(guid):
	"""
	Subscribe to unique channel and wait for response
	"""
	channel_id = 'response:' + str(guid)
	log.info('subscribing to ' + channel_id + ' and waiting for response')
	sub.subscribe('responses')
	sub.subscribe(channel_id)
	for rsp in sub.listen():
		print('response received')
		print(rsp)
		return json.loads(rsp['data'])


def wait_for_rsp(guid):
	print('waiting for guid ' + str(guid))
	rsp = None
	while rsp is None:
		rsp = r.get(guid)
	r.delete(guid)
	return json.loads(rsp)


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
	#gw = Gateway()
	#data = {}
	#response = None

	msg_guid = get_guid()

	return msg_guid


@app.route('/viscus/cr/v1/payment', methods=[POST])
@timeit
def payment():
	#gw = Gateway()
	#http_rsp = None
	#msg = {}

	#logging.basicConfig(filename='example.log',level=logging.INFO)
	log.basicConfig(level=log.INFO, format='%(asctime)s %(message)s')

	server_date_time = datetime.now()
	log.info('server time: ' + str(server_date_time))
	msg_guid = str(get_guid())
	log.info('message guid: ' + str(msg_guid))
	#ksn = request.headers.get('ksn')
	#bdk = request.headers.get('bdk-index')

	try:
		msg = convert_to_dict(request)
	except BadRequestException as e:
		return (e.message, 400)

	msg['payment']['guid'] = msg_guid
	msg['type'] = msg.iterkeys().next()
	log.info('type: ' + msg['type'])
	add_to_queue('incoming', msg)
	core_rsp = wait_for_rsp(msg_guid)

	try:
		http_rsp = create_http_rsp(core_rsp, request)
	except Exception as e:
		return (e.message, 500)

	print('returning ' + str(http_rsp))
	return http_rsp


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


if __name__ == '__main__':
	initialize()
	app.run(debug=debug)
