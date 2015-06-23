from __future__ import division

from scipy.optimize import curve_fit
from numpy import exp, linspace, sqrt, diag

from artist import Plot

P1 = 9000.


def ice_cube_pmt(x, p0, p1, p2):
    """Saturation curve for PMTs

    from arXiv:1002.2442

    :param x: the measured signal
    :returns: the expected/ideal signal.

    """
    return x * exp(p0 * ((x / p1) ** p2) / ((1. - x / p1) ** 0.25))


def ice_cube_pmt_p1(x, p0, p2):
    """Saturation curve for PMTs

    from arXiv:1002.2442

    :param x: the measured signal
    :returns: the expected/ideal signal.

    """
    # The fit is fairly insensitive to the value of p1, just make sure
    # it's higher then x, to prevent division by 0.
    return x * exp(p0 * ((x / P1) ** p2) / ((1. - x / P1) ** 0.25))


def saturating_function(x, p0):
    return x * exp(p0 * x)


def chisq(f, y, x, popt, s):
    """Calculate the Chi**2

    :param f: the expected function
    :param x,y: measured data points
    :param popt: fit paramters
    :param s: sigma for each data point
    :returns: chi square value

    """
    chisq = sum(((yi - f(xi, *popt)) / si) ** 2 for yi, xi, si in zip(y, x, s))

    return chisq


def fit_curve(x, y):
    """Fit curve to the PMT measurements

    :param x: measure signal
    :param y: expected signal (sum of individual)

    """
    popt, pcov = curve_fit(ice_cube_pmt_p1, x, y, p0=(40., 2.5))
    perr = sqrt(diag(pcov))
    return popt, perr
