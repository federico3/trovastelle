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

# from skyfield.api import load
from skyfield.api import Loader
import os
from celestial_compass.observables import ObservableSkyObject

DATA_PATH = os.environ.get("CELESTIAL_COMPASS_DATA")

load = Loader(DATA_PATH)

planets = load('de440.bsp')
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
        ObservableSkyObject(name=planet_name, data=new_planet, earth=planets['earth'])
    )