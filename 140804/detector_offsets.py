""" Determine detector offset distrobution

This determines the detector offsets for all stations in an ESD datafile.
These offsets are then fitted and the results are shown.

Having run this script on several datasets the expected distribution
has a mean of 0 ns and a sigma of 2.7 ns.

"""
import tables
import matplotlib.pyplot as plt
from numpy import histogram, arange
from scipy.optimize import curve_fit

from sapphire.analysis.reconstructions import ReconstructESDCoincidences
from sapphire.utils import gauss


def determine_offset(dirrec, s_path):
    station_number = int(s_path.split('station_')[-1])
    station_group = dirrec.data.get_node(s_path)
    offsets = [offset for offset in dirrec.determine_detector_timing_offsets(station_group)
               if offset != 0.0]
    return offsets


def determine_offsets(data):
    detector_offsets = []
    dirrec = ReconstructESDCoincidences(data)
    for s_path in dirrec.coincidences_group.s_index:
        detector_offsets.extend(determine_offset(dirrec, s_path))
    return detector_offsets


def fit_offsets(offsets):
    bins = arange(-40 + 1.25, 40, 2.5)
    y, bins = histogram(offsets, bins=bins)
    x = (bins[:-1] + bins[1:]) / 2
    popt, pcov = curve_fit(gauss, x, y, p0=(len(offsets), 0., 2.5))
    return x, y, popt


def plot_fit(x, y, popt):
    plt.step(x, y, where='mid')
    plt.plot(x, gauss(x, *popt))
    plt.show()


if __name__ == '__main__':
    data_path = '/Users/arne/Datastore/esd/2014/1/2014_1_1.h5'
    with tables.open_file(data_path, 'r') as data:
        offsets = determine_offsets(data)
    x, y, popt = fit_offsets(offsets)
    print 'sigma: ', popt[2]
    plot_fit(x, y, popt)
