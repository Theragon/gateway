import atexit
import redis
import time


class EvoRoute(object):
	"""docstring for EvoRoute"""

	def on_exit(s):
		s.red.publish('offline_routes', 'evo')

	def __init__(s):
		super(EvoRoute, s).__init__()
		atexit.register(s.on_exit)
		s.red = redis.StrictRedis(host='localhost', port=6379, db=0)
		s.ps = s.red.pubsub()
		s.red.publish('online_routes', 'evo')

	def start(s):
		while True:
			time.sleep(1)

if __name__ == '__main__':
	evo = EvoRoute()
	evo.start()
