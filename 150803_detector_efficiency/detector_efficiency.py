from __future__ import division

import glob
import os
from itertools import combinations

from numpy import linspace, histogram, sqrt, log10, degrees, isnan, zeros, where
import tables

from artist import Plot
from sapphire import ReconstructESDEvents, CorsikaQuery
from sapphire.utils import distance_between, angle_between


DATA = '/Users/arne/Datastore/efficiency/'
PATHS = '/Users/arne/Datastore/efficienc*/*_*.h5'
OVERVIEW = '/Users/arne/Datastore/efficiency/corsika-overview.h5'
CORE_DISTANCE_BINS = linspace(0, 500, 101)
CORE_DISTANCES = (CORE_DISTANCE_BINS[:-1] + CORE_DISTANCE_BINS[1:]) / 2

# Stations
STATION_TYPE = ['star', 'diamond', 'two', 'triangle']
STATION_NUMBER = 2


def detection_efficiency(path):
    """Calculate efficiency for a specific simulation"""

    with tables.open_file(path, 'r') as data:
        station = data.root.coincidences._v_attrs.cluster.get_station(STATION_NUMBER)
        # Coincidences detected by given station
        coincidences = data.root.coincidences.coincidences
        all_x = coincidences.col('x')
        all_y = coincidences.col('y')
        coins = coincidences.read_where('s%d' % STATION_NUMBER)
        events = data.get_node('/cluster_simulations/station_%d' % STATION_NUMBER, 'events')
        if STATION_NUMBER in [0, 3]:
            query = '(%s)' % ' & '.join('(n%d != 0)' % d for d in [1, 3, 4])  # corners
        if STATION_NUMBER in [1]:
            query = ' | '.join(['(%s)' % ' & '.join('(n%d > .3)' % d for d in ids)
                                for ids in combinations([1, 2, 3, 4], 3)]) # triangles
        if STATION_NUMBER in [2]:
            query = '(%s)' % ' & '.join('(n%d != 0)' % d for d in [1, 2])  # both detectors
        e = events.get_where_list(query)
        coins = coins[e]
        all_counts, bins = histogram(distance_between(0, 0, all_x, all_y),
                                     bins=CORE_DISTANCE_BINS)
        counts, bins = histogram(distance_between(0, 0, coins['x'], coins['y']),
                                 bins=CORE_DISTANCE_BINS)

        return counts, all_counts


def collect_efficiencies():
    """Reconstruct shower (direction) for eligible events"""
    counts = {}
    all_counts = {}
    n = {}
    cq = CorsikaQuery(OVERVIEW)
    for path in glob.glob(PATHS):
        seeds = os.path.basename(path)[:-3]
        sim = cq.get_info(seeds)
        energy = log10(sim['energy'])
        zenith = degrees(sim['zenith'])
        count, all_count = detection_efficiency(path)

        # Check if its the first of this energy
        try:
            counts[energy]
            all_counts[energy]
        except KeyError:
            counts[energy] = {}
            all_counts[energy] = {}

        # Check if its the first of this energy and zenith
        try:
            counts[energy][zenith] += count
            all_counts[energy][zenith] += all_count
        except KeyError:
            counts[energy][zenith] = count
            all_counts[energy][zenith] = all_count
    cq.finish()

    efficiencies = {}
    errors = {}
    for e in counts.keys():
        efficiencies[e] = {}
        errors[e] = {}
        for z in counts[e].keys():
            efficiencies[e][z] = counts[e][z] / all_counts[e][z]
            errors[e][z] = sqrt(counts[e][z] + 1) / all_counts[e][z]

    return efficiencies, errors


def plot_effiencies():
    efficiencies, errors = collect_efficiencies()

    for energy in efficiencies.keys():
        plot = Plot('semilogx')
        for i, zenith in enumerate(sorted(efficiencies[energy].keys())):
            if any(abs(zenith - z) < 0.1 for z in [0, 22.5, 37.5]):
                plot.plot(CORE_DISTANCES, efficiencies[energy][zenith],
#                           yerr=errors[energy][zenith],
                          markstyle='mark size=1pt', linestyle='blue')
                plot.add_pin(str(zenith), x=15, use_arrow=True)
            else:
                plot.plot(CORE_DISTANCES, efficiencies[energy][zenith], mark=None)
        plot_david_data(plot)
        plot.set_ylabel('Efficiency')
        plot.set_ylimits(min=0, max=1.02)
        plot.set_xlimits(min=2, max=500)
        plot.set_xlabel('Core distance')
        plot.save_as_pdf('efficiency_%s_%.1f.pdf' % (STATION_TYPE[STATION_NUMBER], energy))


def plot_david_data(plot):
    """For comparison with figure 4.6 from Fokkema2012

    At least 1 particle in each corner detector, for a 1 PeV proton shower.
    At 0, 22.5, and 35 degrees zenith.

    Source: DIR-plot_detection_efficiency_vs_R_for_angles-1.tex

    """
    plot.plot(*zip((2.6315, 0.9995), (7.8947, 0.9947), (13.157, 0.9801),
                   (18.421, 0.9382), (23.684, 0.8653), (28.947, 0.7636),
                   (34.210, 0.6515), (39.473, 0.5313), (44.736, 0.4243),
                   (50.000, 0.3287), (55.263, 0.2467), (60.526, 0.1798),
                   (65.789, 0.1270), (71.052, 0.0898), (76.315, 0.0624),
                   (81.578, 0.0445), (86.842, 0.0301), (92.105, 0.0220),
                   (97.368, 0.0153)), linestyle='red', markstyle='mark size=1pt')
    plot.plot(*zip((2.6315, 0.9642), (7.8947, 0.9242), (13.157, 0.8459),
                   (18.421, 0.7405), (23.684, 0.6224), (28.947, 0.4870),
                   (34.210, 0.3705), (39.473, 0.2668), (44.736, 0.1909),
                   (50.000, 0.1269), (55.263, 0.0833), (60.526, 0.0533),
                   (65.789, 0.0366), (71.052, 0.0243), (76.315, 0.0161),
                   (81.578, 0.0115), (86.842, 0.0079), (92.105, 0.0047),
                   (97.368, 0.0034)), linestyle='red', markstyle='mark size=1pt')
    plot.plot(*zip((2.6315, 0.7180), (7.8947, 0.6214), (13.157, 0.4842),
                   (18.421, 0.3441), (23.684, 0.2296), (28.947, 0.1414),
                   (34.210, 0.0882), (39.473, 0.0513), (44.736, 0.0317),
                   (50.000, 0.0193), (55.263, 0.0109), (60.526, 0.0071),
                   (65.789, 0.0043), (71.052, 0.0029), (76.315, 0.0021),
                   (81.578, 0.0012), (86.842, 0.0009), (92.105, 0.0006),
                   (97.368, 0.0005)), linestyle='red', markstyle='mark size=1pt')


if __name__ == "__main__":
#     reconstruct()
    for i in range(4):
        STATION_NUMBER = i
        plot_effiencies()
