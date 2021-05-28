import time
import logging
import board
import neopixel
import threading
import ctypes

class LED(threading.Thread): 
    def __init__(self): 
        threading.Thread.__init__(self) 
        self.Pin = board.D10
        self.Number = 54
        self.Modus = 'rainbow'
        self.ORDER = neopixel.GRB

    def run(self):
        if self.Modus == "rainbow":
            try:
                self.ledpixels = neopixel.NeoPixel(
                    self.Pin, self.Number, brightness=1.0, auto_write=False, pixel_order=self.ORDER
                )
                while True:
                    for j in range(255):
                        for i in range(self.Number):
                            self.pixel_index = (i * 256 // self.Number) + j
                            self.ledpixels[i] = self.neo_wheel(self.pixel_index & 255)
                        self.ledpixels.show()
                        time.sleep(0.0005)
                        #if stop_neoleds:
                        #    self.ledpixels.fill((0, 0, 0))
                        #    self.ledpixels.show()
                        #    return
            finally:
                #self.ledpixels.fill((0, 0, 0))
                #self.ledpixels.show()
                print("exception---end")


    def neo_wheel(self, pos):
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
        return (r, g, b) if self.ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


    def get_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
    def stop(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        self.ledpixels.fill((0, 0, 0))
        self.ledpixels.show()
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

