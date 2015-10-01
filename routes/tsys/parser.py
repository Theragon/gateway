from voluptuous import Any, Schema, Required, Length, All, ALLOW_EXTRA
from collections import OrderedDict
from baseclasses import RouteParser
from utils import stringutils as su
from utils import parseutils as pu
from utils import funcutils as fu
from tsysconstants import *
from config import *

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
	'track2Data': Any(unicode),
	Required('f22'): Any(unicode),
	'serialNumber': Any(unicode),
	'terminalUserId': Any(unicode),
	'deviceType': Any(unicode),
	'terminalOsVersion': Any(unicode),
	'transactionCounter': Any(unicode),
	#'accountType': Any(str, unicode),
	'paymentCode': All(unicode, Length(min=1, max=1)),
	'tipAmount': All(unicode, Length(min=1, max=1)),
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

	def calc_lrc(self, msg):
		lrc = 0

		for i in msg:
			lrc ^= ord(i)

		return lrc

	def construct_msg(self, msg):
		tmp_msg = REC_FORM + APP_TYPE + DELIM + ROUTE_ID + msg + ETX

		lrc = self.calc_lrc(tmp_msg)

		final_msg = STX + tmp_msg + chr(lrc)

		return final_msg

	def parse_dict_to_payment(self, payment_dict, gen_key):

		print('parsing payment dict to tsys payment msg')
		print(str(payment_dict))

		#pos_data_codes = payment_dict['payment']['f22']

		msg_unparsed = OrderedDict()
		msg_unparsed[SGREQ] = {}

		msg_unparsed[SGREQ]['A1'] = pos_id
		msg_unparsed[SGREQ]['A3'] = gen_key
		msg_unparsed[SGREQ]['A10'] = '10'
		msg_unparsed[SGREQ]['A12'] = payment_dict['payment']['paymentCode']
		msg_unparsed[SGREQ]['A15'] = payment_dict['payment']['amount']
		msg_unparsed[SGREQ]['A17'] = payment_dict['payment']['transactionCounter']

		msg_unparsed[SGREQ]['A21'] = {}
		msg_unparsed[SGREQ]['A21']['B1'] = '0'
		msg_unparsed[SGREQ]['A21']['B2'] = '1'
		msg_unparsed[SGREQ]['A21']['B3'] = 'C'
		msg_unparsed[SGREQ]['A21']['B4'] = '1'
		msg_unparsed[SGREQ]['A21']['B5'] = '1'
		msg_unparsed[SGREQ]['A21']['B6'] = '5'
		msg_unparsed[SGREQ]['A21']['B9'] = '1'
		msg_unparsed[SGREQ]['A21']['B13'] = '0'

		msg_unparsed[SGREQ]['A24'] = payment_dict['payment']['track2Data']
		msg_unparsed[SGREQ]['A41'] = developer_id
		msg_unparsed[SGREQ]['A42'] = version_id

		xml_msg = pu.dict_to_xml(msg_unparsed)
		print('xml_msg: ' + xml_msg)

		tsys_payment = self.construct_msg(xml_msg)
		print('tsys payment: ' + tsys_payment)

		return tsys_payment
