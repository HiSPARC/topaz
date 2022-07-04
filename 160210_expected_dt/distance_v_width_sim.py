"""Width of dt distribution vs distance

Used to compare data to a simulation.

"""
import itertools

import tables

from numpy import arange, histogram, linspace, std
from scipy.optimize import curve_fit
from scipy.stats import norm

from artist import Plot

PATH = '/Users/arne/Datastore/expected_dt/test_station_dt_spa.h5'


def lin(x, a, b):
    return x * a + b


def plot_distance_width():

    distances = []
    widths = []

    with tables.open_file(PATH, 'r') as data:
        cluster = data.root.coincidences._v_attrs.cluster
        station_groups = [(id, data.get_node(sidx, 'events')) for id, sidx in enumerate(data.root.coincidences.s_index)]
        bins = arange(-2000, 2000, 20)
        for ref, other in itertools.combinations(station_groups, 2):
            ref_id, ref_events = ref
            id, events = other
            distances.append(cluster.calc_rphiz_for_stations(ref_id, id)[0])

            dt = ref_events.col('ext_timestamp').astype(int) - events.col('ext_timestamp').astype(int)
            pre_width = std(dt)
            counts, bins = histogram(dt, bins=linspace(-1.8 * pre_width, 1.8 * pre_width, 100), density=True)
            x = (bins[:-1] + bins[1:]) / 2
            popt, pcov = curve_fit(norm.pdf, x, counts, p0=(0.0, distances[-1]))
            widths.append(popt[1])
            print(std(dt), popt[1])

    popt, pcov = curve_fit(lin, distances, widths, p0=(1.1, 1))
    print(popt, pcov)

    plot = Plot()
    plot.scatter(distances, widths)
    plot.plot([0, 600], [0, 600 / 0.3], mark=None, linestyle='gray')
    plot.plot([0, 600], [lin(0, *popt), lin(600, *popt)], mark=None)
    plot.set_xlimits(min=0, max=600)
    plot.set_ylimits(min=0, max=700)
    plot.set_xlabel(r'Distance [\si{\meter}]')
    plot.set_ylabel(r'Width of dt distribution [\si{\ns}]')
    plot.save_as_pdf('plots/distance_v_width_pr')


if __name__ == "__main__":
    plot_distance_width()
