import multiprocessing as mpr
import threading
import logging
import pprint
import redis
import time
import sys

sys.path.append('/home/logi/repos/gateway')

from utils import queueutils as q
#from utils.parseutils import json_to_dict, dict_to_json
from utils import messageutils as mu
from utils import pubsub as ps

log = logging.getLogger(__name__)

debug = True
red = redis.StrictRedis(host='localhost', port=6379, db=0)
#ps = red.pubsub()


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
			msg = s.get_request()
			route = mu.get_route(msg)
			queue = route + ':incoming'
			log.info('delivering message to queue ' + queue)
			#s.deliver_to_route(queue, dict_to_json(msg))
			s.deliver_to_route(queue, msg)
			rsp = s.get_response()
			s.deliver_to_front(rsp)

	def get_request(s):
		log.info('waiting for message on queue incoming')
		msg = q.dequeue_d('incoming')
		log.info('received msg ' + str(msg))
		return msg

	def get_response(s):
		log.info('waiting for response from route')
		rsp = q.dequeue_d('core:outgoing')
		log.info('response received from route: ' + str(rsp))
		return rsp

	def deliver_to_route(s, queue, msg):
		q.enqueue_d(queue, msg)

	def deliver_to_front(s, msg):
		guid = mu.get_guid(msg)
		q.enqueue_d(guid, msg)


class GateWay():
	"""docstring for GateWay"""

	def monitor_routes(s):
		while True:
			# check if new routes are offline/online
			s.check_route_status()
			time.sleep(0.25)

	def check_route_status(s):
		status = None
		rsp = q.dequeue('route-status', 100)
		if rsp:
			log.info('route status: ' + rsp)
			route, status = rsp.split(':')
		if status == 'online':
			s.mark_route_online(route)
		if status == 'offline':
			s.mark_route_offline(route)


	def mark_route_online(s, route):
		s.routes.append(route)
		log.info(pprint.pformat(s.routes))

	def mark_route_offline(s, route):
		try:
			s.routes.remove(route)
		except ValueError:
			log.info('route ' + route + ' not registered')
		finally:
			log.info(pprint.pformat(s.routes))


	def ask_online_routes_to_republish(s):
		log.info('asking online routes to republish status')
		ps.publish('route-status-publish', 'all:republish')


	def start(s):
		s.ask_online_routes_to_republish()
		for i in range(s.num_workers):
			worker = Worker()
			s.workers.append(worker)
			worker.start()

	def exit(s):
		log.info('waiting for workers to finish')
		for w in s.workers:
			w.join()
		s.thread.join()

	def __init__(s):
		set_up_log()
		log.debug('starting Gateway')
		s.routes = []
		if debug:
			s.num_workers = 1
		else:
			s.num_workers = 2
		q.connect()

		s.thread = threading.Thread(target=s.monitor_routes, args=())
		s.thread.daemon = True
		s.thread.start()

		s.workers = []


def main():
	from os.path import dirname as dir
	from sys import path
	print(dir(path[0]))
	path.append(dir(path[0]))

	gw = GateWay()
	try:
		gw.start()
	finally:
		gw.exit()


if __name__ == '__main__':
	main()
