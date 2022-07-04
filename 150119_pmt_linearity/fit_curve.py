

from numpy import abs, diag, exp, log10, polyval, sqrt, where
from scipy.optimize import curve_fit
from scipy.special import erf
from scipy.stats import linregress

P1 = 1e2


def ice_cube_pmt(x, p0, p1, p2):
    """Saturation curve for PMTs

    from arXiv:1002.2442

    :param x: the measured signal.
    :param p#: parameters for the function.
    :returns: the expected/ideal signal.

    """
    return x * exp(p0 * ((x / p1) ** p2) / ((1. - x / p1) ** 0.25))


ICE_CUBE_TEX = r"""
    $\mathrm{ln}V_{\mathrm{in}} = \mathrm{ln}V +
     \frac{p_0\left(\frac{V}{p_1}\right)^{p_2}}
          {\left(1-\frac{V}{p_1}\right)^{\frac{1}{4}}}$,
     \scriptsize{($p_0 = %.1f$, $p_1 = %d$, $p_2 = %.1f$)}"""


def ice_cube_pmt_p1(x, p0, p2, p3):
    """Saturation curve for PMTs

    P1 is fixed, since the fit is insensitive to ti, as long as x < P1.
    from arXiv:1002.2442

    :param x: the measured signal.
    :param p#: parameters for the function.
    :returns: the expected/ideal signal.

    """
    # The fit is fairly insensitive to the value of p1, just make sure
    # it's higher then x, to prevent division by 0.
    return x * exp(p0 * ((x / p3) ** p2) / ((1. - x / P1) ** 0.25))


def lin(x, slope, intercept):
    return x * slope + intercept


def lin_intersection(slope_1, intercept_1, slope_2, intercept_2):
    if slope_1 == slope_2:
        raise Exception('The lines are parallel and will never cross')
    return ((intercept_2 - intercept_1) / (slope_1 - slope_2))


def log_lin(x, slope, intercept):
    return 10 ** (log10(x) * slope - intercept)


def linear_errorfunction_linear(x, smoothness, slope_high, intercept_high):
    """Two connected linear functions, contributions determined by erf

    Connect two linear lines by smoothing the points around the intersection.
    The contribution from each line is determined using an error function.
    In loglog space.

    :param x: x coordinate at which to evaluate the function.
    :param smoothness: the smoothness of the transition, spreading the
                       error function.
    :param slope_high: the slope of the upper (high x) linear line.
    :param intercept_high: the y-intercept of the upper (high x) linear line.
    :return: the y value at x.

    """
    slope_low, intercept_low = (1., 0.)
    intercept = 10 ** ((intercept_high - intercept_low) /
                       (slope_high - slope_low))
    erf_low = 1 - (erf((x - intercept) * smoothness) + 1) / 2.
    erf_high = (erf((x - intercept) * smoothness) + 1) / 2.
    low = erf_low * log_lin(x, slope_low, intercept_low)
    high = erf_high * log_lin(x, slope_high, intercept_high)
    return low + high


def loglog_xy_circ_lin(x, *args):
    return 10 ** xy_circ_lin(log10(x), *args)


def xy_circ_lin(x, r, slope_high, intercept_high):
    slope_low, intercept_low = (1, 0)
    return lin_circ_lin(x, r, slope_low, intercept_low, slope_high, intercept_high)


def loglog_lin_circ_lin(x, *args):
    return 10 ** lin_circ_lin(log10(x), *args)


def lin_circ_lin(x, r, slope_low, intercept_low, slope_high, intercept_high):
    """
    s = slope_low
    k = intercept_low
    n = slope_high
    m = intercept_high
    ra = r
    rc = center_circle_x
    d = center_circle_y

    The center of the circle is given by (x_c, y_c)

    """
    if slope_low == slope_high:
        raise Exception("Parallel lines not allowed")

    if slope_low > slope_high:
        # Circle below the lines
        sign = -1.
    else:
        # Circle above the lines
        sign = 1.

    # y-intercepts of lines parallel to input lines, but shifted by r
    parallel_intercept_low = intercept_low + sign * r * sqrt(1 + slope_low ** 2)
    parallel_intercept_high = intercept_high + sign * r * sqrt(1 + slope_high ** 2)

    # center of the circle
    x_c = ((parallel_intercept_high - parallel_intercept_low) /
           (slope_low - slope_high))
    y_c = slope_low * x_c + parallel_intercept_low

    # Calculate parameters for lines which intersect the circle center and
    # are perpendicual to the low or high tangents.
    perpendicular_slope_low = -1. / slope_low
    perpendicular_slope_high = -1. / slope_high
    perpendicular_intercept_low = (x_c * (slope_low + 1 / slope_low) +
                                   parallel_intercept_low)
    perpendicular_intercept_high = (x_c * (slope_high + 1 / slope_high) +
                                    parallel_intercept_high)

    # x positions where the lines transition to the circle and vice-versa
    intersect_circle_low_x = lin_intersection(slope_low, intercept_low,
                                              perpendicular_slope_low,
                                              perpendicular_intercept_low)
    intersect_circle_high_x = lin_intersection(slope_high, intercept_high,
                                               perpendicular_slope_high,
                                               perpendicular_intercept_high)

    y = where(x < intersect_circle_low_x,
              lin(x, slope_low, intercept_low),
              y_c - sign * sqrt(r ** 2 - (x - x_c) ** 2))
    y = where(x < intersect_circle_high_x,
              y,
              lin(x, slope_high, intercept_high))

    return y


def polynom(x, *args):
    """Polynomial fit"""

    return polyval(list(args) + [0], x)


def saturating_function(x, p0, p1, p2):
    """A simple saturating function"""

    return x * p2 * exp(p0 * x ** p1)


def chisq(f, y, x, popt, s):
    """Calculate the Chi**2

    :param f: the expected function (from x to y).
    :param x,y: measured data points.
    :param popt: fit paramters.
    :param s: sigma for each data point.
    :returns: chi square value.

    """
    chisquare = sum(((yi - f(xi, *popt)) / si) ** 2
                    for yi, xi, si in zip(y, x, s))

    return chisquare


def redchisq(f, y, x, popt, s, dof):
    """Calculate the reduced Chi**2

    :param f: the expected function.
    :param x,y: measured data points.
    :param popt: fit paramters.
    :param s: sigma for each data point.
    :param dof: degrees of freedom.
    :returns: reduced chi square value.

    """
    chisquare = chisq(f, y, x, popt, s)
    nu = len(x) - 1. - dof

    return chisquare / nu


def lin_fit(x, y, filter):
    """Fit curve to the PMT measurements

    Provide x and y as list.

    :param x: measured signal.
    :param y: expected signal (sum of individual).
    :param err: uncertainties on y data.

    """
    slope, intercept, r_value, p_value, std = linregress(x.compress(filter),
                                                         y.compress(filter))
    return slope, intercept


fit_function = loglog_xy_circ_lin


def fit_curve(x, y, err=None, p0=(2.8, 2, -1)):
    """Fit curve to the PMT measurements

    Provide x and y as list.

    :param x: measured signal.
    :param y: expected signal (sum of individual).
    :param err: uncertainties on y data.

    """
    popt, pcov = curve_fit(fit_function, x, y, sigma=err,
                           p0=p0,
                           absolute_sigma=True)
    if all(popt == p0):
        raise Exception('Failed fit.')
    perr = sqrt(diag(pcov))
    popt[0] = abs(popt[0])
    return popt, perr
