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

from skyfield.api import Loader, Star
import json
import pandas as pd
import os

from celestial_compass.observables import ObservableSkyObject

DATA_PATH = os.environ.get("CELESTIAL_COMPASS_DATA")

load = Loader(DATA_PATH)

def load_d3_celestial_messier_dataframe(fobj):
    """Given an open file for a JSON de-celestial Messier catalog, return a parsed dataframe.
    """
    try:
        from pandas import read_json, set_option
    except ImportError:
        raise ImportError("NO PANDAS NO CANDO")

    fobj.seek(0)
    magic = fobj.read(2)
    compression = 'gzip' if (magic == b'\x1f\x8b') else None
    fobj.seek(0)

    _catalog = json.load(fobj)
        
    df = pd.json_normalize(_catalog, record_path=['features'])
    
    df['dso_id'] = df['id']
    df['ra_degrees'] = df['geometry.coordinates'].map(lambda x: x[0])
    df['dec_degrees'] = df['geometry.coordinates'].map(lambda x: x[1])
    df['messier_id'] = df['id'][1:]
    df['magnitude'] = df['properties.mag']
    df['named'] = df.apply(lambda x: len(x['properties.alt'])>0, axis=1)
    df['dso_name'] = df.apply(lambda x: x['properties.alt'] + " (" + x['properties.name'] +")" if x['properties.alt'] else x['properties.name'], axis=1)
    df['label'] = df['dso_name']
    
    df = df.assign(
        ra_hours = df['ra_degrees'] / 15.0,
        epoch_year = 2000.0,
    )

    return df

d3cel_messier_URL = 'https://raw.githubusercontent.com/ofrohn/d3-celestial/master/data/messier.json'
with load.open(d3cel_messier_URL, filename=os.path.join(DATA_PATH,"d3cel_Messier.json")) as f:
    mlist = load_d3_celestial_messier_dataframe(f)

# messiers = Star.from_dataframe(mlist)

mlist_named = mlist[mlist['named']]

ObservableMessiers = [ObservableSkyObject(name=messier[1]['dso_name'],data=Star.from_dataframe(messier[1])) for messier in mlist_named.iterrows()]