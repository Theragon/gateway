import multiprocessing as mpr
import logging
import sys

sys.path.append('/home/logi/repos/gateway')

from utils import dbutils as db

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


def wait_for_msg():
	db.get_msg()


class GateWay():
	"""docstring for GateWay"""

	def register_route(self, msg):
		route = msg.get('data')
		log.info('route ' + route + ' is online')
		self.routes.append(route)
		log.info(self.routes)

	def deregister_route(self, msg):
		route = msg.get('data')
		log.info('route ' + route + ' is offline')
		try:
			self.routes.remove(route)
		except ValueError:
			log.info('route ' + route + ' not registered')
		finally:
			log.info(self.routes)

	def start_process(self):
		print('Starting ' + mpr.current_process().name)
		self.monitor_msg_queue()

	def start(s):
		s.pool = mpr.Pool(
			processes=2,
			initializer=s.start_process,
			maxtasksperchild=2)
		#s.pool.apply_async()

	def monitor_msg_queue(self):
		print(mpr.current_process().name + ' monitoring message queue')
		while True:
			msg = db.get_msg()
			log.info('message received')
			log.info(msg)
			#self.delegate(msg)

	def __init__(self, target=None, callback=None):
		#s = self
		self.ps = db.pubsub
		self.routes = []

		#self.ps.subscribe(**{'online_routes': self.register_route})
		#self.ps.subscribe(**{'offline_routes': self.deregister_route})
		db.subscribe_to_channel('online_routes', self.register_route)
		db.subscribe_to_channel('offline_routes', self.deregister_route)
		self.thread = self.ps.run_in_thread(sleep_time=0.001)
		set_up_log()
		log.debug('starting Gateway')
		self.callback = callback

		self.workers = []
		self.pool = None
		#self.pool = mpr.Pool(processes=2, initializer=self.start_process,)


if __name__ == '__main__':
	gw = GateWay()
	gw.start()
