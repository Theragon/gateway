import unittest
import requests
import json

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


class FunctionalTests(unittest.TestCase):
	"""docstring"""
	def test_01_tsys_payment(self):
		data = json.dumps(payment)
		rsp = requests.post(payment_url, data=data, headers=app_json)
		assert rsp is not None
		print('rsp: ' + rsp.text)


if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(FunctionalTests)
	unittest.TextTestRunner(verbosity=2).run(suite)
