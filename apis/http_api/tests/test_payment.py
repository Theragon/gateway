from lxml import etree
import unittest
import requests
import json
from mock import *

payment_url = 'http://localhost:5000/viscus/cr/v1/payment'

OK = 200
NOT_ALLOWED = 405

app_xml = {'Content-Type': 'application/xml'}
text_xml = {'Content-Type': 'text/xml'}
app_json = {'Content-Type': 'application/json'}


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

	@unittest.skip("")
	def test_post_json(self):
		resp = requests.post(
			payment_url,
			data=json.dumps(payment_json),
			headers=app_json)
		print('resp.text: ' + str(resp.text))
		#print('resp.content: ' + str(resp.content))
		#print('dir(resp): ' + str(dir(resp)))
		assert resp.status_code == requests.codes.ok
		#assert resp.text == 'OK'

	@unittest.skip("")
	def test_xml_payment_tsys(self):
		xml = get_xml_payment('tsys')
		resp = requests.post(payment_url, data=xml, headers=app_xml)
		print('resp.text: ' + str(resp.text))
		#print('resp.content: ' + str(resp.content))

		assert resp.status_code is not None
		#assert resp.status_code == requests.codes.ok

	#@unittest.skip("")
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
		"""with patch.object(ProductionClass, 'method', return_value=None) as mock_method:
									thing = ProductionClass()
									thing.method(1, 2, 3)"""


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
