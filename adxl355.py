import smbus

POWER_CTL           = 0x2D

POWER_CTL_OFF       = 0x01
POWER_CTL_ON        = ~POWER_CTL_OFF
POWER_CTL_DRDY_OFF  = 0x04
POWER_CTL_DRDY_ON   = ~POWER_CTL_DRDY_OFF
POWER_CTL_TEMP_OFF  = 0x02
POWER_CTL_TEMP_ON   = ~POWER_CTL_TEMP_OFF

RANGE               = 0x2C
RANGE_MASK          = 0x03
RANGE_2G            = 0b01
RANGE_4G            = 0b10
RANGE_8G            = 0b11



# Convenience class
class ADXL355Range:
    range2G = RANGE_2G
    range4G = RANGE_4G
    range8G = RANGE_8G
    
LOWPASS_FILTER      = 0x28
LOWPASS_FILTER_MASK = 0x0F
LOWPASS_FILTER_4000 = 0x0000
LOWPASS_FILTER_2000 = 0x0001
LOWPASS_FILTER_1000 = 0x0010
LOWPASS_FILTER_500  = 0x0011
LOWPASS_FILTER_250  = 0x0100
LOWPASS_FILTER_125  = 0x0101
LOWPASS_FILTER_62_5 = 0x0110
LOWPASS_FILTER_31_25    = 0x0111
LOWPASS_FILTER_15_625   = 0x1000
LOWPASS_FILTER_7_813    = 0x1001
LOWPASS_FILTER_3_906    = 0x1010

class ADXL355LowpassFilter:
    lowpassFilter_4000 = LOWPASS_FILTER_4000
    lowpassFilter_2000 = LOWPASS_FILTER_2000
    lowpassFilter_1000 = LOWPASS_FILTER_1000
    lowpassFilter_500 = LOWPASS_FILTER_500
    lowpassFilter_250 = LOWPASS_FILTER_250
    lowpassFilter_125 = LOWPASS_FILTER_125
    lowpassFilter_62_5 = LOWPASS_FILTER_62_5
    lowpassFilter_31_25 = LOWPASS_FILTER_31_25
    lowpassFilter_15_625 = LOWPASS_FILTER_15_625
    lowpassFilter_7_813 = LOWPASS_FILTER_7_813
    lowpassFilter_3_906 = LOWPASS_FILTER_3_906
    lowpassFilterValue = {
        lowpassFilter_4000: '4000',
        lowpassFilter_2000: '2000',
        lowpassFilter_1000: '1000',
        lowpassFilter_500: '500',
        lowpassFilter_250: '250',
        lowpassFilter_125: '125',
        lowpassFilter_62_5: '62.5',
        lowpassFilter_31_25: '31.25',
        lowpassFilter_15_625: '15.625',
        lowpassFilter_7_813: '7.813',
        lowpassFilter_3_906: '3.906'
    }


XDATA3              = 0x08
XDATA2              = 0x09
XDATA1              = 0x0A
YDATA3              = 0x0B
YDATA2              = 0x0C
YDATA3              = 0x0D
ZDATA1              = 0x0E
ZDATA2              = 0x0F
ZDATA3              = 0x10

TEMP2               = 0x06
TEMP1               = 0x07

TEMP_START          = TEMP2
TEMP_LENGTH         = 2

AXIS_START          = XDATA3
AXIS_LENGTH         = 9

STATUS              = 0x04
STATUS_MASK_DATARDY = 0x01
STATUS_MASK_NVMBUSY = 0x10

bus = smbus.SMBus(1)

