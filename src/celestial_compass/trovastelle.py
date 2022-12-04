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


from turtle import color
from celestial_compass.display_manager import DisplayController, round_number_to_fixed_width, format_distance, test_distance_format
from celestial_compass.visibility_window import VisibilityWindow
import matplotlib.colors as mcolors
from celestial_compass.arrow_controller import ArrowController, sim9dof, simstepper 
import logging


from celestial_compass.compass import CelestialCompass
from celestial_compass.observables import ObserverLLA

import numpy as np
import os, json
import asyncio
import zmq
import zmq.asyncio
from geojson import Feature, Point, LineString


def get_observables(
    satellites: bool=True,
    missions: bool=True,
    planets: bool=True,
    smallbodies: bool=False,
    mellyn: bool=True,
    messiers: bool=True,
):
    # Observables config
    SPICEYPY_AVAILABLE = False
    try:
        import spiceypy as spice
        SPICEYPY_AVAILABLE = True
    except:
        logging.warning("Spiceypy is not available!")

    from celestial_compass.data.satellites import ObservableSatellites
    if SPICEYPY_AVAILABLE:
        from celestial_compass.data.missions import ObservableMissions
    else:
        from celestial_compass.data.missions_base import ObservableMissions
    from celestial_compass.data.planets import ObservablePlanets
    from celestial_compass.data.small_bodies import ObservableSmallBodies
    from celestial_compass.data.mellyn import ObservableMellyn    
    from celestial_compass.data.messier import ObservableMessiers

    Observables = []
    if config.get("observables",{}).get("satellites",True):
        Observables += ObservableSatellites
    if config.get("observables",{}).get("missions",True):
        Observables += ObservableMissions
    if config.get("observables",{}).get("planets",True):
        Observables += ObservablePlanets
    if config.get("observables",{}).get("smallbodies",False):
        Observables += ObservableSmallBodies
    if config.get("observables",{}).get("mellyn",True):
        Observables += ObservableMellyn
    if config.get("observables",{}).get("messiers",True):
        Observables += ObservableMessiers
    
    return Observables

