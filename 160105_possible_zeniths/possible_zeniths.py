"""Possible directions for two detectors

Given a distance between detectors and their sampling rate this figures out
the possible time differences and the theta angles those would result in if
the shower azimuth was parallel to the line between the detectors.

"""
from numpy import arange, arcsin, degrees, floor

from artist import Plot


def possible_zeniths():
    d = 10
    c = 3e8

    tmax = d / c
    ts = 2.5e-9

    n = floor(tmax / ts)

    k = arange(-n, n + 1)

    theta = arcsin(k * ts / tmax)

    plot = Plot()
    plot.scatter(k * ts * 1e9, degrees(theta))
    plot.set_xlabel(r'Time difference [\si{\ns}]')
    plot.set_ylabel(r'Zenith angle [\si{\degree}]')
    plot.set_ylimits(-90, 90)
    plot.save_as_pdf('possible_zeniths')


if __name__ == "__main__":
    possible_zeniths()
