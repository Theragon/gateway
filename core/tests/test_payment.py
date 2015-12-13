import threading
import unittest
import redis
import json
import sys
import os

#from .core import dispatcher
#from dispatcher import Dispatcher

proj_root = os.path.dirname(os.path.dirname(os.getcwd()))
print('proj_root: ' + proj_root)
full_path = __file__
print('full_path: ' + full_path)
print('1 level up: ' + os.path.dirname(full_path))
print('2 levels up: ' + os.path.dirname(os.path.dirname(full_path)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(full_path))))
sys.path.append(proj_root)
#from core import *
#from core.gateway import Gateway
#from core.dispatcher import Dispatcher

red = redis.StrictRedis(host='localhost', port=6379, db=0)
ps = red.pubsub(ignore_subscribe_messages=True)
ps.subscribe('requests')

# Create a thread to run tasks in background
bg_thread = threading.Thread()
# Create a queue to store results from background thread
#msg_store = Queue.Queue()

tsys_incoming = 'tsys:incoming'

payment = \
	{
		u'payment':
		{
			u'nonce': u'7604056809',
			u'deviceType': u'MPED400',
			u'transactionCounter': u'3',
			u'customerReference': u'00000001',
			u'f22': u'51010151114C',
			u'route': u'tsys',
			u'serialNumber': u'311001305',
			u'softwareVersion': u'1.3.1.15',
			u'emvData': u'4f07a00000000430605712679999',
			u'currency': u'GBP',
			u'amount': u'10.00',
			u'paymentScenario': u'CHIP',
			u'cardAcceptorId': u'TestHekla5',
			u'accountType': u'30',
			u'guid': u'f3d316bc-cc11-4622-b70a-3ace13cb9c45',
			u'authorizationGuid': u'86ee88f8-3245-4fa6-a7fb-354ef1813854',
			u'terminalDateTime': u'20130614172956000',
			u'configVersion': u'12',
			u'terminalUserId': u'OP1',
			u'terminalOsVersion': u'1.08.00'
		}
	}


def get_msg_wait(queue_name):
	"""
	Pop message from message queue and return its payload
	"""
	print('getting message from ' + queue_name)
	msg = red.blpop(queue_name, timeout=0)
	#payload = self.get_payload(msg)
	#return json.loads(payload)
	return msg


def get_msg_no_wait(queue_name):
	"""
	Pop message from message queue and return its payload
	"""
	msg = red.lpop(queue_name)
	#payload = msg[1]
	#return json.loads(payload)
	return msg


def add_to_queue(key, value):
	print('adding message ' + json.dumps(value) + ' to queue ' + str(key))
	try:
		red.rpush(key, json.dumps(value))
	except Exception as e:
		raise e


def run_in_background(method):
	global bg_thread
	# Initialize thread with a method and run it in background
	bg_thread = threading.Thread(target=method, args=())
	bg_thread.start()


class PaymentTests(unittest.TestCase):

	"""docstring"""
	#gw = None

	@classmethod
	def setUpClass(cls):
		#cls.gw = Gateway()
		pass

	def test_tsys_payment2(self):
		import time

		guid = 'f3d316bc-cc11-4622-b70a-3ace13cb9c45'
		print('puting message with guid ' + guid + ' to queue')

		# put the message to the incoming queue
		add_to_queue('incoming', payment)

		# wait a little bit just in case (this is not really needed)
		time.sleep(0.1)

		# try to get the message from the queue
		gw_msg = get_msg_no_wait('incoming')
		# Gateway should already have received the message
		assert gw_msg is None

		# get the message from the route incoming queue
		route_msg = get_msg_wait(tsys_incoming)

		assert route_msg is not None


if __name__ == '__main__':
	unittest.main()
