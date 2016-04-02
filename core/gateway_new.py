import multiprocessing as mpr
import threading
import logging
import time
import sys

sys.path.append('/home/logi/repos/gateway')

#from utils import dbutils as db
from utils import queueutils as q
from utils.parseutils import json_to_dict, dict_to_json
#from messagehandler import MessageHandler

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


class Worker(mpr.Process):
	"""docstring for Worker"""
	def __init__(s):
		mpr.Process.__init__(s)
		s.queue_online = q.is_available()

	def run(s):
		log.info('worker running')
		while s.queue_online:
			msg = s.wait_for_request()
			txn_type = msg.iterkeys().next()
			route = msg.get(txn_type).get('route')
			queue = route + ':incoming'
			log.info('delivering message to queue ' + queue)
			s.deliver_to_route(queue, dict_to_json(msg))
			s.wait_for_response()

	def wait_for_request(s):
		log.info('waiting for message on queue incoming')
		msg = q.dequeue('incoming')
		log.info('received msg ' + msg)
		return json_to_dict(msg)

	def wait_for_response(s):
		log.info('waiting for response from route')
		rsp = json_to_dict(q.dequeue('core:outgoing'))
		log.info('response received from route: ' + str(rsp))

	def deliver_to_route(s, queue, msg):
		q.enqueue(queue, msg)


class GateWay():
	"""docstring for GateWay"""

	def monitor_routes(self):
		while True:
			# check online routes
			self.check_online_routes()
			# check offline routes
			self.check_offline_routes()
			time.sleep(0.25)

	def check_online_routes(self):
		rsp = q.dequeue('online_routes', 100)
		if rsp is not None:
			self.mark_route_online(rsp)

	def check_offline_routes(self):
		rsp = q.dequeue('offline_routes', 100)
		if rsp is not None:
			self.mark_route_offline(rsp)

	def mark_route_online(self, route):
		self.routes.append(route)
		log.info(self.routes)

	def mark_route_offline(self, route):
		try:
			self.routes.remove(route)
		except ValueError:
			log.info('route ' + route + ' not registered')
		finally:
			log.info(self.routes)


	def start(s):
		for i in range(s.num_workers):
			worker = Worker()
			s.workers.append(worker)
			worker.start()

	def exit(s):
		log.info('waiting for workers to finish')
		for w in s.workers:
			w.join()
		s.thread.join()

	def __init__(self):
		#s = self
		set_up_log()
		log.debug('starting Gateway')
		self.routes = []
		self.num_workers = 2
		q.connect()

		self.thread = threading.Thread(target=self.monitor_routes, args=())
		self.thread.daemon = True
		self.thread.start()

		self.workers = []


def main():
	try:
		gw = GateWay()
		gw.start()
	finally:
		gw.exit()


if __name__ == '__main__':
	main()
	#gw = GateWay()
	#gw.start()
