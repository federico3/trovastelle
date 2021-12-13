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

from celestial_compass.visibility_window import VisibilityWindow
from celestial_compass.arrow_controller import ArrowController
from celestial_compass.observables import ObserverLLA#, Observable, ObservableTerrestrialLocation, ObservableSkyObject, ObservableSatellite, ObservableEphemSatellite
from celestial_compass.led_manager import RGBManager
from celestial_compass.display_manager import DisplayController, format_distance

import matplotlib.colors as mcolors
import logging
import datetime
import time
import numpy as np
import random

class CelestialCompass(object):
    def __init__(
        self,
        controller: ArrowController,
        observer: ObserverLLA,
        observables: list,
        time_on_target_s: float=300,
        target_list_length_s: float=7200,
        check_visible: bool = False,
        visibility_window: VisibilityWindow=VisibilityWindow(),
        refresh_rate_hz:float = 1.,
        simulated_display: bool=False,
        simulated_led:bool=False,
        simulated_motors:bool=False,
        led_pins_rgba = (5, 6, 13, 19),
        led_colors: dict = None,
    ):
        logging.debug("Starting application")
        self.running = False
        self.controller = controller
        self.observer = observer
        self.observables = observables
        self.time_on_target_s = time_on_target_s
        self.target_list_length_s = target_list_length_s
        self.schedule = []
        self.check_visible = check_visible
        self.visibility_window = visibility_window
        if led_colors is None:
            self.led_colors = {
                'Mellon': "xkcd:pale",
                'Messier': "xkcd:baby green",
                'Mission': "xkcd:light periwinkle",
                'Planet': "xkcd:pale mauve",
                'Satellite': "xkcd:magenta",
            }
        else:
            self.led_colors = led_colors
        
        logging.debug("Setting up RGB manager")
        self.led_manager = RGBManager(
            R_LED=led_pins_rgba[0],
            G_LED=led_pins_rgba[1],
            B_LED=led_pins_rgba[2],
            A_LED=led_pins_rgba[3],
        )
        
        logging.debug("Creating schedule")
        self.update_schedule()
        
        logging.debug("Setting up display controller")
        if simulated_display:
            device = luma.emulator.device.capture()
            self.display_controller = DisplayController(device=device)
        else:
            self.display_controller = DisplayController()
        
        self.refresh_rate_hz = refresh_rate_hz
        logging.debug("Ready to run")
        self.running = True
        
    def update_schedule(self):
        logging.debug("Updating schedule")
        current_time = datetime.datetime.now(datetime.timezone.utc)
        attempts_to_add = 0
        # Clean up the head
        while (len(self.schedule) > 0 and self.schedule[0]['end_time']<current_time):
            self.schedule = self.schedule[1:]
        # Add at the back
        while ((
            len(self.schedule) == 0 or 
            self.schedule[-1]['end_time']<current_time+datetime.timedelta(seconds=self.target_list_length_s))
        and attempts_to_add<50*(self.target_list_length_s/self.time_on_target_s)):
            attempts_to_add += 1
            _observable = random.choices(
                self.observables,
                weights = [obs.weight for obs in self.observables],
                k=1)[0]
            # If this is already in the list
            if _observable.name in [_s['observable'].name for _s in self.schedule]:
                continue
            if len(self.schedule):
                _schedule_end_time = self.schedule[-1]['end_time']
            else:
                _schedule_end_time = current_time
            if self.check_visible and _observable.check_visible:
                _visible_start = self.visibility_window.is_visible(_observable, self.observer, _schedule_end_time)
                _visible_end = self.visibility_window.is_visible(_observable, self.observer, _schedule_end_time+datetime.timedelta(seconds=self.time_on_target_s))
                if not _visible_start or not _visible_end:
                    print(_observable, "is not visible")
                    continue

            self.schedule.append(
                {
                    'start_time': _schedule_end_time,
                    'end_time': _schedule_end_time+datetime.timedelta(seconds=self.time_on_target_s),
                    'observable': _observable,
                    'color_rgb': mcolors.to_rgb(mcolors.XKCD_COLORS[self.led_colors.get(_observable.type_name,'xkcd:white')]),
                }
            )
        if attempts_to_add>=50*(self.target_list_length_s/self.time_on_target_s):
            warnings.warn("Very little is visible right now!")

    
    def run(self):
        while self.running:
            
            # Get initial pose of arrow
            logging.info("Getting alt-az")
            self.controller.get_alt_az()
            
            # Clean up the schedule
            logging.debug("Calling schedule updater")
            self.update_schedule()
            
            # TODO Pulse LED appropriately
            logging.debug("Calling LED")
            color = self.schedule[0]['color_rgb']
            self.led_manager.breathe_color_async(color, frequency_hz=0.5, duration_s=self.time_on_target_s)

            
            while len(self.schedule) and self.schedule[0]['end_time']>datetime.datetime.now(datetime.timezone.utc):
                observable = self.schedule[0]['observable']
                logging.debug("Now displaying observable {}".format(observable.name))
                # Get alt and az of celestial object
                
                t = datetime.datetime.now(datetime.timezone.utc)
                alt_radians, az_radians, distance = observable.observe_topocentric(
                    observer_lon_E_deg=self.observer.lon_rad*180./np.pi,
                    observer_lat_N_deg=self.observer.lat_rad*180./np.pi,
                    observer_h_m=self.observer.alt_m,
                    observing_time=t)
                logging.debug("Object cordinates:\nAlt {}\nAz {}".format(alt_radians, az_radians))
                # Command controller.slew_to_alt_az
                logging.debug("Slewing to target")
                self.controller.slew_to_alt_az(alt_radians, az_radians)
                
                # Update display
                logging.debug("Updating display")
                self.display_controller.display_observable_data(
                    observable_name=observable.name,
                    observable_type=observable.type_name,
                    observable_dist=format_distance(distance),
                    )
                
                time.sleep(1./self.refresh_rate_hz)
            self.led_manager._keep_breathing=False