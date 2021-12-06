import os
import datetime
import skyfield
try:
    import ephem
    EPHEM_AVAILABLE=True
except ModuleNotFoundError as e:
    EPHEM_AVAILABLE=False
from skyfield.api import N, Star, W, E, wgs84, Loader, load_file

DATA_PATH = os.environ.get("CELESTIAL_COMPASS_DATA")

load = Loader(DATA_PATH)

class Observable(object):
    def __init__(self, name, data, weight:float=1., color:list[float]=[1., 1., 1.], check_visible:bool=True):
        self.name = name
        self.data = data
        self.weight = weight
        self.color = color
        self.check_visible = check_visible
    def observe_topocentric(
        self,
        observer_lon_rad:
        float,
        observer_lat_rad: float,
        observer_h_m: float, 
        observing_time: datetime.datetime,
    ):
        raise NotImplemented
    def __str__(self):
        return("Observable: {}".format(self.name))
    def __repr__(self):
        return("Observable: {}\n{}".format(self.name,self.data))
    
class ObservableTerrestrialLocation(Observable):
    def __init__(
        self,
        name: str,
        data: dict,
        weight:float=1.,
        color:list[float]=[1., 1., 1.],
        check_visible:bool=False
    ):
        self.name = name
        self.data = data
        self.weight = weight
        self.color = color
        self.check_visible = check_visible
        self.location_relative = wgs84.latlon(
            data["lat_deg_N"]*N,
            data["lon_deg_E"]*E,
            elevation_m=data["alt_m"]
        )
        
    def observe_topocentric(
        self,
        observer_lon_E_deg: float,
        observer_lat_N_deg: float,
        observer_h_m: float, 
        observing_time: datetime,
    ):
        ts = load.timescale()
        t = ts.from_datetime(observing_time)
        
        observer_relative = wgs84.latlon(
            latitude_degrees=observer_lat_N_deg*N,
            longitude_degrees=observer_lon_E_deg*E,
            elevation_m=observer_h_m
        )
        
        location_relative = self.location_relative - observer_relative
        loc_topocentric = location_relative.at(t)
        alt, az, distance = loc_topocentric.altaz()
        
        return alt.radians, az.radians, distance
    
    def __str__(self):
        return("Observable terrestrial location: {}".format(self.name))
    def __repr__(self):
        return("Observable: {}\n{}".format(self.name,self.data))
    
class ObservableSkyObject(Observable):
    def __init__(
        self,
        name: str,
        data: skyfield.jpllib.ChebyshevPosition,
        earth=None,
        weight:float=1.,
        color:list[float]=[1., 1., 1.],
        check_visible:bool=True,
    ):
        self.name = name
        self.body = data
        self.weight = weight
        self.color = color
        self.check_visible = check_visible
        if earth is None:
            self.planets = load('de440.bsp')
            self.earth = self.planets['earth']
        else:
            self.earth = earth
        
    def observe_topocentric(
        self,
        observer_lon_E_deg: float,
        observer_lat_N_deg: float,
        observer_h_m: float, 
        observing_time: datetime,
    ):
        ts = load.timescale()
        t = ts.from_datetime(observing_time)
        
        observer = self.earth+wgs84.latlon(
            observer_lat_N_deg*N,
            observer_lon_E_deg*E,
            elevation_m=observer_h_m
        )
        
        body_astrometric = observer.at(t).observe(self.body)

        alt, az, distance = body_astrometric.apparent().altaz()
        
        return alt.radians, az.radians, distance
    
    def __str__(self):
        return("Observable sky object: {}".format(self.name))
    def __repr__(self):
        return("Observable: {}\n{}".format(self.name,self.body))
    
class ObservableSatellite(Observable):
    def __init__(
        self,
        name: str,
        data: skyfield.sgp4lib.EarthSatellite,
        weight:float=1.,
        color:list[float]=[1., 1., 1.],
        check_visible:bool=True,
    ):
        self.name = name
        self.satellite = data
        self.weight = weight
        self.color = color
        self.check_visible = check_visible
    def observe_topocentric(
        self,
        observer_lon_E_deg: float,
        observer_lat_N_deg: float,
        observer_h_m: float, 
        observing_time: datetime,
    ):
        ts = load.timescale()
        t = ts.from_datetime(observing_time)
        
        observer_relative = wgs84.latlon(
            latitude_degrees=observer_lat_N_deg*N,
            longitude_degrees=observer_lon_E_deg*E,
            elevation_m=observer_h_m
        )
        
        sat_relative = self.satellite - observer_relative
        sat_topocentric = sat_relative.at(t)
        alt, az, distance = sat_topocentric.altaz()
        
        return alt.radians, az.radians, distance
    
    def __str__(self):
        return("Observable satellite: {}".format(self.name))
    def __repr__(self):
        return("Observable: {}\n{}".format(self.name,self.satellite))
    
if EPHEM_AVAILABLE:
    class ObservableEphemSatellite(Observable):
        def __init__(
            self,
            name: str,
            data: ephem.FixedBody,
            weight:float=1.,
            color:list[float]=[1., 1., 1.],
            check_visible:bool=True,
        ):
            self.name = name
            self.satellite = data
            self.weight = weight
            self.color = color
            self.check_visible = check_visible
        def observe_topocentric(
            self,
            observer_lon_E_deg: float,
            observer_lat_N_deg: float,
            observer_h_m: float, 
            observing_time: datetime,
        ):
            
            ephemobs = ephem.Observer()
            ephemobs.lon = str(observer_lon_E_deg)
            ephemobs.lat = str(observer_lat_N_deg)
            ephemobs.elevation = observer_h_m

            ephemobs.date = datetime.datetime.now()
            
            self.satellite.compute(ephemobs)
            
            return self.satellite.alt, self.satellite.az, self.satellite.earth_distance
        
        def __str__(self):
            return("Observable satellite: {}".format(self.name))
        def __repr__(self):
            return("Observable: {}\n{}".format(self.name,self.satellite))
else:
    class ObservableEphemSatellite(Observable):
        pass