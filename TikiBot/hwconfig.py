# hardware configuration
# all pin numbers are corresponding to GPIO!
# this is the config for "charles"

hwconfig = {
    "pca9685": {
        "freq": 60,
        "armchannel": 0,
        "armpositions": (10,90), # mix, dispense
        "elevatorchannel": 1,
        "elevatorpositions": (175,5), # up, down
        "fingerchannel": 2,
        "fingerpositions": (165,100,70),  # retracted, above bell, bell
    },
    "light": {
        "PIN": 23,
    },
    "mixer": {
        "PIN": 24,
    },
    # currently not used
    "reset": {
        "PIN": 17,
    },
    # Neopixel-LEDs
    "neo": {
        "PIN": 10,
        "NUM": 109,
    },
}
