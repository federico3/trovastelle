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

from skyfield.api import Loader
import os
from celestial_compass.observables import ObservableSkyObject

DATA_PATH = os.environ.get("CELESTIAL_COMPASS_DATA")

load = Loader(DATA_PATH)
planets = load('de440s.bsp')

planet_names = [
    "Mercury",
    "Venus",
    "Earth",
    "Mars",
    "Jupiter",
    "Saturn",
    "Neptune",
    "Uranus",
    "Pluto"
]

ObservablePlanets = []

for planet_name in planet_names:
    try:
        new_planet = planets[planet_name]
    except:
        new_planet = planets[planet_name+ " barycenter"]
    ObservablePlanets.append(
        ObservableSkyObject(name=planet_name, data=new_planet, earth=planets['earth'], type_name="Planet")
    )