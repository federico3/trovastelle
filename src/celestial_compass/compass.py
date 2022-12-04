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

import luma.emulator.device

import matplotlib.colors as mcolors
import logging
import datetime
import numpy as np
import random
import asyncio

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
        display_controller: DisplayController=None,
        simulated_display: bool=False,
        simulated_led:bool=False,
        led_pins_rgba = (5, 6, 13, 19),
        led_anode_high = False,
        led_voltage_scale = 1.,
        led_colors: dict = None,
        calibration_level: int = 3,
    ):
        logging.info("Starting application")
        self.running = False
        self.controller = controller
        self.observer = observer
        self.observables = observables
        self.time_on_target_s = time_on_target_s
        self.target_list_length_s = target_list_length_s
        self.schedule = []
        self.check_visible = check_visible
        self.visibility_window = visibility_window
        self.calibration_level = calibration_level
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
        
        logging.info("Setting up RGB manager")
        self.simulated_led = simulated_led
        if self.simulated_led:
            self.led_manager = None
        else:
            self.led_manager = RGBManager(
                R_LED=led_pins_rgba[0],
                G_LED=led_pins_rgba[1],
                B_LED=led_pins_rgba[2],
                A_LED=led_pins_rgba[3],
                anode_high=led_anode_high,
                voltage_scale=led_voltage_scale,
            )
        
        logging.info("Creating schedule")
        self.update_schedule()
        
        if display_controller is None:
            logging.info("Setting up display controller")
            if simulated_display:
                device = luma.emulator.device.capture()
                self.display_controller = DisplayController(device=device)
                logging.info("Using simulated display in compass")
            else:
                self.display_controller = DisplayController()
                logging.info("Using real display in compass")
        else:
            self.display_controller = display_controller
            logging.info("Using externally-created display in compass")
        
        self.refresh_rate_hz = refresh_rate_hz
        logging.info("Ready to run")
        self.logged_observable_name = False
        self.running = True
        
        
    def calibrate(self):
        for _try in range(3):
            self.display_controller.display_calibration_data(self.controller.calibration_status)
            self.controller.calibrate(max_tries=1, report_status_function=self.display_controller.display_calibration_data, calibration_level=self.calibration_level)
        self.display_controller.display_calibration_data(self.controller.calibration_status)
        
    def update_observables(self, new_observables):
        self.observables = new_observables
        return True

    def update_schedule(self):
        logging.info("Updating schedule")
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
                    logging.info(_observable, "is not visible")
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
            logging.warning("Very little is visible right now!")

    async def run(self):
        main_task = asyncio.create_task(self._run_main())
        io_task = asyncio.create_task(self._run_listener())
        await main_task
        await io_task
    
    async def _run_listener(self):
        pass
        # """ This is where you put your sockets, etc. """
        # """ https://pyzmq.readthedocs.io/en/latest/api/zmq.asyncio.html """
        # context = zmq.asyncio.Context()
        # sock = context.socket(zmq.REP)
        # sock.bind("tcp://*:5556")
        # while True:
        #     msg = await sock.recv() # waits for msg to be ready
        #     # reply = await async_process(msg)
        #     reply = json.dumps("config").encode()
        #     await sock.send(reply)
        # # sock = self.zmq_context.socket(zmq.PULL)
        # # sock.bind(self.zmq_address)
        # # while self.running:
        # #     print("Still here!")
        # #     msg = await sock.recv_multipart()
        # #     print(msg)
        # #     reply = "OK"
        # #     await sock.send_multipart(reply)
        # #     # await asyncio.sleep(1./self.refresh_rate_hz)

    async def _run_main(self):
        while self.running:
            
            # Get initial pose of arrow
            logging.debug("Getting alt-az")
            self.controller.get_alt_az()
            
            # Clean up the schedule
            logging.debug("Calling schedule updater")
            self.update_schedule()
            
            # TODO Pulse LED appropriately
            logging.debug("Calling LED")
            color = self.schedule[0]['color_rgb']
            if not self.simulated_led:
                self.led_manager.breathe_color_async(color, frequency_hz=0.5, duration_s=self.time_on_target_s)

            self.logged_observable_name = False
            while len(self.schedule) and self.schedule[0]['end_time']>datetime.datetime.now(datetime.timezone.utc):
                observable = self.schedule[0]['observable']
                if self.logged_observable_name is False:
                    logging.info("Now displaying observable {}".format(observable.name))
                    self.logged_observable_name = True
                else:
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
                
                await asyncio.sleep(1./self.refresh_rate_hz)
                # time.sleep(1./self.refresh_rate_hz)
            # Stop breathing, will restart at next loop around
            if not self.simulated_led:
                self.led_manager._keep_breathing=False
