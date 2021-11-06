"""
 Copyright 2021 by California Institute of Technology.  ALL RIGHTS RESERVED.
 United  States  Government  sponsorship  acknowledged.   Any commercial use
 must   be  negotiated  with  the  Office  of  Technology  Transfer  at  the
 California Institute of Technology.
 
 This software may be subject to  U.S. export control laws  and regulations.
 By accepting this document,  the user agrees to comply  with all applicable
 U.S. export laws and regulations.  User  has the responsibility  to  obtain
 export  licenses,  or  other  export  authority  as may be required  before
 exporting  such  information  to  foreign  countries or providing access to
 foreign persons.
 
 This  software  is a copy  and  may not be current.  The latest  version is
 maintained by and may be obtained from the Mobility  and  Robotics  Sytstem
 Section (347) at the Jet  Propulsion  Laboratory.   Suggestions and patches
 are welcome and should be sent to the software's maintainer.
 
"""

import RPi.GPIO as GPIO
import time, datetime
import numpy as np

class RGBManager(object):
    def __init__(self, R_LED: int=5, G_LED: int=19, B_LED: int=6, A_LED: int=13, anode_high: bool=False, voltage_scale: float=1.):
        GPIO.setmode(GPIO.BCM)
        self.R_LED = R_LED
        self.G_LED = G_LED
        self.B_LED = B_LED
        self.A_LED = A_LED
        self.anode_high = anode_high
        self.voltage_scale = voltage_scale
        
        self.RGB_pins = {"R": R_LED, "G": G_LED, "B": B_LED, "A": A_LED}
        self.RGB_PWM = {}
        for color, pin in self.RGB_pins.items():
            GPIO.setup(pin, GPIO.OUT)
            self.RGB_PWM[color] = GPIO.PWM(pin, 100)
            self.RGB_PWM[color].start(0)
            
    def __del__(self):
        for color, pin in self.RGB_pins.items():
            self.RGB_PWM[color].stop()
            
    def display_color(self, RGB_color: list=[1.,1.,1.]):
        if self.anode_high:
            self.RGB_PWM['R'].ChangeDutyCycle(self.voltage_scale*(100-RGB_color[0]*100))
            self.RGB_PWM['G'].ChangeDutyCycle(self.voltage_scale*(100-RGB_color[1]*100))
            self.RGB_PWM['B'].ChangeDutyCycle(self.voltage_scale*(100-RGB_color[2]*100))
            self.RGB_PWM['A'].ChangeDutyCycle(100)
        else:
            self.RGB_PWM['R'].ChangeDutyCycle(self.voltage_scale*(RGB_color[0]*100))
            self.RGB_PWM['G'].ChangeDutyCycle(self.voltage_scale*(RGB_color[1]*100))
            self.RGB_PWM['B'].ChangeDutyCycle(self.voltage_scale*(RGB_color[2]*100))
            self.RGB_PWM['A'].ChangeDutyCycle(0)
    def breathe_color(self, RGB_color: list=[1.,1.,1.], frequency_hz: float=.25, duration_s: float=10):
        start_time = datetime.datetime.now()
        current_time = datetime.datetime.now()
        time_elapsed = (current_time-start_time).total_seconds()
        while time_elapsed<duration_s:
            current_time = datetime.datetime.now()
            time_elapsed = (current_time-start_time).total_seconds()
            amplitude = (np.cos(time_elapsed*frequency_hz*2*np.pi)+1)/2
            self.display_color(np.array(RGB_color)*amplitude)
            time.sleep(0.05)