class ADXL355:
    
    _devAddr = None
    
    def __init__(self, addr = 0x1d):
        self._devAddr = addr
        
    def begin(self):
        powerCtl = bus.read_byte_data(self._devAddr, POWER_CTL)

        if (powerCtl & POWER_CTL_OFF) == POWER_CTL_OFF:
            bus.write_byte_data(self._devAddr, POWER_CTL, (powerCtl & POWER_CTL_ON))
        
    def end(self):
        powerCtl = bus.read_byte_data(self._devAddr, POWER_CTL)

        if (powerCtl & POWER_CTL_OFF) != POWER_CTL_OFF:
            bus.write_byte_data(self._devAddr, POWER_CTL, powerCtl | POWER_CTL_OFF)
            
    def getLowpassFilter(self):
        return (bus.read_byte_data(self._devAddr, LOWPASS_FILTER)) & LOWPASS_FILTER_MASK
        
    def setLowpassFilter(self, newLowpassFilter):
        if type(newLowpassFilter) is not int:
            raise ValueError('newLowpassFilter must be an integer')
            
        if newLowpassFilter < LOWPASS_FILTER_3_906 or newLowpassFilter > LOWPASS_FILTER_4000:
            raise ValueError('newLowpassFilter is out of range')
            
        lowpassFilter = bus.read_byte_data(self._devAddr, LOWPASS_FILTER)
        lowpassFilter = (lowpassFilter & LOWPASS_FILTER_MASK) | newLowpassFilter
        bus.write_byte_data(self._devAddr, LOWPASS_FILTER, lowpassFilter)
        
    def getRange(self):
        return (bus.read_byte_data(self._devAddr, RANGE)) & RANGE_MASK
        
    def setRange(self, newRange):
        if type(newRange) is not int:
            raise ValueError('newRange must be an integer')
            
        if newRange < RANGE_2G or newRange > RANGE_8G:
            raise ValueError('newRange is out of range')
            
        range = bus.read_byte_data(self._devAddr, RANGE)
        range = (range & ~RANGE_MASK) | newRange
        bus.write_byte_data(self._devAddr, RANGE, range)
    
    range = property(getRange, setRange)
    
    def isRunning(self):
        powerCtl = bus.read_byte_data(self._devAddr, POWER_CTL)
        
        return (powerCtl & POWER_CTL_OFF) != POWER_CTL_OFF
        
    isRunning = property(isRunning)
            
    
    def getStatus(self):
        status = bus.read_byte_data(self._devAddr, STATUS)
        return status & STATUS_MASK_DATARDY
    
    status = property(getStatus)
    
    def getTemperature(self):
        tempBytes = bus.read_i2c_block_data(self._devAddr, TEMP_START, TEMP_LENGTH)
        temp = tempBytes[0] << 8 | tempBytes[1]
        temp = (1852 - temp) / 9.05 + 19.21
        return temp
        
    temperature = property(getTemperature)
    
    def getAxes(self):
        axisBytes = bus.read_i2c_block_data(0x1d, AXIS_START, AXIS_LENGTH)

        axisX = (axisBytes[0] << 16 | axisBytes[1] << 8 | axisBytes[2]) >> 4
        axisY = (axisBytes[3] << 16 | axisBytes[4] << 8 | axisBytes[5]) >> 4
        axisZ = (axisBytes[6] << 16 | axisBytes[7] << 8 | axisBytes[8]) >> 4

        if(axisX & (1 << 20 - 1)):
            axisX = axisX - (1 << 20)

        if(axisY & (1 << 20 - 1)):
            axisY = axisY - (1 << 20)

        if(axisZ & (1 << 20 - 1)):
            axisZ = axisZ - (1 << 20)

        return {'x': axisX, 'y': axisY, 'z': axisZ}
        
    axes = property(getAxes)
    
    def getAxisX(self):
        return self.axes['x']

    axisX = property(getAxisX)
    
    def getAxisY(self):
        return self.axes['y']

    axisY = property(getAxisY)
    
    def getAxisZ(self):
        return self.axes['z']

    axisZ = property(getAxisZ)
    
if __name__ == "__main__":
    adxl355 = ADXL355()
    
    print 'Set range to 4G'
    adxl355.range = ADXL355Range.range4G
    print "Range = %d" % adxl355.range
    print 'Set range to 2G'
    adxl355.range = ADXL355Range.range2G
    print "Range = %d" % adxl355.range
    
    print 'Set low pass filter to 62.5'
    adxl355.lowpassFilter = ADXL355LowpassFilter.lowpassFilter_62_5
    print 'Low pass filter = %d (%s)' % adxl355.lowpassFilter, ADXL355LowpassFilter.lowpassFilterValue[adxl355.lowpassFilter]
    
    print "Measuring? %r" % adxl355.isRunning
    print "Activate sensor"
    adxl355.begin()
    print "Measuring? %r" % adxl355.isRunning
    print "Status = %d" % adxl355.status
    print "Temperature = %dC" % adxl355.temperature
    allAxes = adxl355.axes
    print "All axes X: %d Y: %d Z: %d" % (allAxes['x'], allAxes['y'], allAxes['z'])
    print 'Axis X only: %d' % adxl355.axisX
    print 'Axis Y only: %d' % adxl355.axisY
    print 'Axis Z only: %d' % adxl355.axisZ
    print 'Deactivate sensor'
    adxl355.end()
    print "Measuring? %r" % adxl355.isRunning
