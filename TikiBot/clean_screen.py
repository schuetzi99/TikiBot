try:  # Python 2
    from Tkinter import *  # noqa
except ImportError:  # Python 3
    from tkinter import *  # noqa

import time
from rectbutton import RectButton
from serial_connection import SerialConnection
import math
import logging


UPDATE_MS = 800
DISPLAY_MS = 120


class CleanScreen(Frame):
    def __init__(self, master, amount, turns, pumpcount=1):
        super(CleanScreen, self).__init__(master)
        self.master = master
        self.last_disp = 0.0
        self.pumpnumber = 0
        self.turn = 0
        self.amount = amount
        self.turns = turns
        self.pumpcount = pumpcount
        self.stopCleaning = False
        self.desc = Text(self, relief=FLAT, wrap=NONE, state=DISABLED)
        backbtn = RectButton(self, text="Abbruch", command=self.handle_button_back)
        self.bgcolor = master.bgcolor
        self.configure(bg=self.bgcolor)

        self.desc.grid(column=0, row=0, sticky=N+E+W+S)
        backbtn.grid(column=0, row=1, padx=10, pady=10, sticky=E+W+S)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        try:
            self.ser.readData()
        except:
            try:
                self.ser = SerialConnection()
                self.ser.readData()
            except:
                logging.debug("Verbindung nicht moeglich")
        self.next_Pump()

    def next_Pump(self):
        sercommand = ''
        self.pid = None
        self.dispenselist = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        for currentpump in range(self.pumpnumber, (self.pumpnumber + self.pumpcount)):
            if currentpump < 24:
                self.dispenselist[currentpump] = 136 * self.amount
        sercommand = (','.join(map(str, self.dispenselist))) + '\n'
        print(sercommand)
        self.pumpnumber += self.pumpcount - 1
        self.ser.sendData(sercommand)
        if self.pumpnumber >= 23:
            self.pumpnumber = 0
            self.turn += 1
        else:
            self.pumpnumber += + 1
        if self.turn >= self.turns:
            self.stopCleaning = True
            self.master.screen_pop_to_top()
        self.pid = self.after(UPDATE_MS, self.update_screen)
        
               
    def update_screen(self):
        self.pid = None
        if not self.stopCleaning:
            serout = ''
            serout=str(self.ser.readLine())
            if bool(re.search(r'ok', serout)):
                logging.debug("ok gefunden")
                self.next_Pump()
            else:
                try:
                    bool(re.search(r'\d+,\d+', serout))
                    ml_left = serout.split(",")
                    logging.debug("pumpnumber " + str(self.pumpnumber))
                    self.desc.config(state=NORMAL)
                    self.desc.delete(0.0, END)
                    self.desc.tag_config("header", background="#077", foreground="white")
                    self.desc.tag_config("pumpnumber", lmargin1=10, lmargin2=20)
                    self.desc.tag_config("left", foreground="#c44")
                    self.desc.insert(END, "Cleaning Pump: ", "header")
                    self.desc.insert(END, str(list(range((self.pumpnumber - self.pumpcount),self.pumpnumber))), "pumpnumber")
                    self.desc.insert(END, " left %.0f ml\n" % math.ceil(int(ml_left[self.pumpnumber - self.pumpcount]) / 136), 'left')
                    self.desc.config(state=DISABLED)
                except ValueError:
                    print("That's not an int!")
                self.master.update()
                self.pid = self.after(UPDATE_MS, self.update_screen)
            
        

    def handle_button_back(self):
        if self.pid != None:
            self.after_cancel(self.pid)
        self.turn = 5
        self.stopCleaning = True
        self.master.screen_pop()

    def hasNumbers(inputString):
        return any(char.isdigit() for char in inputString)

