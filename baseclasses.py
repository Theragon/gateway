class RouteClient():
	"""Some description that tells you it's abstract,
	often listing the methods you're expected to supply."""
	def exchange_msg(self):
		raise NotImplementedError("Should have implemented this")


class RouteParser():
	"""Some description that tells you it's abstract,
	often listing the methods you're expected to supply."""
	def __init__(self):
		self.caller = None

	def parse(self, data):
		raise NotImplementedError(
			"Class %s doesn't implement parse()" % (self.__class__.__name__))

	def is_payment(self):
		return self.caller == 'do_payment'

	def is_refund(self):
		return self.caller == 'do_refund'

	def do_some_shit(self):
		raise NotImplementedError(
			"Class %s doesn't implement do_some_shit()" % (self.__class__.__name__))
