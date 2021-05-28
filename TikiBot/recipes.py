from __future__ import division
import sys
import math
import time
import platform
import operator
import os
from feeds import SupplyFeed
import time
import re
from serial_connection import SerialConnection
import logging
import socket
hostname=socket.gethostname()
import importlib
try:
    hwc = __import__(hostname)
    hwconfig = hwc.hwconfig
    print("loading hostspecific config " + hostname)
except:
    hwc = __import__("hwconfig")
    hwconfig = hwc.hwconfig
    print("no hostspecific config found, loading default hwconfig")
try:
    import RPi.GPIO as GPIO
    test_environment = False
    from adafruit_servokit import ServoKit
    print("raspihardware found, modules imported")
except (ImportError, RuntimeError):
    test_environment = True




# Unit multipliers to convert to milliliters
GALLON = 3785.41
QUART = 946.35
FIFTH = 757.08
PINT = 473.17
CUP = 236.58
SHOT = 44.36
JIGGER = 44.36
PONY = 29.57
OUNCE = 29.57
OZ = 29.57
TBSP = 14.79
TSP = 4.93
SPLASH = 2.5
DASH = 0.92
MILLILITER = 1.0
CENTILITER = 10.0
DECILITER = 100.0
LITER = 1000.0
ML = 1.0
CL = 10.0
DL = 100.0
L = 1000.0


unit_measures = {
    "dash": DASH,
    "splash": SPLASH,
    "tsp": TSP,
    "tbsp": TBSP,
    "oz": OZ,
    "ounce": OUNCE,
    "pony": PONY,
    "jigger": JIGGER,
    "shot": SHOT,
    "cup": CUP,
    "pint": PINT,
    "fifth": FIFTH,
    "quart": QUART,
    "gallon": GALLON,
    "ml": ML,
    "cl": CL,
    "dl": DL,
    "l": L,
}


type_icons = {
    "Alkoholfrei": "AlkoholfreiDrinkIcon.gif",
    "Cocktails": "CocktailDrinkIcon.gif",
    "Longdrinks": "LongDrinkIcon.gif",
    "Fancy Drinks": "FancyDrinkIcon.gif",
    "Tropical Drinks": "TropicalDrinkIcon.gif",
    "Coladas": "ColadaDrinkIcon.gif",
    "Sour": "SourDrinkIcon.gif",
    "Extra Schuss": "ExtraSchussIcon.gif",
}


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class Ingredient(object):
    def __init__(self, feed, ml):
        self.feed = feed
        self.milliliters = ml

    @classmethod
    def fromArray(cls, data):
        if type(data) is dict:
            name = data['name']
            ml = data['ml']
        else:
            name, amount, unit = data
            mult = unit_measures.get(unit, 0.0)
            ml = amount * mult
        feed = SupplyFeed.getByName(name)
        return cls(feed, ml)

    def toArray(self, metric=True):
        val, unit = self.getBarUnits(metric=metric)
        return [self.feed.getName(), val, unit]

    def getName(self):
        return self.feed.getName()

    def getBarUnits(self, partial=1.0, metric=False):
        """
        Takes the volume of this ingredient, multiplies it by the arg `partial`,
        and returns a tuple `(val, units)` that is the number and name of units that
        best represents the volume in bartending units, or ml if `metric` is true.
        """
        ml = self.milliliters * partial
        unit, div = ("dash", DASH)
        if metric:
            unit, div = ("ml", ML)
        elif ml > 0.25 * OZ:
            unit, div = ("oz", OZ)
        elif ml > TBSP:
            unit, div = ("Tbsp", TBSP)
        elif ml > 2*DASH:
            unit, div = ("tsp", TSP)
        val = ml / div
        return (val, unit)

    def fractionalBarUnits(self, partial=1.0, metric=False):
        """
        Takes the volume of this ingredient, multiplies it by the arg `partial`,
        and returns a tuple `(wholenumber, fraction, units)` that represents the
        volume in imperial or metric units, depending on the arg `metric`.
        The `fraction` and `units` returned are strings, and the `wholenumber`
        is the number of fluid units (minus the fraction).  For metric units,
        the fraction will be an empty string "", and the `wholenumber` will
        actually be a floating point number of milliliters, with one decimal
        point.  For imperial units, `wholenumber` will be an integer, and the
        `fraction` will either be a null string "", or a string like "7/8"
        """
        val, unit = self.getBarUnits(partial, metric=metric)
        if metric:
            #return (math.floor(val*10+0.5)/10.0, "", unit)
            return (math.floor(val*10)/10.0, "", unit)
        whole = math.floor(val)
        frac = val - whole
        min_delta = 1
        found_numer = 0
        found_denom = 0
        for denom in [8, 6, 4, 3, 2]:
            numer = math.floor((frac * denom) + 0.5)
            delta = abs(frac - (numer/denom))
            if delta <= min_delta:
                min_delta = delta
                found_numer = numer
                found_denom = denom
        if found_numer >= found_denom:
            found_numer -= found_denom
            whole += 1
        frac = ""
        if found_numer > 0:
            frac = "%d/%d" % (found_numer, found_denom)
        return (whole, frac, unit)

    def readableDesc(self, partial=1.0, metric=True):
        whole, frac, unit = self.fractionalBarUnits(partial=partial, metric=metric)
        valstr = ""
        if whole > 0:
            valstr += "%.3g" % whole
        if frac:
            if valstr:
                valstr += " "
            valstr += frac
        if not valstr:
            valstr = "0"
        return "%s %s %s" % (valstr, unit, self.getName())

    def isFlowing(self):
        return self.feed.isFlowing()

    def startFeed(self):
        self.feed.startFeed()

    def stopFeed(self):
        self.feed.stopFeed()


