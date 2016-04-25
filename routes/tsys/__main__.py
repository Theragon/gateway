#!/usr/bin/env python
from tsys import TsysRoute
tsys = TsysRoute()
try:
	tsys.start()
finally:
	tsys.stop()
