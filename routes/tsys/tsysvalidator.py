from voluptuous import Any, Schema, Required, Length, All, ALLOW_EXTRA
from voluptuous import MultipleInvalid
import logging
import sys


class ValidationError(MultipleInvalid):
	"""Exception to use when message fails validation"""

	def __init__(self, errors):
		super(ValidationError, self).__init__(errors)

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
	Required('track2Data'): Any(unicode),
	Required('f22'): Any(unicode),
	'serialNumber': Any(unicode),
	'terminalUserId': Any(unicode),
	'deviceType': Any(unicode),
	'terminalOsVersion': Any(unicode),
	'transactionCounter': Any(unicode, str),
	'accountType': Any(str, unicode),
	Required('paymentCode'): All(unicode, str, Length(min=1, max=1)),
	'tipAmount': All(unicode, str, Length(min=1, max=1)),
	Required('route'): Any(unicode),
}

payment_schema = Schema({
	'payment': payment
}, extra=ALLOW_EXTRA)


def validate_msg(msg):
	txn_type = msg.iterkeys().next()
	if txn_type == 'payment':
		return validate_payment(msg)


def validate_payment(msg):
	try:
		payment_schema(msg)
	except MultipleInvalid as e:
		raise ValidationError(e.errors)
