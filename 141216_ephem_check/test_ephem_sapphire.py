from datetime import datetime

import numpy as np
import ephem

from sapphire.transformations import base, angles, celestial, clock


LONGITUDE = 52.3562599596
LATITUDE = 4.95294402001
ALTITUDE = 51.4433

ZENITH = 0.38176
AZIMUTH = 3.0030

H_ALTITUDE, H_AZIMUTH = celestial.zenithazimuth_to_horizontal(ZENITH, AZIMUTH)

GPS = 1333018296.870008589
UTC = clock.gps_to_utc(GPS)


def calc_ephem():
    """Calculate coordinates using PyEphem

    Code from http://stackoverflow.com/a/28096359/1033535

    Check using: http://lambda.gsfc.nasa.gov/toolbox/tb_coordconv.cfm

    """
    observer = ephem.Observer()
    observer.pressure = 0
    observer.lon = str(LONGITUDE)
    observer.lat = str(LATITUDE)
    observer.elevation = ALTITUDE
    observer.date = ephem.Date(datetime.utcfromtimestamp(UTC))

    ra, dec = observer.radec_of(H_AZIMUTH, H_ALTITUDE)
    print 'Ephem:   ', ra, dec
    print 'Ephem:    %10.6f %10.6f' % (ra.real, dec.real)
    print 'Ephem:    %10.6f %10.6f' % (np.degrees(ra.real), np.degrees(dec.real))

#     e = ephem.Equatorial(ra, dec, epoch='2000')
#     g = ephem.Galactic(e)
#     print 'Galactic', g.lon, g.lat


def calc_sapphire():
    """Calculate coordinates using SAPPHiRE

    """
    ra, dec = celestial.zenithazimuth_to_equatorial(LONGITUDE, LATITUDE,
                                                    GPS, ZENITH, AZIMUTH)

    sra = base.decimal_to_sexagesimal(angles.radians_to_hours(ra))
    sdec = base.decimal_to_sexagesimal(np.degrees(dec))

    print 'SAPPHiRE:', '%d:%02d:%02.2f' % sra, '%d:%02d:%02.2f' % sdec
    print 'SAPPHiRE: %10.6f %10.6f' % (ra, dec)
    print 'SAPPHiRE: %10.6f %10.6f' % (np.degrees(ra), np.degrees(dec))


if __name__ == '__main__':
    calc_ephem()
    calc_sapphire()

