""" Coincidence rate as function of distance

This script downloads coincidences for all station pairs which have a certain
distance to eachother (between 50 and 2000 m). It specifically downloads for
timestamp ranges for which both have event data.

Then the coincidence rate is determined from the total time both had data and
the number of found coincidences. This is then plotted against the distance
between the stations.

"""
from __future__ import division

import os

import tables
from artist import Plot
from numpy import array, sqrt, logspace, log10, exp, sum, zeros, interp
from scipy.optimize import curve_fit

from sapphire import HiSPARCNetwork
from sapphire.utils import pbar
from sapphire.simulations.ldf import KascadeLdf

from station_distances import close_pairs_in_network


DATAPATH = '/Users/arne/Datastore/pairs/%d_%d.h5'
NO_LAYOUT = [2, 3, 5, 7, 10, 13, 21, 22, 23, 101, 103, 202, 203, 301, 303, 304,
             305, 401, 601, 1001, 1002, 1003, 1006, 1007, 1008, 1010, 2001,
             2002, 2003, 2004, 2005, 2006, 2008, 2010, 2101, 2102, 2103, 2201,
             3001, 3002, 3101, 3102, 3103, 3104, 3105, 3202, 3203, 3301, 3302,
             3303, 3401, 3501, 3601, 4001, 4002, 4003, 4004, 7001, 7002, 7003,
             7101, 7201, 7301, 7401, 8001, 8002, 8004, 8005, 8006, 8007, 8008,
             8009, 8102, 8103, 8104, 8105, 8201, 8301, 8302, 8303, 13001,
             13002, 13003, 13004, 13005, 13006, 13007, 13008, 13101, 13103,
             13104, 13201, 13301, 13501, 14002, 14003, 20001, 20002, 20003]


def get_coincidence_count(close_pairs):
    network = HiSPARCNetwork(force_stale=True)
    distances = {4: [], 6: [], 8: []}
    distance_errors = {4: [], 6: [], 8: []}
    coincidence_rates = {4: [], 6: [], 8: []}
    interval_rates = {4: [], 6: [], 8: []}
    coincidence_rate_errors = {4: [], 6: [], 8: []}
    pairs = {4: [], 6: [], 8: []}
    for pair in pbar(close_pairs, show=True):
        path = DATAPATH % tuple(pair)
        if not os.path.exists(path):
            continue
        # Do not plot points for stations with known issues
        bad_stations = [22, 507, 1001, 2103, 13007, 20001]
        if pair[0] in bad_stations or pair[1] in bad_stations:
            continue

        with tables.open_file(path, 'r') as data:
            try:
                total_exposure = data.get_node_attr('/', 'total_exposure')
                distance = data.get_node_attr('/', 'distance')
                n_rate = data.get_node_attr('/', 'n_rate')
                interval_rate = data.get_node_attr('/', 'interval_rate')
            except AttributeError:
                continue
            try:
                n_coincidences = data.root.coincidences.coincidences.nrows
            except tables.NoSuchNodeError:
                continue
            if not n_coincidences:
                continue
        n = (len(network.get_station(pair[0]).detectors) +
             len(network.get_station(pair[1]).detectors))
        distances[n].append(distance)
        # Distance error due to unknown detector locations
        if pair[0] in NO_LAYOUT and pair[1] in NO_LAYOUT:
            distance_errors[n].append(20e-3)
        else:
            distance_errors[n].append(5e-3)

        coincidence_rates[n].append(n_rate)
        interval_rates[n].append(interval_rate)
        err = sqrt(n_coincidences + 1) / total_exposure
        # Prevent plotting issue due to log scale
        rate = n_rate
        if err > rate:
            err = rate - 1e-15
        coincidence_rate_errors[n].append(err)
        pairs[n].append(pair)

    return (distances, coincidence_rates, interval_rates,
            distance_errors, coincidence_rate_errors, pairs)


def slope(x, N, s):
    return N * exp(-s * x)


