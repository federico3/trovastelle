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
import datetime

DATA_PATH = os.environ.get("CELESTIAL_COMPASS_DATA")
load = Loader(DATA_PATH)
ts = load.timescale()

stations_url = 'http://celestrak.com/NORAD/elements/stations.txt'
visual_sats_url = 'https://www.celestrak.com/NORAD/elements/visual.txt'
stations = load.tle_file(stations_url, filename="Celestrak_stations.txt")
visual_sats = load.tle_file(visual_sats_url, filename="Celestrak_visual.txt")

# If epoch is too old, try to reload.
# This is now handled by the fetch_celestrak_data.sh script, symlinked in /etc/cron.daily.

by_name_stations = {sat.name: sat for sat in stations}
by_name_visual = {sat.name: sat for sat in visual_sats}

satellites = []

if 'ISS (ZARYA)' in by_name_stations.keys():
    satellites.append(by_name_stations['ISS (ZARYA)'])
if 'TIANHE' in by_name_stations.keys():
    satellites.append(by_name_stations['TIANHE'])
if 'HST' in by_name_visual.keys():
    satellites.append(by_name_visual['HST'])

ObservableSatellites = []
now = ts.from_datetime(datetime.datetime.now(datetime.timezone.utc))

for satellite in satellites:
    tle_age_days = abs(now-satellite.epoch)
    if tle_age_days < 14: # Relatively fresh TLEs
        ObservableSatellites.append(ObservableSatellite(name=satellite.name, data=satellite, type_name="Satellite"))
    else:
        logging.warning("Satellite {} TLE is {} days old, skipping".format(satellite, tle_age_days))