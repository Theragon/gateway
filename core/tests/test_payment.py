import unittest
import sys
import os

proj_root = os.path.dirname(os.path.dirname(os.getcwd()))
print('proj_root: ' + proj_root)
full_path = __file__
print('full_path: ' + full_path)
print('1 level up: ' + os.path.dirname(full_path))
print('2 levels up: ' + os.path.dirname(os.path.dirname(full_path)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(full_path))))
sys.path.append(proj_root)
#from core import *
from core.gateway import Gateway

payment = \
	{
		u"payment":
		{
			# required for evo, not for tsys
			u'cardAcceptorId': u'TestHekla5',
			u'paymentScenario': u'CHIP',
			u'softwareVersion': u'1.3.1.15',
			u'configVersion': u'12',
			u'terminalDateTime': u'20130614172956000',
			u'nonce': u'7604056809',
			u'authorizationGuid': u'86ee88f8-3245-4fa6-a7fb-354ef1813854',
			u'currency': u'USD',
			u'amount': u'10.00',
			u'customerReference': u'00000001',
			u'emvData': u'4f07a00000000430605712679999',
			u'track2Data': u'5592000010000001=16111210000000000000',
			u'f22': u'51010151114C',
			u'serialNumber': u'311001304',
			u'terminalUserId': u'OP1',
			u'deviceType': u'MPED400',
			u'terminalOsVersion': u'1.08.00',
			u'transactionCounter': u'3',
			u'accountType': u'30',
			u'paymentCode': u'D',
			u'tipAmount': u'0',
			u'route': u'tsys'
		}
	}


class PaymentTests(unittest.TestCase):

	"""docstring"""
	#gw = None

	@classmethod
	def setUpClass(cls):
		cls.gw = Gateway()

	def send_payment(self, msg):
		try:
			return self.gw.do_payment(msg)
		except Exception as e:
			return e

	#@unittest.skip("")
	def test_tsys_payment(self):
		resp = self.gw.do_payment(payment)
		assert resp is not None

	@unittest.skip("")
	def test_not_implemented_evo_payment(self):
		resp = None
		try:
			resp = self.gw.do_payment(payment)
		except NotImplementedError:
			#assert isinstance(resp, NotImplementedError)
			return True
		print('resp:' + str(resp))


if __name__ == '__main__':
	unittest.main()
