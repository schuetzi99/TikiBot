import time
from adafruit_servokit import ServoKit
 
# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
kit = ServoKit(channels=16)

kit.servo[0].angle = 100
time.sleep(1)
kit.servo[0].angle = 80
time.sleep(1)
kit.servo[0].angle = 100
time.sleep(3)
kit.servo[1].angle = 100
time.sleep(1)
kit.servo[1].angle = 80
time.sleep(1)
kit.servo[1].angle = 100
time.sleep(3)
kit.servo[2].angle = 100
time.sleep(1)
kit.servo[2].angle = 80
time.sleep(1)
kit.servo[2].angle = 100

