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

import os
from skyfield.api import Loader, wgs84
from celestial_compass.observables import ObservableSatellite

DATA_PATH = os.environ.get("CELESTIAL_COMPASS_DATA")
load = Loader(DATA_PATH)

stations_url = 'http://celestrak.com/NORAD/elements/stations.txt'
visual_sats_url = 'https://www.celestrak.com/NORAD/elements/visual.txt'
stations = load.tle_file(stations_url, filename="Celestrak_stations.txt")
visual_sats = load.tle_file(visual_sats_url, filename="Celestrak_visual.txt")

# TODO if epoch is too old, try to reload

by_name_stations = {sat.name: sat for sat in stations}
by_name_visual = {sat.name: sat for sat in visual_sats}
satellites = [by_name_stations['ISS (ZARYA)'], by_name_stations['TIANHE'], by_name_visual['HST']]

ObservableSatellites = []
for satellite in satellites:
    ObservableSatellites.append(ObservableSatellite(name=satellite.name, data=satellite, type_name="Satellite"))