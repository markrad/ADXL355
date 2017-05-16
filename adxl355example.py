from time import sleep
from adxl355 import ADXL355, ADXL355Range

adxl = ADXL355()

if adxl.isRunning:
	adxl.end()
	
adxl.range = ADXL355Range.range2G

adxl.begin()

print "Current temperature is %fC" % (adxl.temperature)
print
print "Press Ctrl-C to exit"

try:
	while True:
		axes = adxl.axes
		print "x = %d\ty = %d\tz = %d" % (axes['x'], axes['y'], axes['z'])
		sleep(1.0)
except KeyboardInterrupt:
	# Assumes nothing external fiddles with this register
	print "Ctrl-C seen - exiting"
	adxl.end()
	
