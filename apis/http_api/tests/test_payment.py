from lxml import etree
#import multiprocessing
import threading
import unittest
import requests
import redis
#from multiprocessing import Queue
import Queue
import json
#from mock import *

payment_url = 'http://localhost:5000/viscus/cr/v1/payment'

OK = 200
NOT_ALLOWED = 405

app_xml = {'Content-Type': 'application/xml'}
text_xml = {'Content-Type': 'text/xml'}
app_json = {'Content-Type': 'application/json'}


red = redis.StrictRedis(host='localhost', port=6379, db=0)
ps = red.pubsub(ignore_subscribe_messages=True)
ps.subscribe('requests')

rsp = None


def get_msg():
	print('getting message')
	msg = red.blpop('incoming', timeout=0)
	print('msg: ' + str(msg[1]))
	return json.loads(msg[1])


def post_xml_payment(queue):
	#global rsp
	xml = get_xml_payment('tsys')
	http_rsp = requests.post(payment_url, data=xml, headers=app_xml)
	print('thread exiting')
	#print(http_rsp.text)
	#rsp = json.loads(r.text)
	queue.put(http_rsp)


def run_in_background(method):
	# Create a queue to store the result from the thread
	queue = Queue.Queue()
	# Create a thread to wait for the http response in the background
	t = threading.Thread(target=method, args=(queue,))
	t.start()
	return queue


class PaymentTests(unittest.TestCase):

	"""docstring"""

	@classmethod
	def setUpClass(cls):
		#global payment_xml
		#payment_xml = get_xml_payment()
		pass

	'''@classmethod
	def tearDownClass(cls):
		print('tearing down tests')'''

	@unittest.skip("")
	def test_get(self):
		resp = requests.get(payment_url)
		assert resp.status_code == requests.codes.not_allowed
		assert resp.text == 'Method not allowed'


	#@unittest.skip("")
	def test_xml_payment_tsys(self):
		# Make sure the db is clean before test
		red.flushdb()

		# Run the http post request in background and add the result to queue
		queue = run_in_background(post_xml_payment)

		# Get the message from the rest interface incoming message queue
		msg = get_msg()

		# Assert that request was added to message queue
		assert msg is not None
		print(msg)

		guid = str(msg['payment']['guid'])

		# Create a core response
		core_rsp = create_core_rsp(guid)
		print('setting ' + guid + ' to queue')

		# Put the response on the outgoing queue
		red.set(guid, core_rsp)

		# Wait for background thread to return http response
		queue.join()
		# Get the result from the queue
		http_rsp = queue.get()
		print(http_rsp.text)
		#assert resp.status_code == requests.codes.ok

	@unittest.skip("")
	def test_json_payment_tsys(self):
		print('posting json payment')
		payment_json = get_json_payment('tsys')
		#headers = {'Content-Type': 'application/xml'}
		resp = requests.post(payment_url, data=payment_json, headers=app_json)
		print('resp.text: ' + str(resp.text))
		#print('resp.content: ' + str(resp.content))

		assert resp.status_code is not None

	@unittest.skip("")
	def test_xml_payment_evo(self):
		xml = get_xml_payment('evo')
		resp = requests.post(payment_url, data=xml, headers=app_xml)
		print('resp.text: ' + str(resp.text))
		assert resp is not None
		assert resp.status_code == requests.codes.server_error

	@unittest.skip("")
	def test_correct_method_called(self):
		xml = get_xml_payment('test')
		resp = requests.post(payment_url, data=xml, headers=app_xml)
		assert resp is not None


def get_xml_payment(route='tsys'):
	root = etree.Element("payment")
	etree.SubElement(root, "cardAcceptorId").text = "TestHekla5"
	etree.SubElement(root, "paymentScenario").text = "CHIP"
	etree.SubElement(root, "authorizationGuid").text = \
		"""86ee88f8-3245-4fa6-a7fb-354ef1813854"""
	etree.SubElement(root, "terminalDateTime").text = "20130614172956000"
	etree.SubElement(root, "nonce").text = "7604056809"
	etree.SubElement(root, "currency").text = "GBP"
	etree.SubElement(root, "amount").text = "10.00"
	etree.SubElement(root, "softwareVersion").text = "1.3.1.15"
	etree.SubElement(root, "configVersion").text = "12"
	etree.SubElement(root, "customerReference").text = "00000001"
	etree.SubElement(root, "emvData").text = "4f07a00000000430605712679999"
	etree.SubElement(root, "f22").text = "51010151114C"
	etree.SubElement(root, "serialNumber").text = "311001304"
	etree.SubElement(root, "terminalUserId").text = "OP1"
	etree.SubElement(root, "deviceType").text = "MPED400"
	etree.SubElement(root, "terminalOsVersion").text = "1.08.00"
	etree.SubElement(root, "transactionCounter").text = "3"
	etree.SubElement(root, "accountType").text = "30"
	etree.SubElement(root, "route").text = route
	return etree.tostring(root)


def create_core_rsp(guid):
	core_rsp = \
		{
			'payment':
			{
				'paynentGuid': guid,
				'amount': '100.00',
				'currency': 'GBP',
				'cardTypeName': 'MasterCard',
				'maskedCardNumber': '************9004',
				'expiryDateMMYY': '0308',
				'customerReference': '00000040',
				'acquirerTid': '90008910',
				'approvalCode': '013795',
				'issuerResponseText': 'TPOS 0000',
				'batchNumber': '1215',
				'transNumber': '19711',
				'serverDateTime': '20130618154721688',
				'terminalDateTime': '20130618154657000',
				'agreementNumber': '6819106',
				'cardAcceptorName': 'DEV_PED08',
				'cardAcceptorAddress': 'DEV_PED08',
				'nonce': '7604056809'
			}
		}
	return json.dumps(core_rsp)


def get_json_payment(route='tsys'):
	payment_json = \
		{
			"payment":
			{
				'cardAcceptorId': 'TestHekla5',
				'paymentScenario': 'CHIP',
				'softwareVersion': '1.3.1.15',
				'configVersion': '12',
				'terminalDateTime': '20130614172956000',
				'nonce': '7604056809',
				'authorizationGuid': '86ee88f8-3245-4fa6-a7fb-354ef1813854',
				'currency': 'GBP',
				'amount': '10.00',
				'customerReference': '00000001',
				'emvData': '4f07a00000000430605712679999',
				'f22': '51010151114C',
				'serialNumber': '311001304',
				'terminalUserId': 'OP1',
				'deviceType': 'MPED400',
				'terminalOsVersion': '1.08.00',
				'transactionCounter': '3',
				'accountType': '30',
				'route': route
			}
		}
	return json.dumps(payment_json)


if __name__ == '__main__':
	unittest.main()
