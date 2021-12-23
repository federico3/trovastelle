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


from celestial_compass.display_manager import DisplayController, round_number_to_fixed_width, format_distance, test_distance_format
from celestial_compass.visibility_window import VisibilityWindow
import matplotlib.colors as mcolors
from celestial_compass.arrow_controller import ArrowController, sim9dof, simstepper 
import warnings, logging

from celestial_compass.compass import CelestialCompass
from celestial_compass.observables import ObserverLLA

import numpy as np

if __name__ == "__main__":
    
    # Logging config
    logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
    
    # LED config
    logging.debug("Configuring LEDs")
    R_LED = 5
    G_LED = 6
    B_LED = 13
    A_LED = 19
    strong_colors_by_type = {
        'Mellon': "xkcd:hot green",
        'Messier': "xkcd:bright orange",
        'Mission': "xkcd:bright red",
        'Planet': "xkcd:true blue",
        'Satellite': "xkcd:very light purple",
    }

    pale_colors_by_type = {
        'Mellon': "xkcd:pale",
        'Messier': "xkcd:baby green",
        'Mission': "xkcd:light periwinkle",
        'Planet': "xkcd:pale mauve",
        'Satellite': "xkcd:magenta",
    }
    

    logging.debug("Configuring observables")
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
    # from celestial_compass.data.small_bodies import ObservableSmallBodies
    from celestial_compass.data.mellyn import ObservableMellyn    
    from celestial_compass.data.messier import ObservableMessiers
    

    # Observables = ObservableSatellites+ObservableMissions+ObservablePlanets+ObservableSmallBodies+ObservableMellyn+ObservableMessiers
    Observables = ObservableSatellites+ObservableMissions+ObservablePlanets+ObservableMellyn+ObservableMessiers
    
    logging.debug("Configuring observer")
    # Observer: Marzia
    _observer = ObservableMellyn[4]

    observer = ObserverLLA(
        lat_rad = _observer.data['lat_deg_N']*np.pi/180.,
        lon_rad = _observer.data['lon_deg_E']*np.pi/180.,
        alt_m  = _observer.data['alt_m'],
    )

    logging.debug("Configuring arrow controller")
    # Arrow controller
    ac = ArrowController(simulate_motors=False, simulate_9dof=False)
    
    logging.debug("Configuring Trovastelle")
    # Full controller
    cc = CelestialCompass(
            controller= ac,
            observer = observer,
            observables = Observables,
            time_on_target_s=15.,
            target_list_length_s=60,
            check_visible= False,
    #         visibility_window=VisibilityWindow(min_alt_rad=0.),
            simulated_display=False,
            led_pins_rgba = (R_LED, G_LED, B_LED, A_LED),
            led_colors=strong_colors_by_type,
        )
    
    logging.debug("Running! Trovastelle")
    cc.run()