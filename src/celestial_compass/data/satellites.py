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