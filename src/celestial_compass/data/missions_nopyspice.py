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
from spktype01 import SPKType01
from jplephem.spk import SPK
import warnings
import numpy as np
import networkx as nx

from celestial_compass.observables import ObservableSkyObject
from celestial_compass.data.missions_base import ObservableMissions as base_missions


class Type01Object(VectorFunction):
    def __init__(self, kernel_type1, target, kernel_type2=None):
        self.kernel = kernel_type1
        self.kernel_type2 = kernel_type2
        self.center = 0
        self.target = target

    def _at(self, t):
        k = self.kernel
        k2 = self.kernel_type2
        try:
            r, v = k.compute_type01(0, self.target, t.whole, t.tdb_fraction)
        except ValueError as ve:
            if k2 is None:
                raise(ve)
            warnings.warn("No segment from SSB 0 to {}, trying to find a transform".format(self.target))
            # Let's build a graph of dependencies
            # First, is there a segment with the origin and one with the destination?
            found_center = False
            found_target = False
            for segment in k.segments:
                if segment.center == 0:
                    found_center = True
                if segment.target == self.target:
                    found_target = True
                if (found_center and found_target):
                    break
            if not (found_center and found_target):
                raise ValueError("No transform from center SSB 0 to target {}: either center or target not in kernel".format(self.target))
            # Now we need to find a path from center to target.
            G = nx.DiGraph()
            for segment in k.segments:
                G.add_edge(segment.center, segment.target)
            transform_path = nx.shortest_path(G,0,self.target)
            if not len(transform_path):
                raise ValueError("No transform from center SSB 0 to target {}: center and target not connected".format(self.target))
            for _node_ix, _node in enumerate(transform_path[:-1]):
                _next_node = transform_path[_node_ix+1]
#                 print(k, _node, _next_node)
                # Now, some segments may not be Type 1...
                r = np.zeros([3,])
                v = np.zeros([3,])
                try:
                    _dr, _dv = k.compute_type01(_node, _next_node, t.whole, t.tdb_fraction)
                except ValueError:
                    _dr, _dv = k2[_node, _next_node].compute_and_differentiate(t.whole+t.tdb_fraction)
                r += _dr
                v += _dv
            
        return r / AU_KM, v / AU_KM, None, None

DATA_PATH = os.environ.get("CELESTIAL_COMPASS_DATA")
load = Loader(DATA_PATH)
    
v1_kernel_file = os.path.join(DATA_PATH,'Voyager_1.a54206u_V0.2_merged.bsp')
# v1_kernel_file = 'data/voyager_1.ST+1991_a54418u.merged.bsp'
v2_kernel_file = os.path.join(DATA_PATH,'Voyager_2.m05016u.merged.bsp')
# v2_kernel_file = 'data/voyager_2.ST+1992_m05208u.merged.bsp'


voyager_1_kernel_type1 = SPKType01.open(v1_kernel_file)
voyager_1_kernel_type2 = SPK.open(v1_kernel_file)
voyager_1 = Type01Object(voyager_1_kernel_type1, -31, voyager_1_kernel_type2)


voyager_2_kernel_type1 = SPKType01.open(v2_kernel_file)
voyager_2_kernel_type2 = SPK.open(v2_kernel_file)
voyager_2 = Type01Object(voyager_2_kernel_type1, -32, voyager_2_kernel_type2)

missions_nopyspice = {
   "Voyager 1": voyager_1,
   "Voyager 2": voyager_2,
}

ObservableMissions = [ObservableSkyObject(name=key, data=val, type_name="Mission") for key, val in missions_nopyspice.items()] + base_missions
