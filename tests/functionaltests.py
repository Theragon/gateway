import threading
import unittest
import requests
import json

transaction_url = 'http://localhost:5000/viscus/cr/v1/transaction'
payment_url = 'http://localhost:5000/viscus/cr/v1/payment'

app_json = {'Content-Type': 'application/json'}

"""
<payment>
	<amount>999999999999</amount>
	<cardAcceptorId>DEV_DUMMY</cardAcceptorId>
	<configVersion>2</configVersion>
	<currency>BYR</currency>
	<customerReference>cusRef1</customerReference>
	<deviceType>MPED400</deviceType>
	<f22>51010151134C</f22>
	<f52>****************</f52>
	<nonce>03140955183</nonce>
	<paymentCode>C</paymentCode>
	<paymentScenario>MAGSTRIPE</paymentScenario>
	<serialNumber>474795320209</serialNumber>
	<softwareVersion>1.0.0</softwareVersion>
	<terminalDateTime>20151203140955183</terminalDateTime>
	<terminalOsVersion>1.0.0</terminalOsVersion>
	<terminalUserId>userId</terminalUserId>
	<tipAmount>1</tipAmount>
	<track2Data>5592000010000001=16111210000000000000</track2Data>
	<transactionCounter>234546</transactionCounter>
</payment>
"""
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
	return rsp


class FunctionalTests(unittest.TestCase):
	"""docstring"""
	#@unittest.skip('')
	def test_01_tsys_payment(self):
		data = json.dumps(payment)
		rsp = requests.post(payment_url, data=data, headers=app_json)
		assert rsp is not None
		print('rsp: ' + rsp.text)


if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(FunctionalTests)
	unittest.TextTestRunner(verbosity=2).run(suite)
