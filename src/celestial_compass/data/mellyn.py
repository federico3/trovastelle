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
import json

from celestial_compass.observables import ObservableTerrestrialLocation

DATA_PATH = os.environ.get("CELESTIAL_COMPASS_DATA")

with open(os.path.join(DATA_PATH, 'mellyn.json'), 'r') as mellyn_file:
    mellyn = json.load(mellyn_file)

ObservableMellyn = [ObservableTerrestrialLocation(name=mellon['name'], data=mellon, type_name="Mellon") for mellon in mellyn]