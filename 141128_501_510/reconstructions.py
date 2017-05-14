import tables

from numpy import arange, array, degrees, histogram, pi, sqrt

from artist import Plot, PolarPlot

from sapphire import ReconstructESDEvents
from sapphire.clusters import BaseCluster
from sapphire.utils import angle_between

COLORS = ['black', 'teal', 'orange', 'purple', 'cyan', 'green', 'blue', 'red',
          'gray']


def reconstruct_simulations(data):
    cluster = cluster_501_510()
    for station in cluster.stations:
        station_group = '/hisparc/cluster_amsterdam/station_%d' % station.number
        rec_events = ReconstructESDEvents(data, station_group, station,
                                          overwrite=True, progress=True)
        rec_events.prepare_output()
        rec_events.offsets = offset(station.number)
        rec_events.store_offsets()
        try:
            rec_events.reconstruct_directions()
            rec_events.store_reconstructions()
        except:
            pass


def offset(station):
    if station == 501:
        return [-1.064884, 0., 6.217017, 4.851398]
    elif station == 510:
        return [9.416971, 0., 9.298256, 8.447724]


def cluster_501_510():
    station_size = 10.
    a = station_size / 2
    b = a * sqrt(3)
    detectors = [((-a, 0.), 'UD'), ((a, 0.), 'UD'),
                 ((a * 2, b), 'LR'), ((0., b), 'LR')]
    cluster = BaseCluster()
    for n in [501, 510]:
        cluster._add_station((0, 0, 0), 0, detectors, number=n)
    return cluster


def plot_reconstruction_accuracy(data, d):

    station_path = '/cluster_simulations/station_%d'
    cluster = cluster_501_510()
    coincidences = data.root.coincidences.coincidences
    recs501 = data.root.hisparc.cluster_amsterdam.station_501.reconstructions
    recs510 = data.root.hisparc.cluster_amsterdam.station_510.reconstructions
    graph = Plot()
    ids = set(recs501.col('id')).intersection(recs510.col('id'))
    filtered_501 = [(row['zenith'], row['azimuth']) for row in recs501 if row['id'] in ids]
    filtered_510 = [(row['zenith'], row['azimuth']) for row in recs510 if row['id'] in ids]

    zen501, azi501 = zip(*filtered_501)
    zen510, azi510 = zip(*filtered_510)
    zen501 = array(zen501)
    azi501 = array(azi501)
    zen510 = array(zen510)
    azi510 = array(azi510)
    da = angle_between(zen501, azi501, zen510, azi510)

    n, bins = histogram(da, bins=arange(0, pi, .1))
    graph.histogram(n, bins)

    failed = coincidences.nrows - len(ids)
    graph.set_ylimits(min=0)
    graph.set_xlimits(min=0, max=pi)
    graph.set_ylabel('Count')
    graph.set_xlabel('Angle between 501 and 510 [rad]')
    graph.set_title('Coincidences between 501 and 510')
    graph.set_label('Failed to reconstruct %d events' % failed)
    graph.save_as_pdf('coincidences_%s' % d)

    graph_recs = PolarPlot()
    azimuth = degrees(recs501.col('azimuth'))
    zenith = degrees(recs501.col('zenith'))
    graph_recs.scatter(azimuth[:5000], zenith[:5000], mark='*',
                       markstyle='mark size=.2pt')
    graph_recs.set_ylimits(min=0, max=90)
    graph_recs.set_ylabel('Zenith [degrees]')
    graph_recs.set_xlabel('Azimuth [degrees]')
    graph_recs.set_title('Reconstructions by 501')
    graph_recs.save_as_pdf('reconstructions_%s' % d)

if __name__ == '__main__':
    for d in ['c_501_510_141001_141011', 'c_501_510_141101_141111']:
        # with tables.open_file('/Users/arne/Datastore/501_510/%s.h5' % d, 'a') as data:
        #     reconstruct_simulations(data)
        with tables.open_file('/Users/arne/Datastore/501_510/%s.h5' % d, 'r') as data:
            plot_reconstruction_accuracy(data, d)
