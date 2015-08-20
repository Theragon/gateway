from voluptuous import Any, Schema, Required, Length, All, ALLOW_EXTRA
from baseclasses import RouteParser
from utils import stringutils as su
from utils import funcutils as fu
from tsysconstants import *

payment = {
	'cardAcceptorId': All(unicode, Length(min=1, max=10)),
	'paymentScenario': unicode,
	'softwareVersion': Any(unicode),
	'configVersion': Any(unicode),
	'terminalDateTime': Any(unicode),
	'nonce': Any(unicode),
	'authorizationGuid': Any(unicode),
	'currency': Any(unicode),
	'amount': Any(unicode),
	'customerReference': Any(unicode),
	'emvData': Any(unicode),
	Required('f22'): Any(unicode),
	'serialNumber': Any(unicode),
	'terminalUserId': Any(unicode),
	'deviceType': Any(unicode),
	'terminalOsVersion': Any(unicode),
	'transactionCounter': Any(unicode),
	#'accountType': Any(str, unicode),
	Required('route'): 'tsys',
	#Required('www'): Any(str, unicode),
}

payment_schema = Schema({
	'payment': payment
}, extra=ALLOW_EXTRA)


class Parser(RouteParser, object):
	def __init__(self):
		super(Parser, self).__init__()

	def validate_payment(self, msg):
		global payment_schema
		try:
			print('validating message')
			is_valid = payment_schema(msg)
			return is_valid
		except Exception, e:
			print('unable to validate message')
			print(e)
			raise e

	def parse_payment(self, data):
		self.caller = fu.get_caller()
		print('caller: ' + self.caller)

		if self.is_payment():
			print('msg is payment')
			try:
				self.validate_payment(data)
				print('payment passed validation')
			except Exception, e:
				#should create a specific ParseException
				raise e
			#todo: translate to tsys message
			#todo: make the payment happen

		if self.is_refund():
			print('msg is refund')

		return su.sanitize_msg(SALE_APPROVED_RSP)
