from utils.decorators import timeit
from utils import stringutils as su
from utils import parseutils as pu
from tsysconstants import *
from client import Client
import collections
import xmltodict


class Route():
	#acquirer specific logic goes here
	def __init__(self):
		self.authenticated = False
		self.client = Client(debug=False)

		self.phone = '999999999'
		self.auth_code = 'WD03042015'
		self.pos_id = '800018160066091'
		self.zip = '999999'

	def extract_xml_from_msg(self, client_msg):
		#log.msg('parsing response: ' + client_msg)
		print('parsing response: ' + client_msg)
		try:
			stx = client_msg[0]
			print('stx: ' + stx)
			rec_format = client_msg[1]
			print('rec_format: ' + rec_format)
			app_type = client_msg[2]
			print('app_type: ' + app_type)
			delimeter = client_msg[3]
			print('delimeter: ' + delimeter)
			#route_id = client_msg[4:10]
			#print('route_id: ' + route_id)
			xml_msg = client_msg[4:-2]
			print('xml msg: ' + xml_msg)
			etx = client_msg[-2]
			print('etx: ' + etx)
			lrc = client_msg[-1]
			print('lrc: ' + lrc)

		except IndexError:
			raise Exception('String index out of range')

		return xml_msg

	def authenticate(self):
		auth_req = su.sanitize_msg(AUTH_REQ)
		auth_resp = self.client.exchange_msg(auth_req)
		#try:
		xml_msg = self.extract_xml_from_msg(auth_resp)
		#except Exception:
		#raise Exception('Invalid xml')

		try:
			msg_dict = xmltodict.parse(xml_msg)
			#log.msg(msg_dict)
		except Exception:
			raise Exception('Invalid xml')
		print(auth_resp)
		return auth_resp

	def get_msg_dict(self, msg):
		try:
			msg_dict = xmltodict.parse(msg)
		except Exception, e:
			raise e
		return msg_dict

	def create_payment_response(self, data):
		return data

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

	def get_auth_msg(self):
		auth_dict = collections.OrderedDict()
		auth_factor = collections.OrderedDict()

		auth_dict[SGREQ] = {}

		auth_factor['B2'] = self.zip
		auth_factor['B1'] = self.phone

		auth_dict[SGREQ]['A1'] = self.pos_id
		auth_dict[SGREQ]['A2'] = self.auth_code
		auth_dict[SGREQ]['A4'] = auth_factor
		auth_dict[SGREQ]['A10'] = '1'

		try:
			auth_xml = pu.dict_to_xml(auth_dict)
		except Exception as e:
			raise e

		return auth_xml

	def do_authentication(self):
		auth_xml = self.get_auth_msg()
		print('do_auth xml: ' + auth_xml)

		auth_msg = self.construct_msg(auth_xml)
		print('auth_msg: ' + auth_msg)

		auth_resp = self.client.exchange_msg(auth_msg)
		print('auth_resp: ' + auth_resp)

	@timeit
	def do_payment(self, msg):
		if not self.authenticated:
			print('do authentication')
			self.do_authentication()
		print('payment logic')
		"""try:
			return self.authenticate()
		except Exception, e:
			raise e"""
		raw_response = self.client.exchange_msg(msg)
		print('raw response: ' + raw_response)
		xml_msg = self.extract_xml_from_msg(raw_response)
		print('xml message: ' + xml_msg)
		msg_dict = self.get_msg_dict(xml_msg)

		payment_response = self.create_payment_response(msg_dict)

		#return self.client.exchange_msg(msg)
		return payment_response
