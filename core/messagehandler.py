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

	def run(s):
		s.deliver_msg(s.msg)

	def create_queue_name(s, route):
		queue_name = route + ':incoming'
		return queue_name

	def deliver_msg(s, msg):
		log.info('message handler handling message')
		log.debug(msg)
		txn_type = msg.iterkeys().next()
		log.debug('type: ' + txn_type)
		route = msg.get('payment').get('route')
		log.debug('route: ' + str(route))

		queue_name = s.create_queue_name(route)
		log.debug('putting msg on queue ' + queue_name)
		s.red.rpush(queue_name, json.dumps(msg))

		#if txn_type == 'payment':
		#	self.do_payment(msg)
