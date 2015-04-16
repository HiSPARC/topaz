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
    p1 = 9000.
    return x * exp(p0 * ((x / p1) ** p2) / ((1. - x / p1) ** 0.25))


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

    led_on_b  = [1, 160, 224, 172, 206, 246, 242, 188, 352, 180, 232,
                 236, 292, 232, 260, 258, 198, 302, 202, 212, 218,
                 186, 166, 214, 214]

    multi_led = [((1, 2), 344),
                 ((1, 2, 3), 536),
                 ((1, 2, 3, 4), 720),
                 ((1, 2, 3, 4, 5), 920),
                 ((1, 2, 3, 4, 5, 6), 1140),
                 ((1, 2, 3, 4, 5, 6, 7), 1250),
                 ((1, 2, 3, 4, 5, 6, 7, 8), 1420),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9), 1460),
                 ((1, 2, 3, 4, 5, 6, 7, 8), 1400),
                 ((2, 3, 4, 5, 6, 7, 8), 1340),
                 ((3, 4, 5, 6, 7, 8), 1240),
                 ((4, 5, 6, 7, 8), 1140),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 1540),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), 1620),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), 1700),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13), 1760),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14), 1840),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15), 1880),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16), 1920),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17), 1980),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18), 2020),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19), 2060),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20), 2080),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21), 2120),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22), 2140),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23), 2160),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 2180),
                 ((2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 2160),
                 ((3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 2140),
                 ((6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 2060),
                 ((8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1980),
                 ((10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 1860),
                 ((10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22), 1760),
                 ((10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20), 1680),
                 ((10, 11, 12, 13, 14, 15, 16), 1350),
                 ((10, 11, 12, 13, 14), 1110),
                 ((10, 11, 12, 13), 936),
                 ((10, 11, 12), 760),
                 ((10, 11), 448),
                 ((7, 8, 9), 672),
                 ((6, 7, 8, 9), 896),
                 ((5, 6, 7, 8, 9), 1070),
                 ((4, 5, 6, 7, 8, 9), 1220),
                 ((3, 4, 5, 6, 7, 8, 9), 1290),
                 ((2, 3, 4, 5, 6, 7, 8, 9), 1380)]

    for fibers, signal in multi_led:
        sum_signal = sum(led_on_b[fiber] for fiber in fibers)

    signals = [float(signal) for fibers, signal in multi_led]
    sum_signals = [float(sum(led_on_b[fiber] for fiber in fibers))
                   for fibers, signal in multi_led]

    popt, perr = fit_curve(signals, sum_signals)
    print popt, perr

    fit = (r"$\mathrm{ln}V_{\mathrm{in}}=\mathrm{ln}V + "
           r"\frac{p_0\left(\frac{V}{p_1}\right)^{p_2}}"
           r"{\left(1-\frac{V}{p_1}\right)^{\frac{1}{4}}}$"
           r", \scriptsize{($p_0=%.1f$, $p_1=%d$, $p_2=%.1f$)}") % (popt[0], 9000, popt[1])

    graph = Plot(width=r'.67\linewidth', height=r'.67\linewidth',)
    graph.set_label(fit, location='upper left')
    graph.scatter(sum_signals, signals)
    inputs = linspace(min(signals), max(signals), 500)
    graph.plot([ice_cube_pmt_p1(input, *popt) for input in inputs], inputs, mark=None)
    graph.plot([0, 6000], [0, 6000], mark=None, linestyle='gray')
    graph.set_xlimits(0, 6000)
    graph.set_ylimits(0, 6000)
    graph.set_axis_equal()
    graph.set_xlabel('Sum individual LED pulseheights [mV]')
    graph.set_ylabel('Multiple-LED pulseheight [mV]')
    graph.save_as_pdf('linearity_senstech')
