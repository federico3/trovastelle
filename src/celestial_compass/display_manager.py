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

from luma.core.interface.serial import i2c, spi, pcf8574
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1309, ssd1325, ssd1331, sh1106, ws0010
import os
from PIL import ImageFont

from luma.core.interface.serial import i2c, spi, pcf8574
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1309, ssd1325, ssd1331, sh1106, ws0010
import os
from PIL import ImageFont
import skyfield
import warnings

def round_number_to_fixed_width(number, width):
    int_length = len(str(round(number)))
    if int_length>width:
        warnings.warn("Number width {} is longer than max width {}".format(int_length, width))
    if int_length>=width-1:
        formatter = "{:0.0f}"
    else:
        formatter = "{:" + "0.{}".format(width-int_length-1)+"f}"
    num_string = formatter.format(number)
    return num_string

def format_distance(distance: skyfield.units.Distance, width=5):
#     Units
#     LY: from 0.1 LY (1k B) up. Up to 999 LY with decimals, above, int.
#     AU: from 0.1 AU (15M km) to 0.1 LY (10^12). Up to 999 AU, use decimals. Above, just int.
#     M km: from 1M km to 0.1 AU (15M km). Always two decimals
#     km: from 1 km to 1M km. up to 999 km use decimals, above that int.
#     m: from 0 to 1 km. always 1 decimal
#     1 ly ~ 10^13 km
#     1 au ~ 150M  (10~8 km)

    distance_ly = distance.m/9460730472580800 # https://en.wikipedia.org/wiki/Light-year
    if distance_ly>1e9:
        distance_str = round_number_to_fixed_width(distance_ly/1e9, width-1)+ "B LY"
    elif distance_ly>1e6:
        distance_str = round_number_to_fixed_width(distance_ly/1e6, width-1)+ "M LY"
    elif distance_ly>0.1:
        distance_str = round_number_to_fixed_width(distance_ly, width)+ " LY"
    elif distance.au > 0.1:
        distance_str = round_number_to_fixed_width(distance.au, width)+ " AU"
    elif distance.km > 1e6:
        distance_str = round_number_to_fixed_width(distance.km/1e6, width-1)+ "M km"
    elif distance.km>1:
        distance_str = round_number_to_fixed_width(distance.km, width)+ " km"
    else:
        distance_str = round_number_to_fixed_width(distance.m, width+1)+ " m"
    return distance_str

def test_distance_format():
    print(format_distance(skyfield.units.Distance(au=1e5)))
    print(format_distance(skyfield.units.Distance(au=100)))
    print(format_distance(skyfield.units.Distance(au=0.25)))
    print(format_distance(skyfield.units.Distance(km=300*1e6)))
    print(format_distance(skyfield.units.Distance(km=3*1e6)))
    print(format_distance(skyfield.units.Distance(km=300000)))
    print(format_distance(skyfield.units.Distance(km=6378)))
    print(format_distance(skyfield.units.Distance(km=63.78)))

    print(format_distance(skyfield.units.Distance(km=6.378)))

    print(format_distance(skyfield.units.Distance(m=6.378)))
    return

