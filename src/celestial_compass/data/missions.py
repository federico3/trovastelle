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
from skyfield.vectorlib import VectorFunction
from skyfield.constants import AU_KM
import spiceypy as spice
import glob

from celestial_compass.observables import ObservableSkyObject

DATA_PATH = os.environ.get("CELESTIAL_COMPASS_DATA")
load = Loader(DATA_PATH)

planets = load('de440.bsp')
earth = planets['earth']

ts = load.timescale()

class RawSPICEObject(VectorFunction):
    def __init__(self, kernel_list, target):
        self.kernel_list = kernel_list
        for kernel in kernel_list:
            spice.furnsh(kernel)
        self.center = 0
        self.target = target

    def _at(self, t):
        time_et = spice.datetime2et(t.utc_datetime())
        state, _ = spice.spkezr(self.target, [time_et,], 'J2000', 'NONE', '0' )
        r = state[0][:3]
        v = state[0][3:]
        return r / AU_KM, v / AU_KM, None, None

# Voyager
vgr_kernels = glob.glob(os.path.join(DATA_PATH,'VGR','*.bsp'))
vgr_kernels.append(os.path.join(DATA_PATH,'de440.bsp'))
vgr_kernels.append(os.path.join(DATA_PATH,'naif','generic_kernels','lsk','naif0012.tls'))
vgr_kernels.append(os.path.join(DATA_PATH,'naif','generic_kernels','pck','pck00010.tpc'))

vgr1 = RawSPICEObject(vgr_kernels,"-31")
vgr2 = RawSPICEObject(vgr_kernels,"-32")

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

# Parker Solar Probe
PSPkernels = [
    os.path.join(DATA_PATH,'de440.bsp'),
    os.path.join(DATA_PATH,'spp_nom_20180812_20250831_v038_RO5.bsp'),
    os.path.join(DATA_PATH,'naif','generic_kernels','lsk','naif0012.tls'),
    os.path.join(DATA_PATH,'naif','generic_kernels','pck','pck00010.tpc'),
]
PSPtarget = "-96"

PSP = RawSPICEObject(PSPkernels, PSPtarget)

# Bepi Colombo
bepicolombo_kernels = glob.glob(os.path.join(DATA_PATH,'ESA','bepicolombo','kernels','spk','*.bsp'))
bepi = RawSPICEObject(bepicolombo_kernels,"-121")

missions = {
    "Voyager 1": vgr1,
    "Voyager 2": vgr2,
    "Juno": juno,
    "Curiosity": curiosity,
    "Perseverance": perseverance,
    "Ingenuity": ingenuity,
    "InSight": insight,
    "Mars Odyssey": odyssey,
    "Bepi Colombo": bepi,
    "Parker Solar Probe": PSP
}

ObservableMissions = [ObservableSkyObject(name=key, data=val) for key, val in missions.items()]