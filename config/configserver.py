#!/usr/bin/env python

from flask import Flask
import yaml
import sys

sys.path.append('/home/logi/repos/gateway')

from utils import parseutils as pu

app = Flask(__name__)


@app.route('/config/<module>', methods=['GET'])
def get_config(module):
	file_types = ['yaml', 'yml', 'cfg', 'txt']
	f = None
	for t in file_types:
		file_name = module + '.' + t
		try:
			print('trying ' + file_name)
			f = open(file_name)
			print('success')
			break
		except IOError:
			continue
	if f:
		config = yaml.safe_load(f)
		f.close()
		config_json = pu.dict_to_json(config)
		return (config_json, 200)
	else:
		return ('failed to load config for ' + str(module), 500)


if __name__ == '__main__':
	app.run(port=5001)
