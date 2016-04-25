#!/usr/bin/env python
from gateway import GateWay
gw = GateWay()
try:
	gw.start()
finally:
	gw.exit()
