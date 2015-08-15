#!/usr/bin/env python

from socket import *
from ssl import *
import xmltodict
import sys

from baseclasses import RouteClient
from baseclasses import RouteParser
from utils import stringutils as su
from utils import funcutils as fu
from tsysconstants import *
from core.exceptions import *
#from exceptions import *
from config import *


class ClassName(object):
	"""docstring for ClassName"""
	def __init__(self, arg):
		super(ClassName, self).__init__()
		self.arg = arg


class Parser(RouteParser, object):
	def __init__(self):
		super(Parser, self).__init__()

	def parse(self, data):
		self.caller = fu.get_caller()
		print('caller: ' + self.caller)

		if self.is_payment():
			print('msg is payment')

		if self.is_refund():
			print('msg is refund')

		return su.sanitize_msg(SALE_APPROVED_RSP)


class Route():
	def __init__(self):
		self.authenticated = False
		self.client = Client()

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

	def do_payment(self, msg):
		print('payment logic')
		return self.authenticate()
		#return self.client.exchange_msg(msg)


class Client(RouteClient):
	def __init__(self, host=host, port=port, timeout=5):
		self.ready = False
		self.host = host
		self.port = port

		self.prot = PROTOCOL_TLSv1
		self.cert = CERT_NONE

		self.sock = self.create_socket()
		self.sock.settimeout(timeout)
		self.connect_to_host(self.sock)

		while not self.ready:
			self.ready = self.receive_enq()

	def create_socket(self):
		# print('creating socket')
		sock = socket(AF_INET, SOCK_STREAM)
		tls_socket = wrap_socket(sock, ssl_version=self.prot, cert_reqs=self.cert)

		return tls_socket

	def connect_to_host(self, sock):
		sock.connect((self.host, self.port))

	def receive(self):
		try:
			response = self.sock.recv(1024)
			return response.decode()
		except SSLError:
			raise SSLError

	def send(self, msg):
		msg_encoded = msg.encode()
		self.sock.send(msg_encoded)

	def receive_enq(self):
		return self.receive() == '\x05'

	def exchange_msg(self, request):
		self.send(request)
		try:
			response = self.receive()
			return response
		except SSLError:
			raise SSLError

	def close_connection(self):
		self.sock.shutdown(SHUT_RDWR)
		self.sock.close()
		# print('socket closed')

	"""def __del__(self):
		try:
			self.close_connection()
		except socket.error:
			pass"""

	def validate(self, msg):
		return True


def main2():
	host = sys.argv[1]
	to_send = int(sys.argv[2])

	client = TsysClient(host)

	all_msgs = get_all_messages()

	if client.ready:
		print('client is ready')
		resp = client.exchange_msg(all_msgs[to_send])
		if resp:
			print('response: ' + resp)
		client.close_connection()


def get_client():
	return Client()


#if __name__ == '__main__':
	#main2()
