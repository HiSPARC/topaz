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
from sapphire import download_coincidences, HiSPARCNetwork
from sapphire.utils import pbar
from sapphire.transformations.clock import gps_to_datetime
from sapphire.simulations.ldf import KascadeLdf

from eventtime_ranges import get_timestamp_ranges, get_total_exposure
from station_distances import close_pairs_in_network, distance_between_stations

DATAPATH = '/Users/arne/Datastore/pairs/%d_%d.h5'


def download_pair_coincidences(close_pairs):
    for pair in pbar(close_pairs):
        path = DATAPATH % tuple(pair)
        if os.path.exists(path):
            continue
        else:
            print pair
            raise Exception
        distance = distance_between_stations(*pair)
        timestamp_ranges = get_timestamp_ranges(pair)
        total_exposure = get_total_exposure(timestamp_ranges)
        with tables.open_file(path, 'w') as data:
            for ts_start, ts_end in timestamp_ranges:
                print ts_start, ts_end
                download_coincidences(data, stations=list(pair),
                                      start=gps_to_datetime(ts_start),
                                      end=gps_to_datetime(ts_end),
                                      progress=False)
            data.set_node_attr('/', 'total_exposure', total_exposure)
            data.set_node_attr('/', 'distance', distance)


def get_coincidence_count(close_pairs):
    network = HiSPARCNetwork()
    distances = {4: [], 6: [], 8: []}
    coincidence_rates = {4: [], 6: [], 8: []}
    coincidence_rates_err = {4: [], 6: [], 8: []}
    for pair in pbar(close_pairs, show=True):
        path = DATAPATH % tuple(pair)
        if not os.path.exists(path):
            continue
        # Do not plot points for stations with known issues
        bad_stations = [22, 507, 2103, 13007, 20001]
        if pair[0] in bad_stations or pair[1] in bad_stations:
            continue
        with tables.open_file(path, 'r') as data:
            total_exposure = data.get_node_attr('/', 'total_exposure')
            distance = data.get_node_attr('/', 'distance')
            try:
                n_coincidences = data.root.coincidences.coincidences.nrows
            except tables.NoSuchNodeError:
                continue
            if not n_coincidences:
                continue
        n = (len(network.get_station(pair[0]).detectors) +
             len(network.get_station(pair[1]).detectors))
        distances[n].append(distance)
        rate = n_coincidences / total_exposure
        coincidence_rates[n].append(rate)
        err = sqrt(n_coincidences + 1) / total_exposure
        # Prevent plotting issue due to log scale
        if err > rate:
            err = rate - 1e-15
        coincidence_rates_err[n].append(err)

    return distances, coincidence_rates, coincidence_rates_err


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


def plot_coincidence_rate_distance(distances, coincidence_rates, rate_errors):
    markers = {4: 'o', 6: 'triangle', 8: 'square'}
    colors = {4: 'red', 6: 'black!50!green', 8: 'black!20!blue'}
    plot = Plot('loglog')

    freq_2 = .3
    freq_4 = .6
    background = {4: 2 * freq_2 ** 2 * 2e-6,
                  6: 2 * freq_2 * freq_4 * 2e-6,
                  8: 2 * freq_4 ** 2 * 2e-6}

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
        plot.scatter([d / 1e3 for d in distances[n]], coincidence_rates[n], yerr=rate_errors[n],
                     mark=markers[n], markstyle='%s, mark size=.75pt' % colors[n])
    plot.set_xlabel(r'Distance between stations [\si{\kilo\meter}]')
    plot.set_ylabel(r'Coincidence rate [\si{\hertz}]')
    plot.set_axis_options('log origin y=infty')
    plot.set_xlimits(min=40 / 1e3, max=2e4 / 1e3)
    plot.set_ylimits(min=1e-7, max=1e-1)
    plot.save_as_pdf('distance_v_coincidence_rate')


if __name__ == "__main__":
    if 'rates' not in globals():
        close_pairs = close_pairs_in_network(min=45, max=2e3)
        close_pairs += close_pairs_in_network(min=9e3, max=1e4)
        close_pairs += close_pairs_in_network(min=1.2e4, max=1.5e4)

#         download_pair_coincidences(close_pairs)
        distances, rates, rate_errors = get_coincidence_count(close_pairs)

    plot_coincidence_rate_distance(distances, rates, rate_errors)
