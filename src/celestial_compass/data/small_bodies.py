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
        ObservableSkyObject(name=minor_planet_name, data=minor_planet_loc, earth=planets['earth'])
    )