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