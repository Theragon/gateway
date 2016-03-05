#!/usr/bin/env python

# HTTP Headers
app_xml = 'application/xml'
text_xml = 'text/xml'
app_json = 'application/json'
app_yaml = 'application/x-yaml'
text_yaml = 'text/yaml'

APP_XML = {'Content-Type': app_xml, 'Accept': app_xml}
TEXT_XML = {'Content-Type': text_xml, 'Accept': text_xml}
APP_JSON = {'Content-Type': app_json, 'Accept': app_json}
APP_YAML = {'Content-Type': app_yaml, 'Accept': app_yaml}
TEXT_YAML = {'Content-Type': text_yaml, 'Accept': text_yaml}

# HTTP Methods
GET = 'GET'
PUT = 'PUT'
POST = 'POST'
DELETE = 'DELETE'


def contains_json(request):
	return request.headers['Content-Type'] == 'application/json'


def contains_xml(request):
	return request.headers['Content-Type'] == 'text/xml' \
		or request.headers['Content-Type'] == 'application/xml'


def is_json(mimetype):
	return mimetype == app_json


def is_xml(mimetype):
	return mimetype == text_xml or mimetype == app_xml


def is_yaml(mimetype):
	return mimetype == app_yaml or mimetype == text_yaml


class GatewayTimeoutException(Exception):
	"""docstring for GatewayTimeoutException"""
	def __init__(self, message=None):
		super(GatewayTimeoutException, self).__init__(message)
		self.status = 504
		if self.message is None:
			self.message = 'Gateway Timeout'
		self.msg = self.message
		self.rsp = (self.msg, self.status)
		self.response = self.rsp


class InternalServerError(Exception):
	"""docstring for InternalServerError"""
	def __init__(self, message=None):
		super(InternalServerError, self).__init__(message)
		self.status = 500
		if self.message is None:
			self.message = 'Internal Server Error'
		self.msg = self.message
		self.rsp = (self.msg, self.status)
		self.response = self.rsp


class BadRequestException(Exception):
	"""docstring for BadRequestException"""
	def __init__(self, message=None):
		super(BadRequestException, self).__init__(message)
		self.status = 400
		if self.message is None:
			self.message = 'Bad Request'
		self.msg = self.message
		self.rsp = (self.msg, self.status)
		self.response = self.rsp


class NotImplementedException(Exception):
	"""docstring for NotImplementedException"""
	def __init__(self, message=None):
		super(NotImplementedException, self).__init__(message)
		self.status = 501
		if self.message is None:
			self.message = 'Not Implemented'
		self.msg = self.message
		self.rsp = (self.msg, self.status)
		self.response = self.rsp


class NotFoundException(Exception):
	"""docstring for NotFoundException"""
	def __init__(self, message=None):
		super(NotImplementedException, self).__init__(message)
		self.status = 404
		if self.message is None:
			self.message = 'Not Found'
		self.msg = self.message
		self.rsp = (self.msg, self.status)
		self.response = self.rsp
