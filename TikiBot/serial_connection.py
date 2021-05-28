import serial
import re
import logging


class SerialConnection():
    def __init__(self, device="/dev/ttyUSB0", timeout=2, write_timeout=2 ):
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        device = ports[0].device
        try:
            self.ser = serial.Serial(device, 115200, timeout=timeout, write_timeout=write_timeout)
        except:
            try:
                self.ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=timeout, write_timeout=write_timeout)
            except:
                logging.debug("serial connection not possible")
        
    def sendData(self, sercommand):
        #sercommand = sercommand + '\n'
        logging.debug('got command: ' + sercommand)
        #self.ser.write(bytes('\n',"ascii"))
        #self.readData()
        self.ser.write(bytes(sercommand,"ascii"))
                   
    def readData(self):
        while True:
            ser_out = (str(self.ser.readline().strip()))
            ser_out = re.sub(r'[b\';]', '', ser_out)
            logging.debug ("ser_out: " + ser_out)
            return(ser_out)
            if re.match('ok|ready|Ready' in str(ser_out)):
                break
            if not ser_out:
                break
        
                   
    def readLine(self):
        ser_line = (str(self.ser.readline().strip()))
        ser_line = re.sub(r'[b\';]', '', ser_line)
        logging.debug ("ser_line: " + ser_line)
        return(ser_line)
        
    def close(self):
        self.ser.close()

