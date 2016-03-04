import binascii
import copy

from httputil import *

encrypt_url = 'http://10.1.100.56:1280/security/v1/dukpt/encrypt/'
decrypt_url = 'http://10.1.100.56:1280/security/v1/dukpt/decrypt/'

encrypt_req = \
	{
		"ksn": "ffff0000030100000001",
		"bdkIndex": 3,
		"blockCipherMode": "CBC",
		"plainText": None
	}

decrypt_req = \
	{
		"encryptedText": None
	}


def encrypt(text):
	msg = create_enc_msg(str(text))
	r = post_req_json(encrypt_url, msg)
	rsp = r.json()
	encryption_response = rsp['cipherText']

	chrs = [encryption_response[i:i+2] for i in range(0, len(encryption_response), 2)]

	bytes = []
	for c in chrs:
		x = int(c, 16)
		bytes.append(x)

	result = ''.join(map(chr, bytes))

	return result


def decrypt(text):
	msg = create_dec_msg(text)
	r = post_req_json(decrypt_url, msg)
	#print('decryption response:')
	#print(r.text)
	rsp = json.loads(r.text)
	data = rsp['plainText']

	text = ''.join(chr(int(data[i:i+2], 16)) for i in range(0, len(data), 2))
	#print('DECRYPTED TEXT:')
	#print(text)
	return text


def create_enc_msg(text):
	req = copy.deepcopy(encrypt_req)
	txt_bytes = string_to_bytearray(text)
	txt = bytes_to_hex(txt_bytes)
	req['plainText'] = txt.decode('utf-8')
	return req


def create_dec_msg(text):
	req = copy.deepcopy(decrypt_req)
	txt = bytes_to_hex(b''.join(text))
	req['encryptedText'] = txt.decode()
	return req


def string_to_bytearray(string, encoding='utf-8'):
	return bytearray(string, encoding)


def bytes_to_hex(bytes):
	return binascii.hexlify(bytes)
