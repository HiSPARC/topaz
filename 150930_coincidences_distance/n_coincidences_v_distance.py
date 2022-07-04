""" Coincidence rate as function of distance

This script downloads coincidences for all station pairs which have a certain
distance to eachother (between 50 and 2000 m). It specifically downloads for
timestamp ranges for which both have event data.

Then the coincidence rate is determined from the total time both had data and
the number of found coincidences. This is then plotted against the distance
between the stations.

"""


import os
import warnings

from functools import partial

import tables

from numpy import cos, exp, interp, load, log10, logspace, pi, radians, savez, sqrt, sum, where
from scipy.optimize import curve_fit

from artist import Plot

from sapphire import HiSPARCNetwork
from sapphire.utils import pbar

from energy_sensitivity import get_pair_distance_energy_array
from station_distances import close_pairs_in_network
from variable_distance import min_max_distance_pair

DATAPATH = '/Users/arne/Datastore/pairs/%d_%d.h5'
NO_LAYOUT = [2, 3, 5, 7, 10, 13, 21, 22, 101, 103, 202, 203,
             301, 303, 304, 305, 401, 1001, 1002, 1003, 1006, 1007, 1008, 1010,
             2001, 2002, 2003, 2004, 2005, 2008, 2010, 2101, 2102, 2103, 2201,
             3001, 3002, 3101, 3102, 3103, 3104, 3105, 3202, 3203, 3301, 3302,
             3303, 3401, 3501, 3601,
             4001, 4002, 4003, 4004, 7101, 7201, 7301, 7401,
             8001, 8002, 8004, 8005, 8006, 8007, 8008, 8009, 8102, 8103, 8104,
             8105, 8201, 8301, 8302, 8303,
             13001, 13002, 13003, 13004, 13005, 13006, 13007, 13008, 13101,
             13103, 13104, 13201, 13301, 13501, 14002, 14003,
             20001, 20002, 20003]


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
        bad_stations = [22, 507, 1001, 2103, 13007, 20001, 20002, 20003]
        if pair[0] in bad_stations or pair[1] in bad_stations:
            continue

        with tables.open_file(path, 'r') as data:
            try:
                total_exposure = data.get_node_attr('/', 'total_exposure')
                distance = network.calc_distance_between_stations(*pair)
                n_rate = data.get_node_attr('/', 'n_rate')
                interval_rate = data.get_node_attr('/', 'interval_rate')
                n_coincidences = data.get_node_attr('/', 'n_coincidences')
            except AttributeError:
                # print 'failed reading attributes', pair
                continue
        if not n_coincidences:
            continue
        if n_coincidences < 5:
            # Exclude pairs with very few coincidences
            continue
        n = (len(network.get_station(pair[0]).detectors) +
             len(network.get_station(pair[1]).detectors))
        distances[n].append(distance)
        # Distance error due to unknown detector locations or moving stations
        if pair[0] in NO_LAYOUT and pair[1] in NO_LAYOUT:
            gps_layout_error = 20
        elif pair[0] in NO_LAYOUT or pair[1] in NO_LAYOUT:
            gps_layout_error = 10
        else:
            gps_layout_error = 3
        distance_error = [abs(d - distance) + gps_layout_error
                          for d in min_max_distance_pair(pair)]
        if distance_error[0] > distance:
            distance_error[0] = distance - 1e-15
        distance_errors[n].append(distance_error)

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


def expected_rate(distances, coincidence_rates, background,
                  sim_distances, sim_energies, sim_areas, n=8):
    """Rough estimation of expected rate"""

    # Differential flux
    refr = 1e13
    slope = -2.7
    sim_dif_flux = (sim_energies / refr) ** slope
    knee = 3e15
    slope1 = -3.0
    bend = (knee / refr) ** slope
    sim_dif_flux = where(sim_energies <= knee, sim_dif_flux,
                         (sim_energies / knee) ** slope1 * bend)
    knee2 = 3e17
    slope2 = -3.3
    bend *= (knee2 / knee) ** slope1
    sim_dif_flux = where(sim_energies <= knee2, sim_dif_flux,
                         (sim_energies / knee2) ** slope2 * bend)
    ankle = 3e18
    slope3 = -2.6
    bend *= (ankle / knee2) ** slope2
    sim_dif_flux = where(sim_energies <= ankle, sim_dif_flux,
                         (sim_energies / ankle) ** slope3 * bend)

    # Simplified flux
    sim_dif_flux = sim_energies ** slope / sum(sim_energies ** slope)

    # Energy dependend scaling, smaller solid angle for low energy showers
    max_zenith = log10(log10(sim_energies) - 12) ** 0.7

#     f = max(0, min(1, 1.205 * log10(E) - 14.76 - 2.52 / cos(theta)))
# #     solid_angle = 2 * pi * int(0, pi/2) f(theta) * cos(theta) * sin(theta) * dtheta

    zenith = radians(60)

    sim_solid_angle = 2 * pi * (1 - cos(zenith))

    sim_rates = (sim_areas * sim_energies * sim_solid_angle * sim_dif_flux
                 ).sum(axis=1)

    scaling = partial(scale_rate, sim_distances, sim_rates, background)
    popt, pcov = curve_fit(scaling, distances, log10(coincidence_rates), [1.])
    print(n, popt)

    return popt[0] * sim_rates + background


