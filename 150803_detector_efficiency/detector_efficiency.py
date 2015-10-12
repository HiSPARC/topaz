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
PATHS = '/Users/arne/Datastore/efficiency/*_*.h5'
OVERVIEW = '/Users/arne/Datastore/efficiency/corsika-overview.h5'
CORE_DISTANCE_BINS = linspace(0, 500, 100)
CORE_DISTANCES = (CORE_DISTANCE_BINS[:-1] + CORE_DISTANCE_BINS[1:]) / 2
STATION_NUMBER = 0


def detection_efficiency(path):
    """Calculate efficiency for a specific simulation"""

    with tables.open_file(path, 'r') as data:
        station = data.root.coincidences._v_attrs.cluster.get_station(STATION_NUMBER)
        # Coincidences detected by given station
        coincidences = data.root.coincidences.coincidences
        print '-', log10(coincidences[0]['energy']), degrees(coincidences[0]['zenith'])
        all_x = coincidences.col('x')
        all_y = coincidences.col('y')
        coins = coincidences.read_where('s%d' % STATION_NUMBER)
        events = data.get_node('/cluster_simulations/station_%d' % STATION_NUMBER, 'events')
        query = '(%s)' % ' & '.join('(n%d != 0)' % d for d in [1, 3, 4])  # corners
        # query = ' | '.join(['(%s)' % ' & '.join('(n%d > .3)' % d for d in ids) for ids in combinations([1, 2, 3, 4], 3)]) # triangles
        e = events.get_where_list(query)
        coins = coins[e]
        all_counts, bins = histogram(distance_between(0, 0, all_x, all_y),
                                     bins=CORE_DISTANCE_BINS)
        counts, bins = histogram(distance_between(0, 0, coins['x'], coins['y']),
                                 bins=CORE_DISTANCE_BINS)
        efficiency = counts / all_counts
        efficiency = where(isnan(efficiency), 0, efficiency)
        return efficiency


def collect_efficiencies():
    """Reconstruct shower (direction) for eligible events"""
    efficiencies = {}
    n = {}
    cq = CorsikaQuery(OVERVIEW)
    for path in glob.glob(PATHS):
        seeds = os.path.basename(path)[:-3]
        sim = cq.get_info(seeds)
        energy = log10(sim['energy'])
        zenith = degrees(sim['zenith'])
        print '+', energy, zenith
        efficiency = detection_efficiency(path)

        # Check if its the first of this energy
        try:
            efficiencies[energy]
        except KeyError:
            efficiencies[energy] = {}
            n[energy] = {}

        # Check if its the first of this energy and zenith
        try:
            efficiencies[energy][zenith] += efficiency
            n[energy][zenith] += 1
        except KeyError:
            efficiencies[energy][zenith] = efficiency
            n[energy][zenith] = 1
    cq.finish()

    for e in efficiencies.keys():
        for z in efficiencies[e].keys():
            efficiencies[e][z] /= n[e][z]

    return efficiencies


def plot_effiencies():
    efficiencies = collect_efficiencies()
    print efficiencies.keys()
    print efficiencies[15].keys()

    for energy in efficiencies.keys():
        plot = Plot('semilogx')
        for zenith in efficiencies[energy].keys():
            if zenith in [0, 22.5, 37.5]:
                plot.plot(CORE_DISTANCES, efficiencies[energy][zenith], linestyle='blue')
                plot.add_pin(str(zenith), x=15, use_arrow=True)
            else:
                plot.plot(CORE_DISTANCES, efficiencies[energy][zenith], mark=None)
        plot_david_data(plot)
        plot.set_ylabel('Efficiency')
        plot.set_ylimits(min=0, max=1.02)
        plot.set_xlimits(min=1, max=500)
        plot.set_xlabel('Core distance')
        plot.save_as_pdf('efficiency_%.1f.pdf' % energy)


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
                   (97.368, 0.0153)), linestyle='red')
    plot.plot(*zip((2.6315, 0.9642), (7.8947, 0.9242), (13.157, 0.8459),
                   (18.421, 0.7405), (23.684, 0.6224), (28.947, 0.4870),
                   (34.210, 0.3705), (39.473, 0.2668), (44.736, 0.1909),
                   (50.000, 0.1269), (55.263, 0.0833), (60.526, 0.0533),
                   (65.789, 0.0366), (71.052, 0.0243), (76.315, 0.0161),
                   (81.578, 0.0115), (86.842, 0.0079), (92.105, 0.0047),
                   (97.368, 0.0034)), linestyle='red')
    plot.plot(*zip((2.6315, 0.7180), (7.8947, 0.6214), (13.157, 0.4842),
                   (18.421, 0.3441), (23.684, 0.2296), (28.947, 0.1414),
                   (34.210, 0.0882), (39.473, 0.0513), (44.736, 0.0317),
                   (50.000, 0.0193), (55.263, 0.0109), (60.526, 0.0071),
                   (65.789, 0.0043), (71.052, 0.0029), (76.315, 0.0021),
                   (81.578, 0.0012), (86.842, 0.0009), (92.105, 0.0006),
                   (97.368, 0.0005)), linestyle='red')


if __name__ == "__main__":
#     reconstruct()
    plot_effiencies()
