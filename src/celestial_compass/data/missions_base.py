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
from celestial_compass.observables import ObservableSkyObject
from celestial_compass.data.planets import planets

# DATA_PATH = os.environ.get("CELESTIAL_COMPASS_DATA")
# load = Loader(DATA_PATH)

# planets = load('de440s.bsp')

# ts = load.timescale()

# Juno
# so, the SPKs for Juno are only in the past. https://naif.jpl.nasa.gov/pub/naif/pds/data/jno-j_e_ss-spice-6-v1.0/jnosp_1000/data/spk/spkinfo.txt
# But Juno is close enough to Jupiter for the purposes of this project
juno = planets['jupiter barycenter']

# Mars probes
# Likewise for our Mars probes
curiosity = planets['mars barycenter']
perseverance = planets['mars barycenter']
ingenuity = planets['mars barycenter']
insight = planets['mars barycenter']
odyssey = planets['mars barycenter']


missions = {
    "Juno": juno,
    "Curiosity": curiosity,
    "Perseverance": perseverance,
    "Ingenuity": ingenuity,
    "InSight": insight,
    "Mars Odyssey": odyssey,
}

ObservableMissions = [ObservableSkyObject(name=key, data=val, type_name="Mission") for key, val in missions.items()]