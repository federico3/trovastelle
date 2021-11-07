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

from luma.core.interface.serial import i2c, spi, pcf8574
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1309, ssd1325, ssd1331, sh1106, ws0010
import os

class DisplayController(object):
    def __init__(self):
        serial = i2c(port=1, address=0x3C)

        # substitute ssd1331(...) or sh1106(...) below if using that device
        self.device = ssd1309(serial)
        self.font_name = font_name
        
    def display_text(self, text: str, font_name: str="LiberationSans-Regular.ttf", font_size: int=16):
        
        font = self.make_font(font_name, font_size)
        
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            w, h = draw.textsize(text=_text, font=font)
            left = (device.width - w) / 2
            top = (device.height - h) / 2 
            draw.text((left, top), text=_text, font=font, fill="white")
            
    def make_font(self, name, size):
        DATA_PATH = os.environ.get("CELESTIAL_COMPASS_DATA")
        font_path = str(os.path.join(DATA_PATH,'liberation-fonts-ttf',name))
        return ImageFont.truetype(font_path, size)