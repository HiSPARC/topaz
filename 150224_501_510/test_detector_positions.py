import itertools

from numpy import nan, isnan, arange, histogram, linspace, pi, array, sqrt, degrees
from scipy.optimize import curve_fit
import tables
import matplotlib.pyplot as plt

from artist import Plot, PolarPlot

from sapphire.clusters import HiSPARCStations
from sapphire.analysis.reconstructions import (ReconstructESDEvents,
                                               ReconstructESDCoincidences)

from sapphire.analysis.coincidence_queries import CoincidenceQuery
from sapphire.utils import pbar, gauss, ERR, angle_between


STATIONS = [501, 510]
COINDATA_PATH = '/Users/arne/Datastore/501_510/c_501_510_150120_150201.h5'

def reconstruct_simulations(data):

    # Station 510
    station = cluster.get_station(STATIONS[1])
    station_group = '/hisparc/cluster_amsterdam/station_%d' % station.number
    rec_510 = ReconstructESDEvents(data, station_group, station,
                                   overwrite=True, progress=True)
    rec_510.offsets = offset(station.number)
    rec_510.reconstruct_directions()

    rec_510.theta = array(rec_510.theta)
    rec_510.phi = array(rec_510.phi)

    # Station 501
    for order in itertools.permutations(range(4), 4):
        cluster = get_cluster()
        station = cluster.get_station(STATIONS[0])
        station_group = '/hisparc/cluster_amsterdam/station_%d' % station.number
        station._detectors = [station.detectors[id] for id in order]

        rec_501 = ReconstructESDEvents(data, station_group, station,
                                       overwrite=True, progress=True)
        rec_501.offsets = offset(station.number)
        rec_501.reconstruct_directions()

        rec_501.theta = array(rec_501.theta)
        rec_501.phi = array(rec_501.phi)

        high_zenith = (rec_501.theta > .2) & (rec_510.theta > .2)

        plt.figure()
        plt.hist2d(rec_501.phi.compress(high_zenith),
                   rec_510.phi.compress(high_zenith),
                   bins=linspace(-pi, pi, 100),
                   cmap='coolwarm')
        plt.show()


def offset(station):
    if station == 501:
        return [-1.064884, 0., 6.217017, 4.851398]
    elif station == 510:
        return [9.416971, 0., 9.298256, 8.447724]


def get_cluster():
    return HiSPARCStations(STATIONS)


if __name__ == '__main__':
    with tables.open_file(COINDATA_PATH, 'a') as data:
        reconstruct_simulations(data)
