"""Compare station zenith distribution to fits"""



from numpy import arange, array, cos, exp, interp, radians, sin, std, sum
from scipy.optimize import curve_fit
from scipy.stats import binned_statistic

from artist import Plot

from sapphire import Station
from sapphire.utils import gauss


def get_zenith_distribution():
    station = Station(501)
    counts = []
    angles = []
    for j in range(1, 13):
        for i in range(1, 29):
            try:
                zenith_hist = station.zenith(2015, j, i)
            except:
                continue
            total_counts = zenith_hist['counts'].sum()
            if total_counts:
                angles.extend(zenith_hist['angle'])
                # Normalized
                counts.extend(zenith_hist['counts'] / total_counts)
    angles = array(angles).astype('float64')
    counts = array(counts)

    angles += 1.5  # bin edges to bin centers
    angles_bins = arange(0, 91, 3)

    mean_counts = binned_statistic(angles, counts,
                                   statistic='mean', bins=angles_bins)[0]
    std_counts = binned_statistic(angles, counts,
                                  statistic=std, bins=angles_bins)[0]
    angle_centers = (angles_bins[1:] + angles_bins[:-1]) / 2.

    return angle_centers, mean_counts, std_counts


def rossi(x, a, b):
    """ Rossi: zenith angle distribution

    :param x: zenith in degrees.

    """
    rx = radians(x)
    geometry = sin(rx) * cos(rx)
    return a * geometry * cos(rx) ** b


def iyono(x, a, b):
    """ Iyono 2007: zenith angle distribution

    :param x: zenith in degrees.

    """

    rx = radians(x)
    geometry = sin(rx) * cos(rx)
    return a * geometry * exp(-b * ((1 / cos(rx)) - 1))


def ciampa(x, a, b, d):
    """ Ciampa 1998: zenith angle distribution

    :param x: zenith in degrees.

    """
    rx = radians(x)
    geometry = sin(rx) * cos(rx)
    return a * geometry * exp(b * (1 / cos(rx)) - d)


def mod_ciampa(x, a, b):
    """ Based on Ciampa 1998: zenith angle distribution

    :param x: zenith in degrees.

    Positive C parameter

    """
    rx = radians(x)
    geometry = sin(rx) * cos(rx)
    return a * geometry * exp(-b * (1 / cos(rx)))


def mod_ciampa_conv_full(a, b, d):
    """ Based on Ciampa 1998: zenith angle distribution

    Positive C parameter

    """
    x = arange(0.1, 85, 0.1)
    rx = radians(x)
    result = sum((gauss(rx, mod_ciampa(xi, a, b), rxi, radians(d / cos(rxi)))
                  for xi, rxi in zip(x, rx)), axis=0)
    return rx, result


def mod_ciampa_conv(x, a, b, d):
    """ Based on Ciampa 1998: zenith angle distribution

    :param x: zenith in degrees.

    Positive C parameter

    """
    rx, result = mod_ciampa_conv_full(a, b, d)
    return interp(radians(x), rx, result)


def plot_zenith(angle_centers, mean_counts, std_counts):
    fit_functions = [rossi, iyono, mod_ciampa, mod_ciampa_conv]

    rangle_centers = radians(angle_centers)
    sangle_centers = convert_angles(angle_centers)
    angles = arange(0.1, 85, 0.1)
    rangles = radians(angles)

    for fit_function in fit_functions:
        popt, pcov = curve_fit(fit_function, angle_centers, mean_counts)  # , sigma=std_counts)
        print(popt)

        plot = Plot()
        plot.scatter(angle_centers, mean_counts, yerr=std_counts, markstyle='red')
        plot.plot(angles, fit_function(angles, *popt), mark=None)
        plot.set_ylabel('Counts')
        plot.set_xlabel(r'Zenith [\si{\degree}]')
        plot.save_as_pdf('zenith_distribution_%s' % fit_function.__name__)

        plot = Plot('semilogy')
        plot.scatter(sangle_centers, mean_counts / sin(rangle_centers), yerr=std_counts)
        fitted_counts = fit_function(angles, *popt)
        plot.plot(convert_angles(angles), fitted_counts / sin(rangles), mark=None)
        plot.plot(convert_angles(angles), fitted_counts, linestyle='gray', mark=None)
        plot.set_ylabel('Counts')
        plot.set_xlimits(0, 1)
        plot.set_xlabel(r'Zenith angle [$\sec \theta - 1$]')
        plot.save_as_pdf('zenith_distribution_sec_%s' % fit_function.__name__)


def convert_angles(angles):
    return 1. / cos(radians(angles)) - 1


if __name__ == "__main__":
    if 'angle_centers' not in globals():
        angle_centers, mean_counts, std_counts = get_zenith_distribution()

    plot_zenith(angle_centers, mean_counts, std_counts)