class DispensingIngredient(Ingredient):
    def __init__(self, ingr, size_mult):
        new_vol = ingr.milliliters
        super(DispensingIngredient, self).__init__(ingr.feed, new_vol)
        self.dispensed = 0.0
        #self.remainingnew = ingr.feed.remaining - new_vol

    def done(self):
        return self.dispensed >= self.milliliters

    def percentDone(self):
        tempDone = math.ceil(100.0 * self.dispensed / self.milliliters)
        if tempDone > 100:
            tempDone = 100
        return tempDone

    def updateDispensed(self, secs):
        self.dispensed  = secs


class UnknownRecipeTypeError(Exception):
    pass


class Recipe(object):
    recipes = {}
    recipe_types = {}
    by_feed = {}

    def __init__(self, type_, name, ingredients, mixit, icon):
        global type_icons
        if type_ not in type_icons:
            raise UnknownRecipeTypeError()
        if type_ not in Recipe.recipe_types:
            Recipe.recipe_types[type_] = []
        Recipe.recipe_types[type_].append(self)
        self.type_ = type_
        self.name = name
        self.icon = icon
        self.mixit = mixit
        self.ingredients = []
        self.dispensing = []
        self.timeslice_secs = 1.0
        self.min_dispense_secs = 0.1
        self.last_timeslice = time.time()
        self.last_update_time = time.time()
        self.stepsforml = 136 # number of steps for 1 ml
        Recipe.recipes[name] = self
        for ingr_data in ingredients:
            ingr = Ingredient.fromArray(ingr_data)
            if ingr.feed not in Recipe.by_feed:
                Recipe.by_feed[ingr.feed] = []
            Recipe.by_feed[ingr.feed].append(self)
            self.ingredients.append(ingr)

    @classmethod
    def fromDict(cls, d):
        """Create new Recipe instances from a dictionary description."""
        global type_icons
        if 'type_icons' in type_icons:
            type_icons = d['type_icons']
        # Delete old Recipes
        for name, recipe in cls.recipes.items():
            recipe.delete_recipe()
        # Add Recipes from dict
        for name, data in d.get('recipes', {}).items():
            cls(
                data['type'],
                name,
                data['ingredients'],
                data['mixit'],
                icon=data.get('icon'),
            )

    @classmethod
    def toDictAll(cls, d, metric=True):
        """Create a dictionary description of all Recipe instances."""
        global type_icons
        d['recipes'] = {name: recipe.toDict(metric=metric) for name, recipe in cls.recipes.items()}
        d['type_icons'] = type_icons
        return d

    def toDict(self, metric=True):
        data = {
            'type': self.type_,
            'ingredients': [x.toArray(metric=metric) for x in self.ingredients],
            'mixit': self.mixit,
        }
        if self.icon:
            data['icon'] = self.icon
        return data

    @classmethod
    def getTypeNames(cls):
        return sorted(cls.recipe_types.keys())

    @staticmethod
    def getPossibleTypeNames():
        global type_icons
        return sorted(type_icons.keys())

    @classmethod
    def getTypeIcon(cls, name):
        global type_icons
        return type_icons[name]

    @classmethod
    def getRecipesByType(cls, name):
        recipe_list = cls.recipe_types[name]
        return sorted(recipe_list, key=operator.attrgetter('name'))

    @classmethod
    def getRecipesKeysByType(cls, name):
        recipe_list = cls.recipe_types[name]
        for key in sorted(cls.recipes.keys()):
            if cls.getByName(name=key)  in recipe_list:
                yield cls.recipes[key]

    @classmethod
    def getRecipesByFeed(cls, feed):
        if feed not in cls.by_feed:
            return []
        recipe_list = cls.by_feed[feed]
        return sorted(recipe_list, key=operator.attrgetter('name'))

    @classmethod
    def getNames(cls):
        return sorted(cls.recipes.keys())

    @classmethod
    def getAll(cls):
        for key in sorted(cls.recipes.keys()):
            yield cls.recipes[key]

    @classmethod
    def getByName(cls, name):
        return cls.recipes[name]

    def getName(self):
        return self.name

    def getType(self):
        return self.type_

    def getMixit(self):
        return self.mixit

    def getIcon(self):
        return self.icon

    def delete_recipe(self):
        del Recipe.recipes[self.name]
        Recipe.recipe_types[self.type_].remove(self)
        if not Recipe.recipe_types[self.type_]:
            del Recipe.recipe_types[self.type_]
        for ingr in self.ingredients:
            Recipe.by_feed[ingr.feed].remove(self)
            if not Recipe.by_feed[ingr.feed]:
                del Recipe.by_feed[ingr.feed]

    def rename(self, newname):
        del Recipe.recipes[self.name]
        self.name = newname
        Recipe.recipes[newname] = self

    def retype(self, newtype):
        global type_icons
        if newtype not in type_icons:
            raise UnknownRecipeTypeError()
        if newtype not in Recipe.recipe_types:
            Recipe.recipe_types[newtype] = []
        Recipe.recipe_types[self.type_].remove(self)
        if not Recipe.recipe_types[self.type_]:
            del Recipe.recipe_types[self.type_]
        self.type_ = newtype
        Recipe.recipe_types[newtype].append(self)

    def add_ingredient(self, feedname, ml):
        feed = SupplyFeed.getByName(feedname)
        if feed not in Recipe.by_feed:
            Recipe.by_feed[feed] = []
        Recipe.by_feed[feed].append(self)
        self.ingredients.append(Ingredient(feed, ml))
        return self

    def canMake(self):
        for ingr in self.ingredients:
            if not ingr.feed.avail or ingr.feed.remaining <= 0:
                return False
        return True

    def getAlcoholPercentByVolume(self):
        vol = 0.0
        alc_vol = 0.0
        for ingr in self.ingredients:
            ml = ingr.milliliters
            vol += ml
            alc_vol += ml * (ingr.feed.proof / 100.0)
        return 100.0 * alc_vol / vol

    def totalVolume(self):
        vol = 0.0
        for ingr in self.ingredients:
            vol += ingr.milliliters
        return vol
    
        
    def startDispensing(self, volume):
        stepsforml=self.stepsforml
        tot_vol = self.totalVolume()
        vol_mult = volume / tot_vol
        self.dispensing = []
        sercommand = ''
        self.dispenselist = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        logging.info("Dispensing: %s, %d ml" % (self.getName(), volume))
        for ingr in self.ingredients:
            ingr.milliliters = math.ceil(ingr.milliliters * vol_mult)
            self.dispensing.append(DispensingIngredient(ingr, vol_mult))
        for ingr in self.dispensing:
            thisfeed = SupplyFeed.getByName(ingr.feed.name)
            newremaining=thisfeed.feeds[ingr.feed.name].remaining - ingr.milliliters
            thisfeed.feeds[ingr.feed.name].remaining = newremaining
            logging.debug("remaining neu fuer " + ingr.feed.name + ": " + str(thisfeed.feeds[ingr.feed.name].remaining))
            logging.info("Zutat " + ingr.feed.name + ": " + str(ingr.milliliters) + " ml")
            for pumpnumber in list(range(24)):
                if ingr.feed.motor_num == pumpnumber:
                    self.dispenselist[pumpnumber] = int(math.ceil(ingr.milliliters * self.stepsforml))
        sercommand = (','.join(map(str, self.dispenselist))) + '\n'
        try:
            self.ser.readData()
        except:
            logging.debug("keine bestehende verbindung")
            try:
                self.ser = SerialConnection()
                self.ser.readData()
                logging.debug ("habe verbindung")
            except:
                logging.debug("verbindung nicht moeglich")
        hwa = HardwareAction(self.mixit)
        hwa.do_dispensing(self.mixit)
        self.ser.sendData(sercommand)
        self.ser.close()
        del self.ser
        self.updateDispensing(self.mixit)
        

    def updateDispensing(self, mixing=True):
        ml_left = []
        dispenselist = self.dispenselist
        self.ser = SerialConnection()
        ml_left = self.ser.readLine().split(",")
        logging.debug(str(ml_left[0]))
        if not "ok" in ml_left[0]:
            for ingr in self.dispensing:
                logging.debug(ingr.feed.name)
                for pumpnumber in list(range(24)):
                    if ingr.feed.motor_num == pumpnumber:
                        if "Ready" in ml_left[0]:
                            ingr.dispensed = 0
                        else:
                            logging.debug("pumpnumber ", str(pumpnumber))
                            if int(ml_left[pumpnumber]) < 0:
                                ml_left[pumpnumber] = 0
                            ingr.dispensed = math.ceil( (dispenselist[pumpnumber] - int(ml_left[pumpnumber])) / self.stepsforml)
        else:
            self.ser.close()
            del self.ser
            hwa = HardwareAction(self.mixit)
            hwa.end_dispensing(self.mixit)
            self.dispensing[:] = [x for x in self.dispensing if not x.done()]

    def cancelDispensing(self):
        self.ser = SerialConnection()
        self.ser.sendData('@')
        self.ser.readLine()
        self.ser.close()
        del self.ser
        logging.debug("Ausschenken abgebrochen")
        for ingr in self.dispensing:
            ingr.stopFeed()
        self.dispensing[:] = [x for x in self.dispensing if not x.done()]

    def doneDispensing(self):
        return not self.dispensing

