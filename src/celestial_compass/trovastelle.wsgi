import os

os.environ["CELESTIAL_COMPASS_DATA"] = "/home/pi/trovastelle/data"

from celestial_compass.trovastelle_web import *

application = trovastelle_web_app()
