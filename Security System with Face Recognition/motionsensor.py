import RPi.GPIO as GPIO
import os
from time import sleep

GPIO.setmode(GPIO.BOARD)
pir = 8
GPIO.setup(pir,GPIO.IN)
sleep(2)

try:
    while True:
        if GPIO.input(pir) == True:
                print('Motion detected')
                sleep(10)
                

            
finally:
    GPIO.cleanup()
    