from collections import OrderedDict
from Queue import Queue
import xmltodict
#import threading
import logging
import random
import redis
import time
#import json
import uuid
import sys

sys.path.append('/home/logi/repos/gateway')

from tsysvalidator import validate_msg, ValidationError
from utils import queueutils as q
from utils import pubsub as ps
from utils import messageutils as mu

red = redis.StrictRedis(host='localhost', port=6379, db=0)
#ps = red.pubsub()

log = logging.getLogger(__name__)
h = logging.StreamHandler(sys.stdout)
log_format = \
	'%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s'
f = logging.Formatter(log_format)
h.setFormatter(f)
log.addHandler(h)
log.setLevel(logging.DEBUG)

unique_id = uuid.uuid4().hex
route_name = 'tsys-' + unique_id


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

	def get_payload(s, msg):
		payload = msg[1]
		return payload

	def wait_for_msg(s):
		try:
			msg = q.dequeue_d(s.queue_name)
			log.info('MessageMonitor delivering msg: ' + str(msg))
			return msg
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

	route = 'tsys'
	queue_name = route + ':incoming'


	def get_terminal_config(s):
		txn_type = s.msg.iterkeys().next()
		log.debug('txn_type: ' + txn_type)
		serial_number = s.msg.get(txn_type).get('serialNumber', None)
		log.info('getting config for ' + serial_number)
		s.config = s.red.get(serial_number)
		if s.config is None:
			# config not found - return an error
			log.info('config for serialnumber ' + serial_number + ' not found')
		else:
			log.info('config found for serialnumber ' + serial_number)


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
		guid = mu.get_guid(msg)
		log.info('guid: ' + guid)

		secs = random.uniform(0, 2)
		log.info('sleeping for ' + str(secs) + ' seconds')
		#time.sleep(secs)
		log.info('done')

		q.enqueue_d('core:outgoing', msg)  # echo msg back to core

	def my_handler(s, msg):
		print('MY HANDLER: ', msg['data'])
		payload = msg['data']
		if payload == 'all:republish':
			publish_status('online')

	def monitor_routes(self):
		while True:
			# check if new routes are offline/online
			rsp = q.dequeue('route-status-publish', 100)
			if rsp == 'all:republish':
				log.info('republish message received - republishing status')
				publish_status('online')
			time.sleep(0.25)


	def __init__(s):
		log.info('initializing tsys route')
		q.connect()
		s.msg_mon = MessageMonitor(queue_name=s.queue_name, cb=s.msg_received)

		ps.subscribe(**{'route-status-publish': s.my_handler})
		s.thread = ps.run_in_thread(sleep_time=0.001)

		#s.thread = threading.Thread(target=s.monitor_routes, args=())
		#s.thread.daemon = True
		#s.thread.start()

		publish_status('online')

	def stop(s):
		log.info('going down')
		s.thread.stop()
		publish_status('offline')

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


def publish_status(status):
	log.info('publishing status: ' + status)
	q.enqueue('route-status', route_name + ':' + status)


def on_exit():
	publish_status('offline')


def main():
	tsys = TsysRoute()
	try:
		tsys.start()
	finally:
		#log.info('going down')
		tsys.stop()
		#on_exit()

if __name__ == '__main__':
	main()
	#tsys = TsysRoute()
	#tsys.start()
