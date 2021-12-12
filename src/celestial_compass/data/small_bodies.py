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

"""
### Get the data:

```wget https://www.minorplanetcenter.net/iau/MPCORB/MPCORB.DAT.gz```

### Filter by interest:

```zgrep -P "^("$(paste -sd '|' minor_planets_of_interest.txt)") " MPCORB.DAT.gz > MPCORB.excerpt.DAT```
"""

from skyfield.data import mpc
from skyfield.api import load, Loader
import os
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN

from celestial_compass.observables import ObservableSkyObject

DATA_PATH = os.environ.get("CELESTIAL_COMPASS_DATA")

load = Loader(DATA_PATH)
planets = load('de440.bsp')

with load.open(os.path.join(DATA_PATH,'MPCORB.excerpt.DAT')) as f:
    minor_planets = mpc.load_mpcorb_dataframe(f)

ObservableSmallBodies = []

ts = load.timescale()

for minor_planet_row in minor_planets.iterrows():
    minor_planet_name = minor_planet_row[1]['designation']
    minor_planet_loc = planets['sun'] + mpc.mpcorb_orbit(minor_planet_row[1], ts, GM_SUN)

    ObservableSmallBodies.append(
        ObservableSkyObject(name=minor_planet_name, data=minor_planet_loc, earth=planets['earth'], type_name="Small body")
    )