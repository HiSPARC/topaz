import os
import itertools

import tables
from scipy.optimize import curve_fit
from scipy.stats import t, norm, tukeylambda, chi
from numpy import arange, histogram

from sapphire.simulations.showerfront import (
    FlatFrontSimulation, FlatFrontSimulationWithoutErrors,
    FlatFrontSimulation2D, FlatFrontSimulation2DWithoutErrors,
    ConeFrontSimulation)
from sapphire.clusters import BaseCluster, ScienceParkCluster, HiSPARCStations
from sapphire import ReconstructESDEvents
from sapphire.utils import gauss

from artist import Plot


PATH = '/Users/arne/Datastore/expected_dt/test_station_dt_spa.h5'


def lengthy_cluster():
    cluster = BaseCluster()
    detectors = [((0, -5, 0), 'UD'), ((0, 5, 0), 'UD')]
    for r in range(0, 1000, 100):
        cluster._add_station((r, 0, 0), 0, detectors)

    return cluster


def simulate_shower_front():
#     cluster = lengthy_cluster()
#     cluster = HiSPARCStations([504, 505])
    cluster = ScienceParkCluster()
    with tables.open_file(PATH, 'w') as data:
        sim = FlatFrontSimulation(cluster, data, '/flat', 70000)
        sim = ConeFrontSimulation(700, cluster, data, '/cone', 70000)
        sim.run()


def tl(x, loc, scale):
    return tukeylambda.pdf(x, 0.27, loc, scale)


def plot_offset_distributions():
    with tables.open_file(PATH, 'r') as data:
        station_groups = [data.get_node(sidx, 'events')
                          for sidx in data.root.flat.coincidences.s_index]
        bins = arange(-2000, 2000, 20)
        x = (bins[:-1] + bins[1:]) / 2
        for ref_events, events in itertools.combinations(station_groups, 2):
            ref_s = ref_events._v_parent._v_name[8:]
            s = events._v_parent._v_name[8:]

            dt = (ref_events.col('ext_timestamp').astype(int) -
                  events.col('ext_timestamp').astype(int))
            counts, bins = histogram(dt, bins=bins, density=True)

            plot = Plot()
            colors = (c for c in ['gray', 'lightgray', 'blue', 'red'])
            for fit_f, p0 in [(gauss, (1., 0., 30)),
                              (norm.pdf, (0., 30.)),
                              (t.pdf, (1., 0., 1.)),
                              (tl, (0., 450.))]:
                popt, pcov = curve_fit(fit_f, x, counts, p0=p0)
                plot.plot(x, fit_f(x, *popt), mark=None, linestyle=colors.next())
                if fit_f in [norm.pdf]:
                    print ref_s, s, popt[1]
            plot.histogram(counts, bins)
            plot.set_ylimits(min=0)
            plot.set_xlimits(min=-2000, max=2000)
            plot.set_xlabel(r'$\Delta t$ [\si{\ns}]')
            plot.set_ylabel('Counts')
            plot.save_as_pdf('pair_dt_%s_%s' % (ref_s, s))


if __name__ == "__main__":
    if not os.path.exists(PATH):
        simulate_shower_front()
    plot_offset_distributions()
