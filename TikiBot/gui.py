#!/usr/bin/env python3

try:  # Python 2
    from Tkinter import *  # noqa
except ImportError:  # Python 3
    from tkinter import *  # noqa

import os
import sys
from ruamel.yaml import YAML
import platform
from pkg_resources import resource_string

from feeds import SupplyFeed
from recipes import Recipe
from main_screen import MainScreen
#from led import LED
#from serial_connection import SerialConnection

import logging
# *** configure LOGGING here *** (INFO, DEBUG)
#logging.basicConfig(filename=(os.path.expanduser("~/tikibot.log")), level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d_%H:%M:%S')
logging.basicConfig(filename=(os.path.expanduser("~/tikibot.log")), level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d_%H:%M:%S')

def float_representer(dumper, value):
    text = '%.3f' % (value)
    while text[-1] == '0' and text[-2] != '.':
        text = text[:-1]
    return dumper.represent_scalar(u'tag:yaml.org,2002:float', text)

yaml = YAML()
#yaml.add_representer(float, float_representer)
class TikiBotGui(Tk):
    def __init__(self):
        super(TikiBotGui, self).__init__()
        try:
            import RPi.GPIO as GPIO
            self.test_environment = False
        except (ImportError, RuntimeError):
            self.test_environment = True
        self.passcode = "8888"
        self.use_metric = True
        self.stepsforml = "113"
        self.serdevice = "/dev/ttyUSB0"
        self.screen_stack = []
        self.image_cache = {}
        self.title("Let-Him-Mix")
        self.bgcolor = "#94F92F" # bg-color for all frames
        if self.test_environment == False:
            self.attributes("-fullscreen", True)
            self.protocol("WM_DELETE_WINDOW", lambda: false)
            self.option_add("*cursor", "none")
            self.option_add("*font", "Helvetica 22")
            self.option_add("*Text*font", "Helvetica 18")
            self.option_add("*Pour*Button*font", "Helvetica 18")
            self.option_add("*MainScreen*Button*font", "Helvetica 18")
            self.option_add("*TouchSpinner*font", "Helvetica 14")
            self.option_add("*Amount*TouchSpinner*Label*font", "Helvetica 20")
            self.option_add("*Button*background", "#FFFC74") # bg-color of buttons
            self.option_add("*Button*activeBackground", "#F6E70A") # bg-color of active buttons
            #self.neolight=LED()
            #self.neolight.start()
        else:
            self.geometry("1024x600")
            self.option_add("*font", "Helvetica 22")
            self.option_add("*Text*font", "Helvetica 18")
            self.option_add("*Pour*Button*font", "Helvetica 18")
            self.option_add("*MainScreen*Button*font", "Helvetica 18")
            self.option_add("*TouchSpinner*font", "Helvetica 14")
            self.option_add("*Amount*TouchSpinner*Label*font", "Helvetica 20")
            self.option_add("*Button*background", "#FFFC74")
            self.option_add("*Button*activeBackground", "#F6E70A")
        self.bind('<Key-Escape>', lambda evt: sys.exit(0))
        self.load_configs()
        self.screen_push(MainScreen(self))

    def set_passcode(self, newpass):
        self.passcode = newpass

    def load_configs(self):
        try:
            with open(os.path.expanduser("~/.tikibot.yaml"), "r") as f:
                confs = yaml.load(f)
        except FileNotFoundError:
            confs = yaml.load(self.get_resource("tikibot_configs.yaml"))
        self.passcode = confs.get('passcode', '8888')
        self.use_metric = confs.get('use_metric', True)
        self.stepsforml = confs.get('stepsforml', "113")
        self.serdevice = confs.get('serdevice', '/dev/ttyUSB0')
        self.bgcolor = confs.get('bgcolor', '#94F92F')
        SupplyFeed.fromDict(confs)
        Recipe.fromDict(confs)

    def save_configs(self):
        confs = {
            "conf_version": "1.0.0",
            "passcode": self.passcode,
            "use_metric": self.use_metric,
            "stepsforml": self.stepsforml,
            "serdevice": self.serdevice,
            "bgcolor": self.bgcolor,
        }
        confs = SupplyFeed.toDictAll(confs)
        confs = Recipe.toDictAll(confs, metric=self.use_metric)
        with open(os.path.expanduser("~/.tikibot.yaml"), "w") as f:
            yaml.dump(confs, f)
        
    def set_resource(self, name, data):
        with open(os.path.join("resources", name), "w") as f:
            f.write(data)

    def get_resource(self, name):
        with open(os.path.join("resources", name), "r") as f:
            return f.read()
        return None
        #return resource_string('TikiBotPy.resources', name)

    def get_image(self, imgname):
        if imgname in self.image_cache:
            return self.image_cache[imgname]
        if imgname:
            img = PhotoImage(file=os.path.join("resources", "images", imgname))
            #img = PhotoImage(data=resource_string('TikiBotPy.resources.images', imgname).encode('base64'))
        else:
            img = PhotoImage(width=1, height=1)
        self.image_cache[imgname] = img
        return img

    def screen_push(self, screen):
        if self.screen_stack:
            self.screen_stack[-1].forget()
        self.screen_stack.append(screen)
        screen.pack(side=LEFT, fill=BOTH, expand=1)
        self.after(10, self.update)

    def screen_pop(self):
        if self.screen_stack:
            self.screen_stack.pop().forget()
        if self.screen_stack:
            top = self.screen_stack[-1]
            top.pack(side=LEFT, fill=BOTH, expand=1)
            if callable(getattr(top, "activate", None)):
                top.activate()
        self.after(10, self.update)

    def screen_pop_to_top(self):
        if self.screen_stack:
            self.screen_stack.pop().forget()
        while len(self.screen_stack) > 1:
            self.screen_stack.pop()
        if self.screen_stack:
            self.screen_stack[-1].pack(side=LEFT, fill=BOTH, expand=1)
        self.after(10, self.update)


bot = TikiBotGui()
bot.mainloop()

