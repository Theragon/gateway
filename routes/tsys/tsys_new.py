import xmltodict
import logging
import random
import atexit
import redis
import json
import time
import sys
from Queue import Queue
from collections import OrderedDict

from tsysvalidator import validate_msg, ValidationError


log = logging.getLogger(__name__)
h = logging.StreamHandler(sys.stdout)
log_format = \
	'%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s'
f = logging.Formatter(log_format)
h.setFormatter(f)
log.addHandler(h)
log.setLevel(logging.DEBUG)


class MessageMonitor():

	def __init__(s, **kwargs):
		s.host = kwargs.get('host', 'localhost')
		s.port = kwargs.get('port', 6379)
		s.db = kwargs.get('db', 0)
		s.queue_name = kwargs.get('queue_name', 'tsys:incoming')
		s.callback = kwargs.get('cb', None)
		if s.callback is None:
			raise AttributeError('callback must be specified')

		s.inner_queue = Queue()

		s.red = redis.StrictRedis(host=s.host, port=s.port, db=s.db)

	def get_payload(s, msg):
		payload = msg[1]
		return payload

	def wait_for_msg(s):
		try:
			msg = s.red.blpop(s.queue_name, timeout=0)
			log.info('MessageMonitor delivering msg: ' + msg[1])
			payload = s.get_payload(msg)
			return json.loads(payload)
		except KeyboardInterrupt:
			log.info('shutting down')
			sys.exit()

	def monitor_msg_queue(s):
		log.info('MessageMonitor monitoring queue ' + s.queue_name)
		while True:
			msg = s.wait_for_msg()
			if s.callback:
				log.info('callback: ' + str(s.callback))
				s.callback(msg)
			else:
				s.inner_queue.put(msg)

	def get_msg(s):
		s.inner_queue.get()


class TsysRoute(object):
	"""Description of TsysRoute"""
	#red = redis.StrictRedis(host='localhost', port=6379, db=0)
	route = 'tsys'
	queue_name = route + ':incoming'

	red = redis.StrictRedis(host='localhost', port=6379, db=0)
	ps = red.pubsub()

	def msg_received(s, msg):
		log.info('message received')
		log.info('msg: ' + str(msg))
		txn_type = msg.iterkeys().next()
		#todo: finish validation
		try:
			validate_msg(msg)
		except ValidationError as e:
			log.debug('validation failed')
			log.debug(e.errors)
			#todo: handle exception correctly

		#todo: create tsys request
		if txn_type == 'payment':
			tsys_payment = s.create_payment(msg)
			log.debug('tsys_payment: ' + tsys_payment)
		#todo: send to tsys
		#todo: receive response
		#todo: create core response
		#msg = json.loads(msg)
		guid = msg[txn_type]['guid']

		secs = random.uniform(0, 10)
		log.info('sleeping for ' + str(secs) + ' seconds')
		#time.sleep(secs)
		log.info('done')
		s.red.rpush(guid, json.dumps(msg))  # echo msg back to http server

	def on_exit(s):
		s.red.publish('offline_routes', 'tsys')

	def __init__(s):
		log.info('initializing tsys route')
		s.msg_mon = MessageMonitor(queue_name=s.queue_name, cb=s.msg_received)
		atexit.register(s.on_exit)
		s.red.publish('online_routes', 'tsys')

	def start(s):
		s.msg_mon.monitor_msg_queue()
		s.msg_received(s.msg_mon.get_msg())

	# move this method to a separate class
	def create_payment(s, msg):
		pos_id = "800018160066091"
		gen_key = "9E08623B129A9C2EF9E01556"
		dev_id = '002628'
		ver_id = 'H001'

		payment = OrderedDict()
		payment['SGREQ'] = {}  # create the nested structure

		payment['SGREQ']['A1'] = pos_id
		payment['SGREQ']['A3'] = gen_key
		payment['SGREQ']['A10'] = '10'
		payment['SGREQ']['A12'] = msg.get('payment').get('paymentCode')
		payment['SGREQ']['A15'] = msg.get('payment').get('amount')
		payment['SGREQ']['A17'] = msg.get('payment').get('transactionCounter')

		payment['SGREQ']['A21'] = {}
		payment['SGREQ']['A21']['B1'] = msg.get('payment').get('f22')[0]
		payment['SGREQ']['A21']['B2'] = msg.get('payment').get('f22')[1]
		payment['SGREQ']['A21']['B3'] = msg.get('payment').get('f22')[2]
		payment['SGREQ']['A21']['B4'] = msg.get('payment').get('f22')[3]
		payment['SGREQ']['A21']['B5'] = msg.get('payment').get('f22')[4]
		payment['SGREQ']['A21']['B6'] = msg.get('payment').get('f22')[5]
		payment['SGREQ']['A21']['B9'] = msg.get('payment').get('f22')[6]
		payment['SGREQ']['A21']['B13'] = msg.get('payment').get('f22')[7]

		payment['SGREQ']['A24'] = msg.get('payment').get('track2Data')
		payment['SGREQ']['A41'] = dev_id
		payment['SGREQ']['A42'] = ver_id

		xml = xmltodict.unparse(payment, full_document=False)
		return xml


if __name__ == '__main__':
	tsys = TsysRoute()
	tsys.start()
