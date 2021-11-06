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
import json

from celestial_compass.observables import ObservableTerrestrialLocation

DATA_PATH = os.environ.get("CELESTIAL_COMPASS_DATA")

with open(os.path.join(DATA_PATH, 'mellyn.json'), 'r') as mellyn_file:
    mellyn = json.load(mellyn_file)

ObservableMellyn = [ObservableTerrestrialLocation(name=mellon['name'], data=mellon) for mellon in mellyn]