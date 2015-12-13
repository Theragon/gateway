from voluptuous import Any, Schema, Required, Length, All, ALLOW_EXTRA
from voluptuous import MultipleInvalid
#import voluptuous
import logging
import sys


class ValidationError(MultipleInvalid):
	"""Exception to use when message fails validation"""

	def __init__(self, errors):
		super(ValidationError, self).__init__(errors)
		#MultipleInvalid.__init__(self, errors)

log = logging.getLogger(__name__)
h = logging.StreamHandler(sys.stdout)
log_format = \
	'%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s'
f = logging.Formatter(log_format)
h.setFormatter(f)
log.addHandler(h)
log.setLevel(logging.DEBUG)

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
	'transactionCounter': Any(unicode, str),
	#'accountType': Any(str, unicode),
	'paymentCode': All(unicode, Length(min=1, max=1)),
	'tipAmount': All(unicode, Length(min=1, max=1)),
	Required('route'): Any(unicode),
	#Required('www'): Any(str, unicode),
}

payment_schema = Schema({
	'payment': payment
}, extra=ALLOW_EXTRA)


def validate_payment(msg):
	result = True
	errors = None
	try:
		payment_schema(msg)
	except MultipleInvalid as e:
		errors = e.errors
		result = False
		raise ValidationError(e.errors)
	#is_valid = payment_schema(msg)
	log.debug('result: ' + str(result))
	return result, errors


class TsysValidator(object):
	"""docstring for TsysValidator"""
	def __init__(self):
		super(TsysValidator, self).__init__()

	def validate_payment(self, msg):
		is_valid = payment_schema(msg)
		return is_valid
