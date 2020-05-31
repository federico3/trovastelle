# Sky Finder

An arrow that points at interesting objects in the sky, inspired by the art installation at the JPL mall.

## Basic idea

A pointing mechanism (an arrow and/or a laser pointer) that will point out interesting targets in the sky either automatically or in response to user input.

Targets may include

- Stars, galaxies, and other interesting deep sky objects
- Earth satellites
- Locations on Earth (mountains, cities, friends)
- Airplanes?

The mechanism should have a screen to display what is being observed.

## Hardware

### Frame and Assembly

### Motors

Steppers, servos, simple DC motors?

Need a motor driver

### Display

### Laser Pointer

### Brains

System-on-a-chip (SoC) like a Raspberry Pi or microcontroller like ESP/Arduino?

- SoC is way easier to work with (existing astronomy libraries, etc) and has no storage/RAM limitations, but boots slowly and has higher power consumption.
- Microcontroller boots instantly and has lower power usage, but is _very_ limited (a few kBs of RAM).


### Power

USB plug and built-in battery? Need a charge controller to automatically switch from shore power to on-board battery.

## Design concepts

### V1: Sky only, semi-automatic

A pair of stepper motors actuate the pointing mechanism. A microcontroller keeps track of the location of the stepper motors and reports it to SkySafari through the [basic encoder protocol](https://github.com/federico3/DobsonianDSC). [SkySafari](https://play.google.com/store/apps/details?id=com.simulationcurriculum.skysafari5&hl=en_US) issues GOTO commands to the microcontroller via the same protocol. All projections and translations from steps to sky coordinates are performed by Sky Safari.

> TODO: does SkySafari send GoTo commands with the basic protocol?

No screen, no laser pointer, no way to automatically point at objects, calibration needed before every use.

Downside: needs external calibration before use.

### V2: self-calibrating

A compass and accelerometer are installed on the pointing mechanism. This way, the arrow knows where it is pointed (to a precision of a few degrees) in the local alt-az frame. The arrow can communicate its azm-alt to Sky Safari using the [NexStar serial protocol](https://s3.amazonaws.com/celestron-site-support-files/support_files/1154108406_nexstarcommprot.pdf). Conversions from ra-dec to alt-az can be handled with, e.g., [astropy](https://gist.github.com/dokeeffe/18857db66dbabc14679c20a8560e2cd6). 

#### Software updates

- SkySafari compatibility with new protocol
- Cycle through scripted celestial objects autonomously
- Slew to follow satellites autonomously
- Cycle through ground-based objects (lon-lat) autonomously
- Read airplane locations from fr24 or adsbexchange 

#### V2.1: display

V2, but with a display to show what the arrow is pointing at.

#### V2.2: GPS

Automatically get time and location from a GPS receiver.

#### V3.0: laser

V2, but with a laser to point to interesting objects. The laser is controlled by the microcontroller and there is a safety interlock on the base, requiring the user to be present for use.

#### V4.0: camera and astrometry.net

To increase precision, the arrow incorporates a camera that looks at the sky and plate-solves. Probably _very_ unnecessary and may make things more complicated if plate-solving is used by day.
