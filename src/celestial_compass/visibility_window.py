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

import numpy as np
from celestial_compass.observables import Observable, ObserverLLA
import datetime
import logging
        
class VisibilityWindow(object):
    def __init__(
        self,
        min_alt_rad: float=-np.pi/2.,
        max_alt_rad: float= np.pi/2.,
        min_az_rad:  float= 0.,
        max_az_rad:  float= 2*np.pi
    ):
        self.min_alt_rad = min_alt_rad
        self.max_alt_rad = max_alt_rad
        self.min_az_rad = min_az_rad
        self.max_az_rad = max_az_rad
        
    def is_visible(
        self,
        observable: Observable,
        observer=ObserverLLA,
        observing_time:datetime.datetime = datetime.datetime.now(datetime.timezone.utc),
        verbose:bool=False,
    ):
        _alt_rad, _az_rad, _ = observable.observe_topocentric(
            observer_lon_E_deg=observer.lon_rad*180./np.pi,
            observer_lat_N_deg=observer.lat_rad*180./np.pi,
            observer_h_m=observer.alt_m,
            observing_time=observing_time,
        )
        
        if _alt_rad >= self.min_alt_rad and _alt_rad <= self.max_alt_rad and _az_rad>=self.min_az_rad and _az_rad<=self.max_az_rad:
#             if verbose:
#                 print("{} is visible: alt {}, az {}".format(observable, _alt_rad, _az_rad))
            return True
        else:
            if verbose:
                logging.warning("{} is not visible: alt {}, az {}".format(observable, _alt_rad, _az_rad))
            return False
    
    