def expected_rate(real_distances, real_coincidence_rates, background, n=8):
    """Rough estimation of expected rate"""

    distances = logspace(log10(45), log10(2e4), 200)
    energies = logspace(13, 20, 200)
    ldf = KascadeLdf()
    rates = zeros(len(distances))
    slope = -.95  # why this value?

    for energy in energies:
        size = 10 ** (log10(energy) - 15 + 4.8)

        # Relative occurance as function of the energy
        relative_flux = energy ** slope / sum(energies ** slope)

        # density in the stations if the shower hits between them
        densities = ldf.calculate_ldf_value(distances / 2., Ne=size)
        # probability for single detectors
        p = P(densities)
        p0 = P0(densities)
        # probability for at least 2 detectors in a station is
        # \sum_{k=2}^{n} (^n_k) P^k P_0^{n-k}
        p_4 = 6 * p ** 2 * p0 ** 2 + 4 * p ** 3 * p0 + p ** 4
        p_2 = p ** 2
        # probability for both stations
        if n == 4:
            detection_probability = p_2 ** 2
        elif n == 6:
            detection_probability = p_2 * p_4
        elif n == 8:
            detection_probability = p_4 ** 2

        rates += relative_flux * detection_probability

    real_distances = array(real_distances)
    r_coincidence_rates = array(real_coincidence_rates).compress(real_distances < 700)
    r_distances = real_distances.compress(real_distances < 700)

    scaling = lambda x, N: log10(N * interp(x, distances, rates) + background)
    popt, pcov = curve_fit(scaling, r_distances, log10(r_coincidence_rates), [1.])
    print n, popt

    return distances, popt[0] * rates + background


def P(detector_density):
    """Chance of at least one particle in detector"""

    return 1.0 - P0(detector_density)


def P0(detector_density):
    """Chance of detecting no particle in a detector"""

    return exp(-detector_density / 2.0)


def plot_coincidence_rate_distance(distances, coincidence_rates, interval_rates,
                                   distance_errors, rate_errors, pairs):
    """Plot results

    :param distances: dictionary with occuring distances for different
                      combinations of number of detectors.
    :param coincidence_rates: dictionary of occuring coincidence rates for
                              different combinations of number of detectors.
    :param rate_errors: errors on the coincidence rates.

    """
    markers = {4: 'o', 6: 'triangle', 8: 'square'}
    colors = {4: 'red', 6: 'black!50!green', 8: 'black!20!blue'}

    coincidence_window = 10e-6  # seconds
    freq_2 = 0.3
    freq_4 = 0.6
    background = {4: 2 * freq_2 * freq_2 * coincidence_window,
                  6: 2 * freq_2 * freq_4 * coincidence_window,
                  8: 2 * freq_4 * freq_4 * coincidence_window}

    plot = Plot('loglog')
    for n in distances.keys():
        plot.draw_horizontal_line(background[n], 'dashed,thin,' + colors[n])

    for n in distances.keys():
        expected_distances, expected_rates = expected_rate(distances[n],
                                                           coincidence_rates[n],
                                                           background[n],
                                                           n=n)
        plot.plot(expected_distances / 1e3, expected_rates,
                  linestyle=colors[n], mark=None, markstyle='mark size=.5pt')

    for n in distances.keys():
        plot.scatter([d / 1e3 for d in distances[n]], coincidence_rates[n],
                     xerr=distance_errors[n], yerr=rate_errors[n],
                     mark=markers[n], markstyle='%s, mark size=.75pt' % colors[n])
    plot.set_xlabel(r'Distance between stations [\si{\kilo\meter}]')
    plot.set_ylabel(r'Coincidence rate [\si{\hertz}]')
    plot.set_axis_options('log origin y=infty')
    plot.set_xlimits(min=40 / 1e3, max=2e4 / 1e3)
    plot.set_ylimits(min=1e-7, max=1e-1)
    plot.save_as_pdf('distance_v_coincidence_rate')


def plot_coincidence_v_interval_rate(distances, coincidence_rates, interval_rates,
                                     distance_errors, rate_errors, pairs):
    """Plot results

    :param distances: dictionary with occuring distances for different
                      combinations of number of detectors.
    :param coincidence_rates: dictionary of occuring coincidence rates for
                              different combinations of number of detectors.
    :param rate_errors: errors on the coincidence rates.

    """
    markers = {4: 'o', 6: 'triangle', 8: 'square'}
    colors = {4: 'red', 6: 'black!50!green', 8: 'black!20!blue'}
    plot = Plot('loglog')

    plot.plot([1e-7, 1e-1], [1e-7, 1e-1], mark=None)
    for n in distances.keys():
        plot.scatter(interval_rates[n], coincidence_rates[n],
                     yerr=rate_errors[n], mark=markers[n],
                     markstyle='%s, thin, mark size=.75pt' % colors[n])

    plot.set_xlabel(r'Rate based on fitted coincidence intervals [\si{\hertz}]')
    plot.set_ylabel(r'Rate based on number of coincidences and exposure [\si{\hertz}]')
    plot.set_axis_options('log origin y=infty')
    plot.set_xlimits(min=1e-7, max=1e-1)
    plot.set_ylimits(min=1e-7, max=1e-1)
    plot.save_as_pdf('interval_v_coincidence_rate')


if __name__ == "__main__":
    if 'data' not in globals():
        close_pairs = close_pairs_in_network(min=30, max=15e3)
        data = get_coincidence_count(close_pairs)
    plot_coincidence_rate_distance(*data)
    plot_coincidence_v_interval_rate(*data)
