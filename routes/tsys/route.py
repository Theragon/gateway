from utils.decorators import timeit
from utils import stringutils as su
from utils import parseutils as pu
from tsysconstants import *
from client import Client
from parser import Parser
from collections import OrderedDict
from config import *
import xmltodict
import pprint


class Route():
	#acquirer specific logic goes here
	def __init__(self):
		self.authenticated = False
		self.client = Client(debug=False)
		self.parser = Parser()

		self.gen_key = None

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

	def get_auth_msg(self):
		auth_dict = OrderedDict()
		auth_factor = OrderedDict()

		auth_dict[SGREQ] = {}

		auth_factor['B2'] = zip
		auth_factor['B1'] = phone

		auth_dict[SGREQ]['A1'] = pos_id
		auth_dict[SGREQ]['A2'] = auth_code
		auth_dict[SGREQ]['A4'] = auth_factor
		auth_dict[SGREQ]['A10'] = '1'

		try:
			auth_xml = pu.dict_to_xml(auth_dict)
		except Exception as e:
			raise e

		return auth_xml

	def exchange_msg(self, msg):
		tsys_resp = self.client.exchange_msg(msg)

		xml_resp = self.extract_xml_from_msg(tsys_resp)

		dict_resp = pu.xml_to_dict(xml_resp)
		return dict_resp

	def do_authentication(self):
		authenticated = False
		auth_xml = self.get_auth_msg()
		print('do_auth xml: ' + auth_xml)

		auth_msg = self.parser.construct_msg(auth_xml)
		print('auth_msg: ' + auth_msg)

		#auth_resp = self.client.exchange_msg(auth_msg)
		auth_resp = self.exchange_msg(auth_msg)
		print('auth_resp:')
		pprint.pprint(auth_resp)

		if auth_resp[SGRSP]['A83'] == '100':
			print('AUTHENTICATION SUCCESSFUL')
			self.gen_key = auth_resp[SGRSP][A3]
			print('GEN KEY: ' + self.gen_key)
			authenticated = True

		return authenticated

	@timeit
	def do_payment(self, msg):
		#todo: validate payment_msg

		if not self.authenticated:
			print('do authentication')
			try:
				self.authenticated = self.do_authentication()
			except Exception as e:
				print('this should not happen')
				print('raise authentication exception')
				raise e

		print('payment logic')

		#todo: create tsys payment message
		payment_msg = self.parser.parse_dict_to_payment(msg, self.gen_key)

		#send payment to tsys and receive the response
		raw_response = self.client.exchange_msg(payment_msg)
		print('raw response: ' + raw_response)

		#extract the actual xml from the msg
		xml_msg = self.extract_xml_from_msg(raw_response)
		print('xml message: ' + xml_msg)

		#convert the xml to dictionary
		msg_dict = self.get_msg_dict(xml_msg)

		#create appropriate response for the gateway
		payment_response = self.create_payment_response(msg_dict)

		#return the response to the gateway
		return payment_response, payment_msg