class HardwareAction():
    def __init__(self, mixit):
        logging.debug("initialisiere Hardware")
        self.hwconfig = hwconfig
        self.mixit = mixit
        if mixit == True:
            logging.debug("mixing is configured")
        else:
            logging.debug("no mixing is configured")
        
        # setup servos (PCA9685)
        self.fingerChannel = hwconfig["pca9685"]["fingerchannel"]
        self.fingerPositions = hwconfig["pca9685"]["fingerpositions"]
        self.armChannel = hwconfig["pca9685"]["armchannel"]
        self.armPositions = hwconfig["pca9685"]["armpositions"]
        self.elevatorChannel = hwconfig["pca9685"]["elevatorchannel"]
        self.elevatorPositions = hwconfig["pca9685"]["elevatorpositions"]
        self.mixer = hwconfig["mixer"]["PIN"]
        self.light = hwconfig["light"]["PIN"]
        logging.debug("got all hardware parameters")
        
        if test_environment == False:
            logging.debug("no test environment, configure hardwrae")
            #GPIO.setmode(GPIO.BOARD)
            logging.debug("set mode tp gpio.board")
            GPIO.setup(self.mixer, GPIO.OUT)
            GPIO.setup(self.light, GPIO.OUT)
            logging.debug("configure Adafruit ServoKit")
            self.kit = ServoKit(channels=16)
        logging.debug("end of hardware initialization")

    def getConfig(self):
        return self.hwconfig

    def light_on(self):
        logging.debug("turn on light")
        if test_environment == False:
            GPIO.output(self.light, False)

    def light_off(self):
        logging.debug("turn off light")
        if test_environment == False:
            GPIO.output(self.light, True)

    def mixer_start(self):
        logging.debug("start mixer")
        if test_environment == False:
            GPIO.setup(self.mixer, False)

    def mixer_stop(self):
        logging.debug("stop mixer")
        if test_environment == False:
            GPIO.setup(self.mixer, True)

    def ping(self, num=3):
        logging.debug("klingeling")
        if test_environment == False:
            self.kit.servo[self.fingerChannel].angle=self.fingerPositions[0]
            self.kit.servo[self.fingerChannel].angle=self.fingerPositions[2]
            time.sleep(.25)
            for i in range(num-1):
                self.kit.servo[self.fingerChannel].angle=self.fingerPositions[1]
                time.sleep(.15)
                self.kit.servo[self.fingerChannel].angle=self.fingerPositions[2]
                time.sleep(.15)
            self.kit.servo[self.fingerChannel].angle=self.fingerPositions[0]
        
    def arm_dispense(self, dispense=0):
        if dispense == 0:
            logging.debug("moving arm to dispense position")
        else:
            logging.debug("moving arm to mix position")
        ch = self.armChannel
        pos = self.armPositions[1 - dispense]
        logging.debug("ch %d, pos %d" % (ch, pos))
        if test_environment == False:
            #self.kit.set_pwm(ch, 0, pos)
            self.kit.servo[ch].angle = pos

    def arm_mix(self):
        self.arm_dispense(dispense=1)
    
    def elevator_up(self, up=1):
        if up == 1:
            logging.debug("moving elevator to up position")
        else:
            logging.debug("moving elevator to down position")
        ch = self.elevatorChannel
        pos = self.elevatorPositions[1 - up]
        logging.debug("ch %d, pos %d" % (ch, pos))
        if test_environment == False:
            #self.kit.set_pwm(ch, 0, pos)
            self.kit.servo[ch].angle = pos

    def elevator_down(self):
        self.elevator_up(up=0)

    def do_dispensing(self, mixit):
        self.mixer_stop()
        self.light_on()
        time.sleep(.05)
        self.elevator_up()
        time.sleep(.3)
        self.arm_dispense()
        time.sleep(.3)
        return True

    def end_dispensing(self, mixit):
        if mixit == True:
            logging.debug("mixing is configured")
        else:
            logging.debug("no mixing is configured")
        self.mixer_stop()
        time.sleep(.1)
        self.elevator_up()
        time.sleep(.1)
        if mixit == True:
            self.arm_mix()
            time.sleep(1)
            self.elevator_down()
            time.sleep(.50)
            self.mixer_start()
            time.sleep(0.3)
            self.mixer_stop()
            time.sleep(0.6)
            self.mixer_start()
            time.sleep(.30)
            self.mixer_stop()
            time.sleep(0.6)
            self.mixer_start()
            time.sleep(0.3)
            self.mixer_stop()
            time.sleep(.80)
            self.elevator_up()
            time.sleep(1)
            self.arm_dispense()
            time.sleep(1)
            self.elevator_down()
            time.sleep(.5)
            self.mixer_start()
            time.sleep(0.3)
            self.mixer_stop()
            time.sleep(0.5)
            self.elevator_up()
        self.ping()
        time.sleep(1)
        self.light_off()
        return True