class DisplayController(object):
    def __init__(self, device=None):
        if device is None:
            serial = i2c(port=1, address=0x3C)

            # substitute ssd1331(...) or sh1106(...) below if using that device
            self.device = ssd1309(serial)
        else:
            self.device = device
        
        self.object_name_width  = self.device.width
        self.object_name_height = round(self.device.height*2/3)
        self.object_name_origin = (0,0)
        self.object_name_margin = 4
        
        self.object_type_width  = round(self.device.width)/2
        self.object_type_height = self.device.height-self.object_name_height
        self.object_type_origin = (0,round(self.device.height*2/3)+1)
        self.object_type_margin = 4
        
        self.object_dist_width  = self.device.width-round(self.device.width)/2
        self.object_dist_height = self.device.height-self.object_name_height
        self.object_dist_origin = (self.object_type_width+1,round(self.device.height*2/3)+1)
        self.object_dist_margin = 4
        
        self.canvas = canvas(self.device)
        
    def display_text(self, text: str, font_name: str="LiberationSans-Regular.ttf", font_size: int=16):
        
        font = self.make_font(font_name, font_size)
        
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="white", fill="black")
            w, h = draw.textsize(text=text, font=font)
            left = (self.device.width - w) / 2
            top = (self.device.height - h) / 2 
            draw.text((left, top), text=text, font=font, fill="white")
    
    def _get_text_size_for_box(
        self,
        draw: canvas,
        text: str,
        width: int,
        height: int,
        margin: int=0,
        origin: tuple=(0,0),
        font_name: str="LiberationSans-Regular.ttf"
    ):
        font_size = 0
        text_width = 0
        text_height = 0
#         with canvas(self.device) as draw:
        while (text_width<(width-margin)) and (text_height<(height-margin)):
            font_size += 1
            font = self.make_font(font_name, font_size)
            text_width, text_height = draw.textsize(text=text, font=font)
        return font_size-1
    
    def _display_text_in_box(
        self,
        draw: canvas,
        text: str,
        width: int,
        height: int,
        margin: int=0,
        origin: tuple=(0,0),
        font_size:int=None,
        font_name: str="LiberationSans-Regular.ttf"
    ):
        if font_size is None:
            font_size=self._get_text_size_for_box(
                draw=draw,
                text=text,
                width=width,
                height=height,
                margin=margin,
                origin=origin,
                font_name=font_name,
            )
    
#             font_size = 0
#         text_width = 0
#         text_height = 0
# #         with canvas(self.device) as draw:
#         while (text_width<(width-margin)) and (text_height<(height-margin)):
#             font_size += 1
        font = self.make_font(font_name, font_size)
        text_width, text_height = draw.textsize(text=text, font=font)
        draw.text(
            (origin[0]+round((width-text_width)/2), origin[1]+round((height-text_height)/2)),
             text=text,
             font=font,
             fill="white"
            )
        
    def display_observable_data(
        self,
        observable_name: str="",
        observable_type: str="",
        observable_dist: str="",
        font_name: str="LiberationSans-Regular.ttf"
    ):
        with canvas(self.device) as draw:
            self._display_text_in_box(
                draw=draw,
                text=observable_name,
                width=self.object_name_width,
                height=self.object_name_height,
                origin=self.object_name_origin,
                margin=self.object_name_margin,
                font_name=font_name
            )
            type_size = self._get_text_size_for_box(
                draw=draw,
                text=observable_type,
                width=self.object_type_width,
                height=self.object_type_height,
                origin=self.object_type_origin,
                margin=self.object_type_margin,
                font_name=font_name
            )
            dist_size = self._get_text_size_for_box(
                draw=draw,
                text=observable_dist,
                width=self.object_dist_width,
                height=self.object_dist_height,
                origin=self.object_dist_origin,
                margin=self.object_dist_margin,
                font_name=font_name
            )
            self._display_text_in_box(
                draw=draw,
                text=observable_type,
                width=self.object_type_width,
                height=self.object_type_height,
                origin=self.object_type_origin,
                margin=self.object_type_margin,
                font_size=min(type_size, dist_size),
                font_name=font_name
            )
            self._display_text_in_box(
                draw=draw,
                text=observable_dist,
                width=self.object_dist_width,
                height=self.object_dist_height,
                origin=self.object_dist_origin,
                margin=self.object_dist_margin,
                font_size=min(type_size, dist_size),
                font_name=font_name
            )
        
    
    def make_font(self, name, size):
        DATA_PATH = os.environ.get("CELESTIAL_COMPASS_DATA")
        font_path = str(os.path.join(DATA_PATH,'liberation-fonts-ttf',name))
        return ImageFont.truetype(font_path, size)