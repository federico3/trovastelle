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

class sim_GPIO_pin(object):
    def __init__(self):
        pass
    def start(self, input):
        pass
    def stop(self):
        pass
    def ChangeDutyCycle(self,dutycycle):
        pass

class sim_GPIO(object):
    def __init__(self):
        self.BCM = None
        self.IN = 1
        self.OUT = 0
        pass
    def setmode(self, mode):
        pass
    def setup(self, pin, mode):
        pass
    def PWM(self,pin,dutycycle):
        return sim_GPIO_pin()
    def stop(self,):
        pass
    def cleanup(self,):
        return

import logging
try:
    import RPi.GPIO as GPIO
    BOARD_AVAILABLE=True
except (RuntimeError,ModuleNotFoundError) as e:
    logging.warning("Not on hardware!")
    GPIO = sim_GPIO()

import time, datetime
import numpy as np
import threading

class RGBManager(object):
    def __init__(self, R_LED: int=5, G_LED: int=19, B_LED: int=6, A_LED: int=13, anode_high: bool=False, voltage_scale: float=1.):
        GPIO.setmode(GPIO.BCM)
        self.R_LED = R_LED
        self.G_LED = G_LED
        self.B_LED = B_LED
        self.A_LED = A_LED
        self.anode_high = anode_high
        self.voltage_scale = voltage_scale
        self._keep_breathing = True
        
        self.RGB_pins = {"R": R_LED, "G": G_LED, "B": B_LED, "A": A_LED}
        self.RGB_PWM = {}
        for color, pin in self.RGB_pins.items():
            GPIO.setup(pin, GPIO.OUT)
            self.RGB_PWM[color] = GPIO.PWM(pin, 100)
            self.RGB_PWM[color].start(0)
            
    def __del__(self):
        for color, pin in self.RGB_pins.items():
            self.RGB_PWM[color].stop()
        GPIO.cleanup()
            
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
        self._keep_breathing = True
        start_time = datetime.datetime.now()
        current_time = datetime.datetime.now()
        time_elapsed = (current_time-start_time).total_seconds()
        while time_elapsed<duration_s and self._keep_breathing:
            current_time = datetime.datetime.now()
            time_elapsed = (current_time-start_time).total_seconds()
            amplitude = (np.cos(time_elapsed*frequency_hz*2*np.pi)+1)/2
            self.display_color(np.array(RGB_color)*amplitude)
            time.sleep(0.05)
            
    def breathe_color_async(self, RGB_color: list=[1.,1.,1.], frequency_hz: float=.25, duration_s: float=10):
        # Stop other threads who may be breathing
        if self._keep_breathing is True:
            self._keep_breathing=False 
            time.sleep(0.1)
            self._keep_breathing=True
        
        _thread = threading.Thread(target=self.breathe_color, args=(RGB_color,frequency_hz, duration_s))
        _thread.start()
        self._keep_breathing=False

if __name__ == "__main__":
    import os, json
    import zmq
    import itertools

    # logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    context = zmq.Context()
    server = context.socket(zmq.REP)
    server.bind("tcp://*:5555")

    DATA_PATH = os.environ.get("CELESTIAL_COMPASS_DATA")

    with open(os.path.join(DATA_PATH, 'config.json'), 'r') as config_file:
        config = json.load(config_file)

    RGBmgr = RGBManager(
        R_LED=config.get("led_pins",{}).get("red",5),
        G_LED=config.get("led_pins",{}).get("green",19),
        B_LED=config.get("led_pins",{}).get("blue",6),
        A_LED=config.get("led_pins",{}).get("alpha",13),
        anode_high=config.get("led_pins",{}).get("anode_high",False),
        voltage_scale=config.get("led_pins",{}).get("voltage_scale",1.),
    )

    for cycles in itertools.count():
        # Wait for a request in blocking fashion
        request = server.recv().decode()
        logging.debug(request)
        if len(request) == 1 and request[0] == 'Q':
            RGBmgr._keep_breathing=False
            reply = str("OK")+request
        elif request[0] == '[' and request[-1] == ']':
            _color = json.loads(request)
            RGBmgr.breathe_color_async(RGB_color=_color, frequency_hz=.25, duration_s=600)
            reply = str("OK")+request
        else:
            logging.warn("Request {} (length {}) is malformed!".format(request,len(request)))

            reply = str('')
        server.send(reply.encode())
    # Listen to MQTT socket on a loop
    # Whenever we get a new color message
    #   RGBmgr.breathe_color_async(RGB_color=[1.,1.,1.], frequency_hz=.25, duration_s=10)
    # If we get a "stop display" message
    #   RGBmgr._keep_breathing=False