def scale_rate(sim_distances, sim_rates, background, x, N):
    return log10(N * interp(x, sim_distances, sim_rates) + background)


def P(detector_density):
    """Chance of at least one particle in detector"""

    return 1.0 - P0(detector_density)


def P0(detector_density):
    """Chance of detecting no particle in a detector"""

    return exp(-detector_density / 2.0)


def plot_coincidence_rate_distance(data, sim_data):
    """Plot results

    :param distances: dictionary with occuring distances for different
                      combinations of number of detectors.
    :param coincidence_rates: dictionary of occuring coincidence rates for
                              different combinations of number of detectors.
    :param rate_errors: errors on the coincidence rates.

    """
    (distances, coincidence_rates, interval_rates,
     distance_errors, rate_errors, pairs) = data
    sim_distances, sim_energies, sim_areas = sim_data
    markers = {4: 'o', 6: 'triangle', 8: 'square'}
    colors = {4: 'red', 6: 'black!50!green', 8: 'black!20!blue'}

    coincidence_window = 10e-6  # seconds
    freq_2 = 0.3
    freq_4 = 0.6
    background = {4: 2 * freq_2 * freq_2 * coincidence_window,
                  6: 2 * freq_2 * freq_4 * coincidence_window,
                  8: 2 * freq_4 * freq_4 * coincidence_window}

    for rates, name in [(coincidence_rates, 'coincidence'),
                        (interval_rates, 'interval')]:
        plot = Plot('loglog')
        for n in list(distances.keys()):
            plot.draw_horizontal_line(background[n], 'dashed,' + colors[n])

#         for n in distances.keys():
        for n in [4, 8]:
            expected_rates = expected_rate(distances[n], rates[n],
                                           background[n], sim_distances,
                                           sim_energies, sim_areas[n], n=n)
            plot.plot(sim_distances, expected_rates, linestyle=colors[n],
                      mark=None, markstyle='mark size=0.5pt')

        for n in list(distances.keys()):
            plot.scatter(distances[n], rates[n],
                         xerr=distance_errors[n], yerr=rate_errors[n],
                         mark=markers[n],
                         markstyle='%s, mark size=.75pt' % colors[n])
        plot.set_xlabel(r'Distance between stations [\si{\meter}]')
        plot.set_ylabel(r'%s rate [\si{\hertz}]' % name.title())
        plot.set_axis_options('log origin y=infty')
        plot.set_xlimits(min=1, max=20e3)
        plot.set_ylimits(min=1e-7, max=5e-1)
        plot.save_as_pdf('distance_v_%s_rate' % name)


def plot_coincidence_v_interval_rate(data):
    """Plot results

    :param distances: dictionary with occuring distances for different
                      combinations of number of detectors.
    :param coincidence_rates: dictionary of occuring coincidence rates for
                              different combinations of number of detectors.
    :param rate_errors: errors on the coincidence rates.

    """
    (distances, coincidence_rates, interval_rates,
     distance_errors, rate_errors, pairs) = data
    markers = {4: 'o', 6: 'triangle', 8: 'square'}
    colors = {4: 'red', 6: 'black!50!green', 8: 'black!20!blue'}
    plot = Plot('loglog')

    plot.plot([1e-7, 1e-1], [1e-7, 1e-1], mark=None)
    for n in list(distances.keys()):
        plot.scatter(interval_rates[n], coincidence_rates[n],
                     yerr=rate_errors[n], mark=markers[n],
                     markstyle='%s, thin, mark size=.75pt' % colors[n])

    plot.set_xlabel(r'Rate based on coincidence intervals [\si{\hertz}]')
    plot.set_ylabel(r'Rate based on coincidences and exposure [\si{\hertz}]')
    plot.set_axis_options('log origin y=infty')
    plot.set_xlimits(min=1e-7, max=1e-1)
    plot.set_ylimits(min=1e-7, max=1e-1)
    plot.save_as_pdf('interval_v_coincidence_rate')


if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            saved_data = load('simulated_rates.npz')
            sim_distances = saved_data['sim_data'][0]
            sim_energies = saved_data['sim_data'][1]
            sim_areas = saved_data['sim_data'][2]
            sim_data = (sim_distances, sim_energies, sim_areas)
        except:
            sim_distances = logspace(log10(1), log10(20e3), 200)
            sim_energies = logspace(13, 20, 200)
            sim_areas = {n: get_pair_distance_energy_array(sim_distances,
                                                           sim_energies, n=n)
                         for n in [4, 8]}
            sim_data = (sim_distances, sim_energies, sim_areas)
            savez('simulated_rates.npz', sim_data=sim_data)

        if 'data' not in globals():
            close_pairs = close_pairs_in_network(min=0, max=15e3)
            data = get_coincidence_count(close_pairs)

    plot_coincidence_rate_distance(data, sim_data)
    plot_coincidence_v_interval_rate(data)
