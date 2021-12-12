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
Data: `wget https://stuff.mit.edu/afs/athena/project/xephem/lib/catalogs/spacecraft.edb`

```
* VOYAGER 2 Launched: 08/22/1977 Last updated: 12/05/1989
* Good from 08/22.58/1977 through 07/09.92/1979
VOYAGER 2-1,e,4.83715,-33.0429,11.8339,3.63929,0.141964,0.724792,53.7867,09/13/1978,1950,0,0
* Good from 07/09.92/1979 through 08/26.12/1981  (corrected 1/22/1997 VRH)
VOYAGER 2-2,h,12/11.077/1978,2.58239,119.197,-9.17007,1.33782,5.02057,1950,0,0
* Good from 08/26.12/1981 through 01/24.75/1986  (corrected 1/22/1997 VRH)
VOYAGER 2-3,h,07/29.801/1981,2.66245,76.9535,112.261,3.44837,9.60542,1950,0,0
* Good from 01/24.75/1986 through 03/13.09/1987  (corrected 1/22/1997 VRH)
VOYAGER 2-4,h,11/25.008/1982,2.49478,-100.383,-46.0771,5.81736,14.40394,1950,0,0
* Good from 03/13.09/1987 through 08/25/1989  (corrected 1/22/1997 VRH)
VOYAGER 2-5,h,11/24.695/1982,2.49617,-100.376,-46.1063,5.8064,14.39968,1950,0,0
* Good from 08/25/1989 through 12/31/2040  (corrected 1/22/1997 VRH)
VOYAGER 2-6,h,04/30.224/1983,78.8189,100.935,130.058,6.2841,21.24042,1950,0,0
* VOYAGER 1 Launched: 09/05/1977 Last updated: 12/05/1989
* Good from 09/05.54/1977 through 03/05.5/1979
VOYAGER 1-1,e,1.03547,-17.9821,-0.349381,4.99712,0.0882316,0.798528,31.6497,08/30/1978,1950,0,0
* Good from 03/05.5/1979 through 11/13/1980  (corrected 1/22/1997 VRH)
VOYAGER 1-2,h,11/28.764/1978,2.47979,112.913,-1.46534,2.29959,5.16622,1950,0,0
* Good from 11/13/1980 through 01/01/2040  (corrected 1/22/1997 VRH)
VOYAGER 1-3,h,12/18.497/1979,35.8006,178.355,-21.7477,3.72559,8.77808,1950,0,0
```
""" 

import os
import ephem

from celestial_compass.observables import ObservableEphemSatellite
from celestial_compass.data.missions_base import ObservableMissions


# Voyager
voyager1_pyephem_raw = ephem.readdb("VOYAGER 1-3,h,12/18.497/1979,35.8006,178.355,-21.7477,3.72559,8.77808,1950,0,0")
voyager2_pyephem_raw = ephem.readdb("VOYAGER 2-6,h,04/30.224/1983,78.8189,100.935,130.058,6.2841,21.24042,1950,0,0")

voyager1_pyephem = ObservableEphemSatellite(
    name='Voyager 1',
    data=voyager1_pyephem_raw,
    type_name="Mission",
)
voyager2_pyephem = ObservableEphemSatellite(
    name='Voyager 2',
    data=voyager2_pyephem_raw,
    type_name="Mission",
)

ObservableMissions = [voyager1_pyephem, voyager2_pyephem] + ObservableMissions