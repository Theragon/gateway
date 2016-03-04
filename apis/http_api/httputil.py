import requests
import json

timeout = None

req_headers = \
	{
		'Accept': 'application/json,application/octet-stream',
		'Content-Type': 'application/octet-stream'
	}

app_json = \
	{
		'Content-type': 'application/json',
		'Accept': 'application/json'
	}
txt_xml = {'Content-type': 'text/xml'}
app_xml = {'Content-type': 'application/xml'}
app_oct = {'Content-type': 'application/octet-stream'}


def post_req_json(url, data, to=timeout):
	"""
	Wrapper function to post json requests
	"""
	try:
		r = requests.post(url, data=json.dumps(data), headers=app_json, timeout=to)
		return r
	except requests.exceptions.Timeout as e:
		return e
	except ValueError as e:
		return e


def put_req_json(url, data, to=timeout):
	"""
	Wrapper function to put json requests
	"""
	try:
		r = requests.put(url, data=json.dumps(data), headers=app_json, timeout=to)
		return r
	except requests.exceptions.Timeout as e:
		return e
	except ValueError as e:
		return e


def post_req_xml(url, data, to=timeout):
	"""
	Wrapper function to post json requests
	"""
	try:
		r = requests.post(url, data=data, headers=app_xml, timeout=to)
		return r
	except requests.exceptions.Timeout as e:
		return e
	except ValueError as e:
		return e


def post_req_oct(url, data, to=timeout):
	"""
	Wrapper function to post json requests
	"""
	try:
		r = requests.post(url, data=data, headers=req_headers, timeout=to)
		return r
	except requests.exceptions.Timeout as e:
		return e
	except ValueError as e:
		return e
