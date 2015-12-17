import multiprocessing as mpr
import logging
import redis
import json
import sys

import config as cfg

log = logging.getLogger(__name__)
sh = logging.StreamHandler(sys.stdout)
log_format = \
		'%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s'
f = logging.Formatter(log_format)
sh.setFormatter(f)
log.addHandler(sh)
if cfg.debug:
	log.setLevel(logging.DEBUG)
else:
	log.setLevel(logging.INFO)


class MessageHandler(mpr.Process):
	"""Description of MessageHandler"""
	red = redis.StrictRedis(host='localhost', port=6379, db=0)

	def __init__(s, **kwargs):
		super(MessageHandler, s).__init__()
		s.msg = kwargs.get('msg', None)

		s.config = None

	def run(s):
		s.get_terminal_config()
		s.deliver_msg()

	def create_queue_name(s, route):
		queue_name = route + ':incoming'
		return queue_name

	def get_terminal_config(s):
		txn_type = s.msg.iterkeys().next()
		log.debug('txn_type: ' + txn_type)
		serial_number = s.msg.get(txn_type).get('serialNumber', None)
		log.info('getting config for ' + serial_number)
		s.config = s.red.get(serial_number)
		if s.config is None:
			# config not found - return an error
			log.info('config for serial number ' + serial_number + ' not found')
		else:
			log.info('config found for serial number ' + serial_number)

	def deliver_msg(s):
		log.info('message handler handling message')
		log.debug(s.msg)
		txn_type = s.msg.iterkeys().next()
		log.debug('type: ' + txn_type)
		route = s.msg.get('payment').get('route')
		log.debug('route: ' + str(route))

		queue_name = s.create_queue_name(route)
		log.debug('putting msg on queue ' + queue_name)
		s.red.rpush(queue_name, json.dumps(s.msg))

		#if txn_type == 'payment':
		#	self.do_payment(msg)
