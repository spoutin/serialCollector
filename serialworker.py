import serial
import time
import multiprocessing

# Change this to match your local settings
SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_BAUDRATE = 115200


class SerialProcess(multiprocessing.Process):
 
    def __init__(self, input_queue, output_queue):
        multiprocessing.Process.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.sp = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)
 
    def close(self):
        self.sp.close()
 
    def write_serial(self, data):
        self.sp.write(data)
        # time.sleep(1)
        
    def read_serial(self):
        return self.sp.readline().replace("\n", "")
 
    def run(self):
        self.sp.flushInput()
        while True:
            try:
                self.loop()
            except KeyboardInterrupt:
                return

    def loop(self):
        time.sleep(.01)
        # look for incoming tornado request
        while not self.input_queue.empty():
            data = self.input_queue.get()
 
            # send it to the serial device
            self.write_serial(data)
            # print "writing to serial: " + data
 
        # look for incoming serial data
        if self.sp.inWaiting() > 0:
            data = self.read_serial()
            # print "reading from serial: " + data
            # send it back to tornado
            self.output_queue.put(data)
