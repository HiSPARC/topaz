# Source:
# https://github.com/astropy/astropy/blob/master/astropy/coordinates/tests/accuracy/test_altaz_icrs.py

# Licensed under a 3-clause BSD style license - see:
# https://github.com/astropy/astropy/blob/master/licenses/LICENSE.rst
"""Accuracy tests for AltAz to ICRS coordinate transformations.

We use "known good" examples computed with other coordinate libraries.

Note that we use very low precision asserts because some people run tests on 32-bit
machines and we want the tests to pass there.
TODO: check if these tests pass on 32-bit machines and implement
higher-precision checks on 64-bit machines.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import calendar
import datetime

import numpy as np

from astropy.tests.helper import pytest, catch_warnings
from astropy import units as u
from astropy.time import Time, TimeDelta
from astropy.coordinates.builtin_frames import AltAz
from astropy.coordinates import EarthLocation
from astropy.coordinates import Angle, SkyCoord

from sapphire.transformations import base, angles, celestial, clock


def test_against_hor2eq():
    """Check that Astropy gives consistent results with an IDL hor2eq example.

    See EXAMPLE input and output here:
    http://idlastro.gsfc.nasa.gov/ftp/pro/astro/hor2eq.pro
    """
    print('IDL hor2eq')
    # Observatory position for `kpno` from here:
    # http://idlastro.gsfc.nasa.gov/ftp/pro/astro/observatory.pro
    location = EarthLocation(lon=Angle('-111d36.0m'),
                             lat=Angle('31d57.8m'),
                             height=2120. * u.m)

    # obstime = Time('2041-12-26 05:00:00')
    obstime = Time(2466879.7083333, format='jd')
    # obstime += TimeDelta(-2, format='sec')

    altaz_frame = AltAz(obstime=obstime, location=location)
    altaz = SkyCoord('264d55m06s 37d54m41s', frame=altaz_frame)

    radec_frame = 'icrs'

    # The following transformation throws a warning about precision problems
    # because the observation date is in the future
    with catch_warnings() as _:
        radec_actual = altaz.transform_to(radec_frame)
    print('Astropy: ', radec_actual)


    radec_expected = SkyCoord('00h13m14.1s  +15d11m0.3s', frame=radec_frame)
    print('Source:  ', radec_expected)
    distance = radec_actual.separation(radec_expected).to('arcsec')
    # print(distance)

    # TODO: why is there a difference of 2.6 arcsec currently?
    # radec_expected = ra=3.30875 deg, dec=15.183416666666666 deg
    # radec_actual = ra=3.3094193224314625 deg, dec=15.183757021354532 deg
    # distance = 2.6285 arcsec
#     assert distance < 5 * u.arcsec

    # SAPPHiRE
    longitude = -111.6
    latitude = 31.9633
    jd = 2466879.7083333
    elevation = (37, 54, 41)
    azi = (264, 55, 6)
    # lst = clock.gmst_to_lst(clock.juliandate_to_gmst(jd), longitude)
    # Matches  LAST = +03 53 53.6  in the hor2eq.pro
    gps = clock.utc_to_gps(calendar.timegm(clock.juliandate_to_utc(jd).utctimetuple()))
    zenith, azimuth = celestial.horizontal_to_zenithazimuth(
        np.radians(base.sexagesimal_to_decimal(*elevation)),
        np.radians(base.sexagesimal_to_decimal(*azi)))
    ra, dec = celestial.zenithazimuth_to_equatorial(longitude, latitude,
                                                    gps, zenith, azimuth)

    print('SAPPHiRE: ra=%f, dec=%f' % (np.degrees(ra), np.degrees(dec)))


def test_against_pyephem():
    """Check that Astropy gives consistent results with one PyEphem example.

    PyEphem: http://rhodesmill.org/pyephem/

    See example input and output here:
    https://gist.github.com/zonca/1672906
    https://github.com/phn/pytpm/issues/2#issuecomment-3698679
    """
    print('PyEphem')
    obstime = Time('2011-09-18 08:50:00')
    location = EarthLocation(lon=Angle('-109d24m53.1s'),
                             lat=Angle('33d41m46.0s'),
                             height=0. * u.m)
    # We are using the default pressure and temperature in PyEphem
    altaz_frame = AltAz(obstime=obstime, location=location)

    altaz = SkyCoord('6.8927d -60.7665d', frame=altaz_frame)
    radec_actual = altaz.transform_to('icrs')
    print('Astropy: ', radec_actual)

    radec_expected = SkyCoord('196.497518d -4.569323d', frame='icrs')  # EPHEM
    print('Source:  ', radec_expected)
    # radec_expected = SkyCoord('196.496220d -4.569390d', frame='icrs')  # HORIZON
    distance = radec_actual.separation(radec_expected).to('arcsec')
    # TODO: why is this difference so large?
    # It currently is: 31.45187984720655 arcsec
    assert distance < 1e3 * u.arcsec

    # Add assert on current Astropy result so that we notice if something changes
    radec_expected = SkyCoord('196.495372d -4.560694d', frame='icrs')
    distance = radec_actual.separation(radec_expected).to('arcsec')
    # Current value: 0.0031402822944751997 arcsec
    #assert distance < 1 * u.arcsec

    # SAPPHiRE
    longitude = base.sexagesimal_to_decimal(-109, -24, -53.1)
    latitude = base.sexagesimal_to_decimal(33, 41, 46.0)
    utc = datetime.datetime(2011, 9, 18, 8, 50, 00)
    elevation = np.radians(-60.7665)
    azi = np.radians(6.8927)
    gps = clock.utc_to_gps(calendar.timegm(utc.utctimetuple()))
    zenith, azimuth = celestial.horizontal_to_zenithazimuth(elevation, azi)
    ra, dec = celestial.zenithazimuth_to_equatorial(longitude, latitude,
                                                    gps, zenith, azimuth)

    print('SAPPHiRE: ra=%f, dec=%f' % (np.degrees(ra), np.degrees(dec)))


def test_against_jpl_horizons():
    """Check that Astropy gives consistent results with the JPL Horizons example.

    The input parameters and reference results are taken from this page:
    (from the first row of the Results table at the bottom of that page)
    http://ssd.jpl.nasa.gov/?horizons_tutorial
    """
    print('NASA JPL')
    obstime = Time('1998-07-28 03:00')
    location = EarthLocation(lon=Angle('248.405300d'),
                             lat=Angle('31.9585d'),
                             height=2.06 * u.km)
    # No atmosphere
    altaz_frame = AltAz(obstime=obstime, location=location)

    altaz = SkyCoord('143.2970d 2.6223d', frame=altaz_frame)
    radec_actual = altaz.transform_to('icrs')
    print('Astropy: ', radec_actual)
    radec_expected = SkyCoord('19h24m55.01s -40d56m28.9s', frame='icrs')
    print('Source:  ', radec_expected)
    distance = radec_actual.separation(radec_expected).to('arcsec')
    #assert distance < 1 * u.arcsec

    # SAPPHiRE
    longitude = 248.405300
    latitude = 31.9585
    utc = datetime.datetime(1998, 7, 28, 3, 0)
    elevation = np.radians(2.6223)
    azi = np.radians(143.2970)
    gps = clock.utc_to_gps(calendar.timegm(utc.utctimetuple()))
    zenith, azimuth = celestial.horizontal_to_zenithazimuth(elevation, azi)
    ra, dec = celestial.zenithazimuth_to_equatorial(longitude, latitude,
                                                    gps, zenith, azimuth)

    print('SAPPHiRE: ra=%f, dec=%f' % (np.degrees(ra), np.degrees(dec)))


if __name__ == '__main__':
    test_against_hor2eq()
    test_against_pyephem()
    test_against_jpl_horizons()
