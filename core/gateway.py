import logging.config
import logging
import redis
import json
import sys

from messagehandler import MessageHandler

#if sys.version_info[0] < 3:
#	from logutils.queue import QueueHandler, QueueListener
#else:
#	from logging.handlers import QueueHandler, QueueListener


log = logging.getLogger(__name__)


def set_up_log():
	global log
	h = logging.StreamHandler(sys.stdout)
	log_format = \
		'%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s'
	#	'%(asctime)s %(processName)-10s %(levelname)-8s %(message)s'
	f = logging.Formatter(log_format)
	h.setFormatter(f)
	log.addHandler(h)
	log.setLevel(logging.DEBUG)


class Gateway():
	red = redis.StrictRedis(host='localhost', port=6379, db=0)
	#ps = red.pubsub()

	def __init__(self, target=None, callback=None):
		#s = self

		set_up_log()
		log.debug('starting Gateway')
		self.callback = callback

		self.workers = []


	def start(self):
		try:
			self.monitor_msg_queue()
		except KeyboardInterrupt:
			self.exit()

	def delegate(self, msg):
		log.info('starting new process')
		handler = MessageHandler(msg=msg)
		self.workers.append(handler)
		handler.start()

	def exit(self):
		#s = self
		log.info('waiting for workers to finish')
		for w in self.workers:
			w.join()

	def monitor_msg_queue(self):
		while True:
			msg = self.get_msg()
			log.info('message received')
			log.info(msg)
			self.delegate(msg)

	def get_payload(self, msg):
		payload = msg[1]
		return payload.decode('utf-8')

	def get_msg(self):
		"""
		Pop message from message queue and return its payload
		"""
		msg = self.red.blpop('incoming', timeout=0)
		payload = self.get_payload(msg)
		return json.loads(payload)


if __name__ == '__main__':
	gw = Gateway()
	gw.start()
