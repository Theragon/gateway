import unittest
import sys
import os

proj_root = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.append(proj_root)
from core.gateway import *

payment_json = \
	{
		"payment":
		{
			# required for evo, not for tsys
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
			'route': 'tsys'
		}
	}


class PaymentTests(unittest.TestCase):

	"""docstring"""

	#@unittest.skip("")
	def test_tsys_payment(self):
		resp = do_payment('tsys', payment_json)
		assert resp is not None

	def test_not_implemented_evo_payment(self):
		resp = None
		try:
			resp = do_payment('evo', payment_json)
		except NotImplementedError:
			#assert isinstance(resp, NotImplementedError)
			return True
		print('resp:' + str(resp))


if __name__ == '__main__':
	unittest.main()
