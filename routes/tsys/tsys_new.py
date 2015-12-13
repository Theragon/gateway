import logging
import redis
import json
import sys
from Queue import Queue


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
		s.callback = kwargs.get('callback', None)
		if s.callback is None:
			raise AttributeError('callback must be specified')

		s.inner_queue = Queue()

		s.red = redis.StrictRedis(host=s.host, port=s.port, db=s.db)

	def get_payload(s, msg):
		payload = msg[1]
		return payload

	def wait_for_msg(s):
		msg = s.red.blpop(s.queue_name, timeout=0)
		log.info('MessageMonitor delivering msg: ' + msg[1])
		payload = s.get_payload(msg)
		return json.loads(payload)
		#return msg[1]

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

	def msg_received(s, msg):
		log.info('message received')
		log.info('msg: ' + str(msg))
		#todo: validate
		#todo: create tsys request
		#todo: send to tsys
		#todo: receive response
		#todo: create core response
		#msg = json.loads(msg)
		txn_type = msg.iterkeys().next()
		guid = msg[txn_type]['guid']
		s.red.rpush(guid, json.dumps(msg))  # echo msg back to http server

	def __init__(s):
		log.info('initializing tsys route')
		s.msg_mon = MessageMonitor(queue_name=s.queue_name, callback=s.msg_received)

	def start(s):
		s.msg_mon.monitor_msg_queue()
		s.msg_received(s.msg_mon.get_msg())


if __name__ == '__main__':
	tsys = TsysRoute()
	tsys.start()
