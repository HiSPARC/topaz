from __future__ import division

from scipy.optimize import curve_fit
from numpy import exp, linspace, sqrt, diag

from artist import Plot


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
    # The fit is fairly insensitive to p1, but make sure it is higher
    # then x, to prevent division by 0.
    return x * exp(p0 * ((x / P1) ** p2) / ((1. - x / P1) ** 0.25))


def saturating_function(x, p0):
    return x * exp(p0 * x)

def chisq(f, y, x, popt, sigma):

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


if __name__ == '__main__':


    led_ph = [1, 150, 220, 156, 225, 230, 230, 182, 299, 163, 202,
              220, 250, 202, 244, 240, 190, 240, 159, 196, 180,
              182, 160, 210, 202]

    led_pi = [1, 1.68, 2.44, 1.80, 2.43, 2.56, 2.57, 2.18, 3.32, 1.82, 2.46,
              2.46, 3.00, 2.36, 2.87, 2.56, 2.22, 2.79, 1.84, 2.20, 2.05,
              2.00, 1.83, 2.47, 2.70]

    multi_led = [((23, 24), 325, 4.45),
                 ((22, 23, 24), 550, 6.55),
                 ((21, 22, 23, 24), 730, 8.61),
                 ((20, 21, 22, 23, 24), 860, 10.60),
                 ((19, 20, 21, 22, 23, 24), 1000, 12.21),
                 ((18, 19, 20, 21, 22, 23, 24), 1120, 15.20),
                 ((17, 18, 19, 20, 21, 22, 23, 24), 1267, 17.66),
                 ((16, 17, 18, 19, 20, 21, 22, 23, 24), 1339, 19.12),
                 ((15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1453, 21.00),
                 ((14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1545, 23.00),
                 ((13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1605, 24.33),
                 ((12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1712, 26.55),
                 ((11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1776, 28.04),
                 ((10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1844, 29.46),
                 ((9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1877, 30.66),
                 ((8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1960, 32.23),
                 ((7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1983, 33.15),
                 ((6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 2036, 34.30),
                 ((4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 2097, 36.25),
                 ((2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 2150, 38.15),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 2170, 38.57)]

    measured_pi = []
    measured_ph = []
    expected_pi = []
    expected_ph = []
    for fibers, ph, pi in multi_led:
        measured_ph.append(ph)
        measured_pi.append(pi)
        expected_ph.append(sum(led_ph[fiber] for fiber in fibers))
        expected_pi.append(sum(led_pi[fiber] for fiber in fibers))

    # Fit and plot pulseheight

    global P1
    P1 = 9000.

    popt, perr = fit_curve(measured_ph, expected_ph)
    print popt, perr


    fit = (r"$\mathrm{ln}V_{\mathrm{in}}=\mathrm{ln}V + "
           r"\frac{p_0\left(\frac{V}{p_1}\right)^{p_2}}"
           r"{\left(1-\frac{V}{p_1}\right)^{\frac{1}{4}}}$"
           r", \scriptsize{($p_0=%.1f$, $p_1=%d$, $p_2=%.1f$)}") % (popt[0], P1, popt[1])

    graph = Plot(width=r'.67\linewidth', height=r'.67\linewidth',)
    graph.set_label(fit, location='upper left')
    graph.scatter(expected_ph, measured_ph)
    inputs = linspace(min(measured_ph), max(measured_ph), 500)
    graph.plot([ice_cube_pmt_p1(input, *popt) for input in inputs], inputs, mark=None)
    graph.plot([0, 6000], [0, 6000], mark=None, linestyle='gray')
    graph.set_xlimits(0, 6000)
    graph.set_ylimits(0, 6000)
    graph.set_axis_equal()
    graph.set_xlabel('Sum individual LED pulseheights [mV]')
    graph.set_ylabel('Multiple-LED pulseheight [mV]')
    graph.save_as_pdf('linearity_senstech_integral_ph')

    # Fit and plot pulseintegral

    P1 = max(expected_pi)

    popt, perr = fit_curve(measured_pi, expected_pi)
    print popt, perr

    fit = (r"$\mathrm{ln}V_{\mathrm{in}}=\mathrm{ln}V + "
           r"\frac{p_0\left(\frac{V}{p_1}\right)^{p_2}}"
           r"{\left(1-\frac{V}{p_1}\right)^{\frac{1}{4}}}$"
           r", \scriptsize{($p_0=%.1f$, $p_1=%d$, $p_2=%.1f$)}") % (popt[0], P1, popt[1])

    graph = Plot(width=r'.67\linewidth', height=r'.67\linewidth',)
    graph.set_label(fit, location='upper left')
    graph.scatter(expected_pi, measured_pi)
    inputs = linspace(min(measured_pi), max(measured_pi), 500)
    graph.plot([ice_cube_pmt_p1(input, *popt) for input in inputs], inputs, mark=None)
    graph.plot([0, 70], [0, 70], mark=None, linestyle='gray')
    graph.set_xlimits(0, 70)
    graph.set_ylimits(0, 70)
    graph.set_axis_equal()
    graph.set_xlabel('Sum individual LED pulseintegral [nVs]')
    graph.set_ylabel('Multiple-LED pulseintegral [nVs]')
    graph.save_as_pdf('linearity_senstech_integral_pi')
