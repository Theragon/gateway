import sys


def get_caller():
	frame = sys._getframe()
	caller = frame.f_back.f_back.f_code.co_name
	return caller
