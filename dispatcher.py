import multiprocessing as mp
from core.gateway import Gateway
import redis
import json


class Dispatcher(object):
	"""Class that monitors a message queue and dispatches a message"""
	def __init__(self):
		self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
		self.ps = self.r.pubsub(ignore_subscribe_messages=True)
		self.ps.subscribe('requests')
		#self.cores = mp.cpu_count()
		#self.procs = []
		#for i in range(self.cores):
		#	p = mp.Process(target=dispatch_msg, args=(msg,))
		#	self.procs.append(p)

	def run(self):
		while True:
			guid = self.wait_for_msg()
			msg = self.get_msg(guid)
			self.dispatch_msg(msg)

	def get_msg(self, guid):
		print('getting message: ' + guid)
		msg = self.r.lpop(guid)
		return json.loads(msg)

	def wait_for_msg(self):
		#msg = self.ps.get_message()
		for msg in self.ps.listen():
			print(str(msg) + 'received')
			return msg['data']

	def dispatch_msg(self, msg):
		print('dispatching message')
		gw = Gateway()
		p = mp.Process(target=gw.process_msg, args=(msg,))
		p.start()


def main():
	#cores = mp.cpu_count()
	#jobs = []
	#for i in range(cores):
	#	p = mp.Process(target=target, args=(msg,))
	d = Dispatcher()
	guid = d.wait_for_msg()
	msg = d.get_msg(guid)

	print('msg received: ' + msg)

if __name__ == '__main__':
	d = Dispatcher()
	d.run()
