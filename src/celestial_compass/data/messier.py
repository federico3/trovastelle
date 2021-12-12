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

ObservableMessiers = [ObservableSkyObject(name=messier[1]['dso_name'],data=Star.from_dataframe(messier[1]),type_name="Messier") for messier in mlist_named.iterrows()]