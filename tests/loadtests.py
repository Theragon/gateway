import threading
import unittest
import requests
import json
from time import time

transaction_url = 'http://localhost:5000/viscus/cr/v1/transaction'
payment_url = 'http://localhost:5000/viscus/cr/v1/payment'

app_json = {'Content-Type': 'application/json'}

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
			u'currency': u'USD',
			u'amount': u'10.00',
			u'paymentScenario': u'CHIP',
			u'cardAcceptorId': u'TestHekla5',
			u'accountType': u'30',
			u'guid': u'f3d316bc-cc11-4622-b70a-3ace13cb9c45',
			u'authorizationGuid': u'86ee88f8-3245-4fa6-a7fb-354ef1813854',
			u'terminalDateTime': u'20130614172956000',
			u'configVersion': u'12',
			u'terminalUserId': u'OP1',
			u'terminalOsVersion': u'1.08.00',
			u'paymentCode': u'D',
			u'track2Data': u'5592000010000001=16111210000000000000',
		}
	}


def run_in_background(method):
	#global bg_thread
	# Initialize thread with a method and run it in background
	bg_thread = threading.Thread(target=method, args=())
	bg_thread.start()


def post_payment(data):
	rsp = requests.post(payment_url, data=data, headers=app_json)
	#print('response received ' + str(threading.current_thread().name))
	assert rsp
	#return rsp


def timeit(method):
	def timed(*args, **kw):
		#print('STARTING TIMER')
		start = time()
		result = method(*args, **kw)
		end = time()
		delta = end - start

		if delta >= 1:
			print('%s function took %0.3f s' % (method.__name__, delta))
		else:
			print('%s function took %0.3f ms' % (method.__name__, (delta)*1000.0))
		return result
	return timed


@timeit
def start_threads(threads):
	for t in threads:
		t.start()


class FunctionalTests(unittest.TestCase):
	"""docstring"""

	def test_01_hundred_messages(self):
		data = json.dumps(payment)

		threads = []

		for i in range(100):
			t = threading.Thread(target=post_payment, args=(data,))
			threads.append(t)

		start_threads(threads)

		#print('threads are off')

		for t in threads:
			t.join()

if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(FunctionalTests)
	unittest.TextTestRunner(verbosity=2).run(suite)
