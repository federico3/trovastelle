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

from celestial_compass.observables import ObserverLLA
import numpy as np
import time
BOARD_AVAILABLE=False
try:
    import board
    import adafruit_bno055    
    BOARD_AVAILABLE=True
except NotImplementedError as e:
    warnings.warn("Not on hardware!")
    board = None

import logging
from adafruit_motorkit import MotorKit

from adafruit_motor import stepper

import geomag
import math

class sim9dof(object):
    def __init__(self, euler: list=(0,0,0)):
        self.euler = euler
        
class simstepper(object):
    def __init__(self):
        self._step = 0
    def onestep(
        self,
        direction,
        style,
    ):
        self._step += 1*direction
        return self._step

class ArrowController(object):
    """
    """
    def __init__(
        self,
        steps_per_turn_alt:int=2052,
        steps_per_turn_az:int=200,
        observer:ObserverLLA=ObserverLLA(
            lat_rad=45.*np.pi/180.,
            lon_rad=8.*np.pi/180.
        ),
        simulate_motors: bool=False,
        simulate_9dof: bool=False
    ):
        self.alt_rad = None
        self.az_rad = None
        self.steps_per_turn_alt = steps_per_turn_alt
        self.steps_per_turn_az = steps_per_turn_az
        self.observer = observer
        
        if simulate_9dof:
            self.bno055 = sim9dof()
        else:
            i2c = board.I2C()
            self.bno055 = adafruit_bno055.BNO055_I2C(i2c)
        
        if simulate_motors:
            self.stepper_alt = simstepper()
            self.stepper_az = simstepper()
        else:
            self.motorkit = MotorKit()
            self.stepper_alt = self.motorkit.stepper1
            self.stepper_az = self.motorkit.stepper2
        
        self.style_alt = stepper.SINGLE
        self.style_az = stepper.MICROSTEP
        
    def __del__(self):
        try:
            self.stepper_alt.release()
        except:
            logging.error("Could not release alt stepper on exit!")
        try:
            self.stepper_az.release()
        except:
            logging.error("Could not release ax stepper on exit!")
        
    def get_alt_az(self):
        _euler_angles = self.bno055.euler
        # We believe the Euler angles are Z, Y, X, with Z up and Y
        # The order of the Euler angles is RPY. P is alt, Y is az. ???
        # Also note that this is problematic if the base is tilted
        _alt_rad_raw = _euler_angles[1]*np.pi/180.
        _az_rad_raw = _euler_angles[2]*np.pi/180.
        # TODO check that the numbers are sane! Sometimes this returns numbers outside of 0-360
        # TODO correct for magnetic anomaly with 
        # https://pypi.org/project/geomag/
        # Lat in degrees
        # Lon in degrees
        # El in FEET
        geo_declination = geomag.declination(
            dlat=self.observer.lat_rad*180./np.pi,
            dlon=self.observer.lon_rad*180./np.pi,
            h=self.observer.alt_m/0.3048
        )
        # mag heading = real heading - decli
        _az_rad_magnetic = _az_rad_raw + geo_declination*np.pi/180.
        # Normalize to selected range
        # Alt: between -pi and pi. If it is outside of -pi/2, pi/2, we are in trouble
        _alt_rad = (math.fmod(_alt_rad_raw+np.pi,2*np.pi)-np.pi)
        if (_alt_rad>np.pi/2.) or (_alt_rad<-np.pi/2.):
            warnings.warn("WARNING: altitude {} is outside of {}-{} range".format(
            _alt_rad,-np.pi/2,np.pi/2))
        # Az: between -pi and pi
        _az_rad = (math.fmod(_az_rad_magnetic+np.pi,2*np.pi)-np.pi)
        
        self.alt_rad = _alt_rad
        self.az_rad  = _az_rad
        
        return self.alt_rad, self.az_rad
        
    def slew_to_alt_az(self, _alt_rad, _az_rad):
        if (_alt_rad>np.pi/2.) or (_alt_rad<-np.pi/2.):
            raise ValueError(
                "The commanded altitude should be between pi/2 and -pi/2. Commanded altitude: {}".
                format(_alt_rad)
            ) 
        delta_az_rad = (_az_rad-self.az_rad)
        delta_alt_rad = (_alt_rad-self.alt_rad)
        # Normalize rotations
        # OK to turn up to 180 degrees in alt, the important thing is that the TARGET altitude is in -180 to 180.
#         while delta_alt_rad>np.pi/2:
#             delta_alt_rad -= np.pi/2
#         while delta_alt_rad<-np.pi/2:
#             delta_alt_rad += np.pi/2
        # Never turn more than 180 degrees in az
        while delta_az_rad>np.pi:
            delta_az_rad -= np.pi
        while delta_az_rad<-np.pi:
            delta_az_rad += np.pi
        
        steps_alt = (_alt_rad-self.alt_rad)*self.steps_per_turn_alt/(2*np.pi)
        steps_az = (_az_rad-self.az_rad)*self.steps_per_turn_az/(2*np.pi)
        if steps_alt>0:
            direction_alt = stepper.FORWARD
            direction_sign_alt = 1
        else:
            direction_alt = stepper.BACKWARD
            direction_sign_alt = -1
        if steps_az>0:
            direction_az = stepper.FORWARD
            direction_sign_az = 1
        else:
            direction_az = stepper.BACKWARD
            direction_sign_az = -1
            
        # SINGLE, DOUBLE, INTERLEAVE, MICROSTEP

        
        for _s in range(int(round(direction_sign_alt*steps_alt))):
            # Command
            self.stepper_alt.onestep(direction=direction_alt, style=self.style_alt)
            # Update open-loop location
            self.alt_rad += direction_sign_alt*2*np.pi/self.steps_per_turn_alt
            # Normalize alt: between -pi/2 and pi/2
            self.alt_rad = (math.fmod(self.alt_rad+np.pi,2*np.pi)-np.pi)
            
        for _s in range(int(round(direction_sign_az*steps_az))):
            # Command
            self.stepper_az.onestep(direction=direction_az, style=self.style_az)
            # Update open-loop location
            self.az_rad += direction_sign_az*2*np.pi/self.steps_per_turn_az
            # Normalize az: between -pi and pi
            self.az_rad = (math.fmod(self.az_rad+np.pi/2.,np.pi)-np.pi/2.)