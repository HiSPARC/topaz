import itertools
from datetime import datetime

from numpy import linspace, pi, array, histogram2d
import tables

from artist import Plot

from sapphire import (HiSPARCStations, ReconstructESDEvents,
                      download_coincidences, Station)


STATIONS = [507, 510]
COINDATA_PATH = '/Users/arne/Datastore/507_510/c_507_510.h5'
START = datetime(2015, 10, 1)
END = datetime(2015, 12, 1)
REC_PATH = 'recs_013_%d%d%d%d'


def download_data(data):
    download_coincidences(data, stations=STATIONS, start=START, end=END)


def reconstruct_events(data):

    # Station 510
    cluster = get_cluster()
    station = cluster.get_station(STATIONS[1])
    station_group = '/hisparc/cluster_amsterdam/station_%d' % station.number
    rec_510 = ReconstructESDEvents(data, station_group, station,
                                   overwrite=True, progress=True)
    rec_510.prepare_output()
    rec_510.offsets = Station(station.number)
    rec_510.reconstruct_directions()
    rec_510.store_reconstructions()

    rec_510.theta = array(rec_510.theta)
    rec_510.phi = array(rec_510.phi)

    # Station 507
    for order in itertools.permutations(range(4), 4):
        cluster = get_cluster()
        station = cluster.get_station(STATIONS[0])
        station_group = '/hisparc/cluster_amsterdam/station_%d' % station.number
        station._detectors = [station.detectors[id] for id in order]

        rec_507 = ReconstructESDEvents(data, station_group, station,
                                       overwrite=True, progress=True,
                                       destination=REC_PATH % order)
        rec_507.prepare_output()
        rec_507.offsets = Station(station.number)
        rec_507.reconstruct_directions(detector_ids=[order[0], order[1], order[3]])
        rec_507.store_reconstructions()


def get_cluster():
    return HiSPARCStations(STATIONS)


def plot_comparisons(data):
    multi_cidx = data.root.coincidences.coincidences.get_where_list('N > 2')
    c_idx = data.root.coincidences.c_index[multi_cidx]

    min_zenith = 0.2
    r510 = data.get_node('/hisparc/cluster_amsterdam/station_510/',
                         'reconstructions')
    subset510 = [True] * r510.nrows
    id510 = next(i for i, s in enumerate(data.root.coincidences.s_index[:])
                 if s.endswith('_510'))
    for cidx in c_idx:
        if sum(cidx[:, 0] == id510) > 1:
            eid = next(i for s, i in cidx if s == id510)
            subset510[eid] = False
    r510a = r510.col('azimuth').compress(subset510)
    r510z = r510.col('zenith').compress(subset510)
    filter510 = r510z > min_zenith


    for order in itertools.permutations(range(4), 4):
        r507 = data.get_node('/hisparc/cluster_amsterdam/station_507/',
                             REC_PATH % order)
        subset507 = [True] * r507.nrows
        id507 = next(i for i, s in enumerate(data.root.coincidences.s_index[:])
                     if s.endswith('_507'))
        for cidx in c_idx:
            if sum(cidx[:, 0] == id507) > 1:
                eid = next(i for s, i in cidx if s == id507)
                subset507[eid] = False

        r507a = r507.col('azimuth').compress(subset507)
        r507z = r507.col('zenith').compress(subset507)
        filter507 = r507z > min_zenith

        # Ensure neither has low zenith angle to avoid high uncertaintly
        # on azimuth.
        filter = filter510 & filter507

        counts, xbins, ybins = histogram2d(r507a.compress(filter),
                                           r510a.compress(filter),
                                           bins=linspace(-pi, pi, 40))
        plot = Plot()
        plot.histogram2d(counts, xbins, ybins, bitmap=True, type='color')
        plot.set_ylabel(r'Azimuth 510 [\si{\radian}]')
        plot.set_xlabel(r'Azimuth 507 [\si{\radian}]')
        plot.save_as_pdf(REC_PATH % order)

        counts, xbins, ybins = histogram2d(r507z, r510z,
                                           bins=linspace(0, pi / 2., 40))
        plot = Plot()
        plot.histogram2d(counts, xbins, ybins, bitmap=True, type='color')
        plot.set_ylabel(r'Zenith 510 [\si{\radian}]')
        plot.set_xlabel(r'Zenith 507 [\si{\radian}]')
        plot.save_as_pdf('zenith_' + REC_PATH % order)


if __name__ == '__main__':
    with tables.open_file(COINDATA_PATH, 'w') as data:
        download_data(data)
    with tables.open_file(COINDATA_PATH, 'a') as data:
        reconstruct_events(data)
    with tables.open_file(COINDATA_PATH, 'r') as data:
        plot_comparisons(data)
