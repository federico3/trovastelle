"""
 Copyright (C) 2021 Federico Rossi (347N)
 
 This file is part of Trovastelle.
 
 Trovastelle is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 
 Trovastelle is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 
 You should have received a copy of the GNU General Public License
 along with Trovastelle.  If not, see <http://www.gnu.org/licenses/>.
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