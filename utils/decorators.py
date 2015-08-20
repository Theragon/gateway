from time import time


def timeit(method):
	def timed(*args, **kw):
		print('STARTING TIMER')
		start = time()
		result = method(*args, **kw)
		end = time()
		delta = end - start

		if delta >= 1:
			print('%s function took %0.3f s' % (method.__name__, delta))
		else:
			print('%s function took %0.3f ms' % (method.__name__, (delta)*1000.0))
		return result
	return timed