class trovastelle(object):
    def __init__(self, config, color_schema, store_config=lambda x: None):
    # LED config
        self.config = config
        self.color_schema = color_schema
        logging.debug("Configuring LEDs")
        R_LED = config.get("led_pins",{}).get("red",5)
        G_LED = config.get("led_pins",{}).get("green",6)
        B_LED = config.get("led_pins",{}).get("blue",13)
        A_LED = config.get("led_pins",{}).get("alpha",19)
        led_anode_high = config.get("led_pins",{}).get("anode_high", False)
        led_voltage_scale = config.get("led_pins",{}).get("voltage_scale", 1.)

        self.store_config = store_config

        self.strong_colors_by_type = {
            'Mellon': "xkcd:hot green",
            'Messier': "xkcd:bright orange",
            'Mission': "xkcd:bright red",
            'Planet': "xkcd:true blue",
            'Satellite': "xkcd:very light purple",
        }

        # pale_colors_by_type = {
        #     'Mellon': "xkcd:pale",
        #     'Messier': "xkcd:baby green",
        #     'Mission': "xkcd:light periwinkle",
        #     'Planet': "xkcd:pale mauve",
        #     'Satellite': "xkcd:magenta",
        # }

        logging.debug("Configuring display")
        simulated_display = config.get("simulated",{}).get("display",False)
        if simulated_display:
            import luma.emulator.device
            device = luma.emulator.device.capture()
            display_controller = DisplayController(device=device)
            logging.info("Using simulated display in trovastelle")
        else:
            display_controller = DisplayController()
            logging.info("Using real display in trovastelle")
        display_controller.display_fullscreen_text("Trovastelle")


        logging.debug("Configuring observables")
        Observables = get_observables(
            satellites  = config.get("observables",{}).get("satellites",True),
            missions    = config.get("observables",{}).get("missions",True),
            planets     = config.get("observables",{}).get("planets",True),
            smallbodies = config.get("observables",{}).get("smallbodies",False),
            mellyn      = config.get("observables",{}).get("mellyn",True),
            messiers    = config.get("observables",{}).get("messiers",True),
        )

        logging.debug("Configuring observer")
        # Observer: Marzia
        # _observer = ObservableMellyn[4]

        observer = ObserverLLA(
            lat_rad = config.get("observer",{}).get("lat_deg_N", 34.1376481)*np.pi/180.,
            lon_rad = config.get("observer",{}).get("lon_deg_E",-118.138686)*np.pi/180.,
            alt_m   = config.get("observer",{}).get("alt_m", 204.),
        )

        logging.debug("Configuring arrow controller")
        # Arrow controller
        ac = ArrowController(
            simulate_motors=config.get("simulated",{}).get("motors",False),
            simulate_9dof=config.get("simulated",{}).get("9dof",False),
            steps_per_turn_alt=config.get("steppers",{}).get("steps_per_turn_alt",2052),
            steps_per_turn_az=config.get("steppers",{}).get("steps_per_turn_az",int(200*16/6)),
            az_offset_rad=-np.pi/2, # HORRIBLE HACK! But works on Federico's desk, and YOLO
            alt_direction_up = config.get("steppers",{}).get("alt_direction_up", 2) , # 1 is forward, 2 is backwards
            az_direction_cw = config.get("steppers",{}).get("az_direction_cw", 2) ,
        )

        logging.debug("Configuring Trovastelle")
        # Full controller
        self.cc = CelestialCompass(
                controller= ac,
                observer = observer,
                observables = Observables,
                time_on_target_s = config.get("observables_list",{}).get("time_on_target_s",150.),
                target_list_length_s = config.get("observables_list",{}).get("target_list_length_s",600.),
                check_visible= config.get("observables_list",{}).get("check_visible",False),
                visibility_window = VisibilityWindow(
                    min_alt_rad= config.get("observables_list",{}).get("visibility_window",{}).get("min_alt_rad",-np.pi/2.),
                    max_alt_rad= config.get("observables_list",{}).get("visibility_window",{}).get("max_alt_rad", np.pi/2.),
                    min_az_rad = config.get("observables_list",{}).get("visibility_window",{}).get("min_az_rad",  0.),
                    max_az_rad = config.get("observables_list",{}).get("visibility_window",{}).get("max_az_rad",2*np.pi),
                ),
                refresh_rate_hz=config.get("observables_list",{}).get("refresh_rate_hz",1.),
                display_controller=display_controller,
                simulated_display=config.get("simulated",{}).get("display",False),
                simulated_led=config.get("simulated",{}).get("led",False),
                led_pins_rgba = (R_LED, G_LED, B_LED, A_LED),
                led_anode_high = led_anode_high,
                led_voltage_scale = led_voltage_scale,
                led_colors=color_schema.get(config.get("led_color_scheme","strong"), self.strong_colors_by_type),
                calibration_level=config.get("calibration_level",3),
            )
    def calibrate(self):
        logging.info("Calibrating! Trovastelle")
    
        self.cc.calibrate()

    async def listen(self):
        """ This is where you put your sockets, etc. """
        """ https://pyzmq.readthedocs.io/en/latest/api/zmq.asyncio.html """
        context = zmq.asyncio.Context()
        sock = context.socket(zmq.REP)
        sock.bind("tcp://*:5556")
        while True:
            msg = await sock.recv() # waits for msg to be ready
            req = msg.decode()
            if len(req) == 2 and req[:2] == "GC":
                logging.debug("Received request for config")
                reply = json.dumps(self.config)

            elif len(req) == 2 and req[:2] == "GA":
                logging.debug("Received request for calibration status")
                reply = json.dumps(self.cc.controller.calibration_status)
            
            elif len(req) == 2 and req[:2] == "GO":
                logging.debug("Received request for observer location status")
                reply = json.dumps({"lat_deg_N": self.cc.observer.lat_rad*180./np.pi, "lon_deg_E": self.cc.observer.lon_rad*180./np.pi, "alt_m": self.cc.observer.alt_m})
            
            elif len(req) == 2 and req[:2] == "GL":
                logging.debug("Received request for list")
                _schedule_json = []
                for scheduled_ix, scheduled in enumerate(self.cc.schedule):
                    _ra_radians_start, _dec_radians_start, _distance = scheduled['observable'].observe_topocentric_ra_dec(
                        observer_lon_E_deg=self.cc.observer.lon_rad*180./np.pi,
                        observer_lat_N_deg=self.cc.observer.lat_rad*180./np.pi,
                        observer_h_m=self.cc.observer.alt_m,
                        observing_time=scheduled['start_time']
                        )
                    _ra_radians_end, _dec_radians_end, _distance = scheduled['observable'].observe_topocentric_ra_dec(
                        observer_lon_E_deg=self.cc.observer.lon_rad*180./np.pi,
                        observer_lat_N_deg=self.cc.observer.lat_rad*180./np.pi,
                        observer_h_m=self.cc.observer.alt_m,
                        observing_time=scheduled['end_time']
                        )
                    # if (_ra_radians_start==_ra_radians_end and _dec_radians_start==_dec_radians_end):
                    if True:
                        _geometry = Point((
                                _ra_radians_start*180/np.pi,
                                _dec_radians_start*180/np.pi
                            ))
                    else:
                        _geometry = LineString([
                            (_ra_radians_start*180/np.pi,_dec_radians_start*180/np.pi),
                            (_ra_radians_end*180/np.pi,  _dec_radians_end*180/np.pi)
                            ])
                    _schedule_json.append(
                        Feature(
                            properties={
                                "name": scheduled['observable'].name,
                                "type": scheduled['observable'].type_name,
                                "order": scheduled_ix, 
                                "start_time": scheduled['start_time'].strftime("%m/%d/%Y, %H:%M:%S"),
                                "end_time": scheduled['end_time'].strftime("%m/%d/%Y, %H:%M:%S"),
                                "color_rgb": scheduled['color_rgb']
                            },
                            geometry= _geometry
                        )
                    )

                reply = json.dumps({"type":"FeatureCollection","features": _schedule_json})
            
            elif len(req) == 2 and req[:2] == "GP":
                logging.debug("Received request for pointer location")
                _alt_rad, _az_rad = self.cc.controller.get_alt_az()
                reply = json.dumps({"alt_rad": _alt_rad, "az_rad": _az_rad})

            elif len(req) >=2 and req[:2] == "SC":
                _config = json.loads(req[2:])
                logging.info("Processing new dictionary!")
                # print(_config)
                # Dynamic update behavior:
                # - Update observer: update cc.observer, set cc.schedule = [], call cc.update_schedule()
                # - Update observables: set cc.schedule = [], call cc.update_schedule()
                # - Update LED pins: requires application reboot
                # - Update LED color scheme: set cc.schedule = [], call cc.update_schedule() (or we could just update the colors one by one)
                # - Update stepper settings: requires application reboot
                # - Update observables_list parameters: 
                #   - update cc.time_on_target_s | target_list_length_s | check_visible | visibility_window,  set cc.schedule = [], call cc.update_schedule()
                #   - update cc.refresh_rate_hz and continue running with existing
                # - Update simulated: requires application reboot
                _update_schedule = False
                _restart = False
                if "observables" in _config.keys() and _config["observables"] != self.config["observables"]:
                    logging.info("New observables")
                    _Observables = get_observables(
                        satellites  = _config.get("observables",{}).get("satellites",True),
                        missions    = _config.get("observables",{}).get("missions",True),
                        planets     = _config.get("observables",{}).get("planets",True),
                        smallbodies = _config.get("observables",{}).get("smallbodies",False),
                        mellyn      = _config.get("observables",{}).get("mellyn",True),
                        messiers    = _config.get("observables",{}).get("messiers",True),
                    )
                    # Very weird, this sometimes does not work. Some race condition?
                    _updated_observables = self.cc.update_observables(_Observables)
                    print("Updated observables: {}".format(_updated_observables))
                    # self.cc.observables = _Observables
                    _update_schedule = True
                    self.config["observables"] = _config["observables"]

                if "observer" in _config.keys() and _config["observer"] != self.config["observer"]:
                    logging.info("New observer")
                    self.cc.observer = ObserverLLA(
                        lat_rad = float(_config.get("observer",{}).get("lat_deg_N", 34.1376481)*np.pi/180.),
                        lon_rad = float(_config.get("observer",{}).get("lon_deg_E",-118.138686)*np.pi/180.),
                        alt_m   = float(_config.get("observer",{}).get("alt_m", 204.)),
                    )
                    _update_schedule = True
                    self.config["observer"] = _config["observer"]

                if "observables_list" in _config.keys() and _config["observables_list"] != self.config["observables_list"]:
                    logging.info("New observable list parameters")
                    self.cc.time_on_target_s = int(_config.get("observables_list",{}).get("time_on_target_s", 150))
                    self.cc.target_list_length_s = int(_config.get("observables_list",{}).get("target_list_length_s", 600))
                    self.cc.check_visible = _config.get("observables_list",{}).get("check_visible", True)
                    self.cc.visibility_window = VisibilityWindow(
                        min_alt_rad= float(_config.get("observables_list",{}).get("visibility_window",{}).get("min_alt_rad",-np.pi/2.)),
                        max_alt_rad= float(_config.get("observables_list",{}).get("visibility_window",{}).get("max_alt_rad", np.pi/2.)),
                        min_az_rad = float(_config.get("observables_list",{}).get("visibility_window",{}).get("min_az_rad",  0.)),
                        max_az_rad = float(_config.get("observables_list",{}).get("visibility_window",{}).get("max_az_rad",2*np.pi)),
                    )
                    self.cc.refresh_rate_hz = _config.get("observables_list",{}).get("refresh_rate_hz", 1.)
                    _update_schedule = True
                    self.config["observables_list"] = _config["observables_list"]

                if "calibration_level" in _config.keys() and _config["calibration_level"] != self.config["calibration_level"]:
                    logging.info("New calibration level - this will really take effect at the next restart")
                    self.cc.calibration_level = _config["calibration_level"] # This line is quite ineffective, actually. The important thing is that the setting gets saved to disk.
                    self.config["calibration_level"] = _config["calibration_level"]

                if "led_color_scheme" in _config.keys() and _config["led_color_scheme"] != self.config["led_color_scheme"]:
                    logging.info("New color scheme")
                    self.cc.led_colors = self.color_schema.get(_config.get("led_color_scheme","strong"), self.strong_colors_by_type),
                    _update_schedule = True
                    self.config["led_color_scheme"] = _config["led_color_scheme"]

                if "led_pins" in  _config.keys() and _config["led_pins"] != self.config["led_pins"]:
                    logging.info("New LED pins")
                    _restart = True

                if "steppers" in  _config.keys() and _config["steppers"] != self.config["steppers"]:
                    logging.info("New stepper properties")
                    _restart = True

                if "simulated" in  _config.keys() and _config["simulated"] != self.config["simulated"]:
                    logging.info("New simulation properties")
                    _restart = True
                
                # self.config = _config # We do this piecemeal
                # Store configuration on disk!
                self.store_config(self.config)

                if _update_schedule is True:
                    logging.info("Updating schedule")
                    self.cc.schedule = []
                    self.cc.update_schedule()
                if _restart is True:
                    logging.info("Restarting")
                    pass # TODO Raise an Exception or just quit and systemd will respawn us
                reply_code = "OK"
                reply = reply_code+json.dumps(self.config)
            elif len(req) >=2 and req[:2] == "SO":
                _new_observer = json.loads(req[2:])
                if (
                    type(_new_observer) is not dict or
                    "lon_deg_E" not in _new_observer.keys() or
                    "lat_deg_N" not in _new_observer.keys() or
                    "alt_m" not in _new_observer.keys() or
                    np.abs(_new_observer["lon_deg_E"])>180. or
                    np.abs(_new_observer["lat_deg_N"])>90.
                ):
                    logging.warning("New observer is invalid (SO)")
                    reply_code = "NO"
                else:
                    logging.debug("New observer is valid, processing")
                    if (
                        self.cc.observer.lat_rad != _new_observer["lat_deg_N"]*np.pi/180. or
                        self.cc.observer.lon_rad != _new_observer["lon_deg_E"]*np.pi/180. or
                        self.cc.observer.alt_m != _new_observer["alt_m"]
                    ):

                        self.cc.observer = ObserverLLA(
                            lat_rad = _new_observer["lat_deg_N"]*np.pi/180.,
                            lon_rad = _new_observer["lon_deg_E"]*np.pi/180.,
                            alt_m   = _new_observer["alt_m"],
                        )

                        self.config["observer"] = _new_observer
                        self.cc.schedule = []
                        self.cc.update_schedule()
                    else:
                        logging.debug("Observer has not changed")
                    reply_code = "OK"
                    
                # reply = await async_process(msg)
                reply = reply_code+json.dumps(self.config["observer"])

            elif len(req) >=2 and req[:2] == "DL":
                logging.info("Received request to delete and reset schedule list")
                self.cc.schedule = []
                self.cc.update_schedule()
                reply = "OK";
            else:
                reply = "NO";
            await sock.send(reply.encode())

    async def run(self):
        cc_task = asyncio.create_task(self.cc.run())
        io_task = asyncio.create_task(self.listen())
        await cc_task
        await io_task
        



if __name__ == "__main__":
    _debug=False
    # Logging config
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S',
        filename='trovastelle.log',
    )
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger("asyncio").setLevel(logging.DEBUG)

    DATA_PATH = os.environ.get("CELESTIAL_COMPASS_DATA")

    try:
        with open(os.path.join(DATA_PATH, 'config.json'), 'r') as config_file:
            config = json.load(config_file)
    except:
        logging.error("Could not load config.json! Reverting to backup")
        with open(os.path.join(DATA_PATH, 'config.json.bak'), 'r') as config_file:
            config = json.load(config_file)
        
    with open(os.path.join(DATA_PATH, 'colors.json'), 'r') as colors_file:
        color_schema = json.load(colors_file)

    def store_config(config_data):
        with open(os.path.join(DATA_PATH, 'config.json'), 'w') as config_file:
            json.dump(config_data, config_file,indent=2)
    
    ts = trovastelle(config=config, color_schema=color_schema, store_config=store_config)

    ts.calibrate()
    
    asyncio.run(ts.run(),debug=_debug)

    # asyncio.run(recv_and_process())
    

