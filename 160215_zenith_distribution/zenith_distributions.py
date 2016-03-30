"""Compare station zenith distribution to fits"""

from __future__ import division

from scipy.stats import binned_statistic
from scipy.optimize import curve_fit
from numpy import std, sin, cos, exp, arange, array, radians

from artist import Plot

from sapphire import Station


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


def Rossi(x, A, B):
    """ Rossi: zenith angle distribution """

    rx = radians(x)
    geometry = sin(rx) * cos(rx)
    return A * geometry * cos(rx) ** B


def Iyono(x, A, B):
    """ Iyono 2007: zenith angle distribution """

    rx = radians(x)
    geometry = sin(rx) * cos(rx)
    return A * geometry * exp(-B * ((1 / cos(rx)) - 1))


def Ciampa(x, A, C, D):
    """ Ciampa 1998: zenith angle distribution """

    rx = radians(x)
    geometry = sin(rx) * cos(rx)
    return A * geometry * exp(C * (1 / cos(rx)) - D)


def ModCiampa(x, A, C):
    """ Based on Ciampa 1998: zenith angle distribution

    Positive C parameter

    """
    rx = radians(x)
    geometry = sin(rx) * cos(rx)
    return A * geometry * exp(-C * (1 / cos(rx)))


def plot_zenith(angle_centers, mean_counts, std_counts):
    fit_functions = [Rossi, Iyono, ModCiampa]
    for fit_function in fit_functions:
        popt, pcov = curve_fit(fit_function, angle_centers, mean_counts) #, sigma=std_counts)
        print popt
        plot = Plot()
        plot.scatter(angle_centers, mean_counts, yerr=std_counts)
        angles = arange(0, 90, 0.1)
        plot.plot(angles, fit_function(angles, *popt), mark=None)
        plot.set_ylabel('Counts')
        plot.set_xlabel(r'Zenith [\si{\degree}]')
        plot.save_as_pdf('zenith_distribution_%s' % fit_function.func_name)


if __name__ == "__main__":
    if 'angle_centers' not in globals():
        angle_centers, mean_counts, std_counts = get_zenith_distribution()

    plot_zenith(angle_centers, mean_counts, std_counts)
