import tables
from numpy import histogram, isnan, invert, array

from artist import Plot, PolarPlot

from sapphire import FlatFrontSimulation, ReconstructESDEvents, HiSPARCStations
from sapphire.utils import angle_between

DATAPATH = '/tmp/test_simulation_reconstruction.h5'
STATION = 14001
STATION_PATH = '/cluster_simulations/station_%d' % STATION


def simulate():
    """Perform flat shower front simulation on a station"""

    cluster = HiSPARCStations([STATION])
    with tables.open_file(DATAPATH, 'w') as data:
        sim = FlatFrontSimulation(cluster, data, '/', 100000)
        sim.run()


def reconstruct():
    """Reconstruct simulated events"""

    with tables.open_file(DATAPATH, 'a') as data:
        station = data.root.coincidences._v_attrs.cluster.get_station(STATION)
        rec = ReconstructESDEvents(data, STATION_PATH, station, overwrite=True)
        rec.prepare_output()
        rec.offsets = [d.offset for d in station.detectors]
        rec.reconstruct_directions(detector_ids=range(4))
        rec.store_reconstructions()


def analyse():
    """Plot results from reconstructions compared to the simulated input"""

    with tables.open_file(DATAPATH, 'r') as data:
        coincidences = data.get_node('/coincidences/coincidences')
        reconstructions = data.get_node(STATION_PATH)
        assert coincidences.nrows == reconstructions.nrows
        zenith_in = coincidences.col('zenith')
        azimuth_in = coincidences.col('azimuth')
        zenith_re = reconstructions.col('zenith')
        azimuth_re = reconstructions.col('azimuth')

    d_angle = angle_between(zenith_in, azimuth_in, zenith_re, azimuth_re)
    print sum(isnan(d_angle))

    plot = Plot()
    counts, bins = histogram(d_angle[invert(isnan(d_angle))], bins=50)
    plot.histogram(counts, bins)
    plot.set_ylimits(min=0)
    plot.set_xlabel(r'Angle between \si{\radian}')
    plot.set_ylabel('Counts')
    plot.save_as_pdf('angle_between')

    plot = Plot()
    counts, bins = histogram(zenith_in, bins=50)
    plot.histogram(counts, bins, linestyle='red')
    counts, bins = histogram(zenith_re, bins=bins)
    plot.histogram(counts, bins)
    plot.set_ylimits(min=0)
    plot.set_xlimits(min=0)
    plot.set_xlabel(r'Zenith \si{\radian}')
    plot.set_ylabel('Counts')
    plot.save_as_pdf('zenith')

    plot = Plot()
    counts, bins = histogram(azimuth_in, bins=50)
    plot.histogram(counts, bins, linestyle='red')
    counts, bins = histogram(azimuth_re, bins=bins)
    plot.histogram(counts, bins)
    plot.set_ylimits(min=0)
    plot.set_xlabel(r'Azimuth \si{\radian}')
    plot.set_ylabel('Counts')
    plot.save_as_pdf('azimuth')

    unique_coordinates = list({(z, a) for z, a in zip(zenith_re, azimuth_re)})
    zenith_uni, azimuth_uni = zip(*unique_coordinates)
    plot = PolarPlot(use_radians=True)
    plot.scatter(array(azimuth_uni), array(zenith_uni),
                 markstyle='mark size=.75pt')
    plot.set_xlabel(r'Azimuth \si{\radian}')
    plot.set_ylabel(r'Zenith \si{\radian}')
    plot.save_as_pdf('polar')


if __name__ == "__main__":
    simulate()
    reconstruct()
    analyse()
