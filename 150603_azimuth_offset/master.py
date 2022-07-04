"""
Run simulations with skewed azimuth distribution (without offsets)/
Using the results determine 'detector offsets'.
Reconstruct with and without detector offsets.

This to determine if we could be compensating with detector offsets for
real physics.

"""
import tables

from numpy import histogram, linspace, pi, random, sin

from artist import Plot

from sapphire import FlatFrontSimulation, HiSPARCStations, ReconstructESDEvents

RESULT_PATH = 'skewed_azimuth.h5'


class OffsetAzimuthFlatFrontSimulation(FlatFrontSimulation):

    """

    :param cluster: :class:`~sapphire.clusters.BaseCluster` instance.
    :param datafile: writeable PyTables file handle.
    :param output_path: path (as string) to the PyTables group (need not
                        exist) in which the result tables will be created.
    :param N: number of simulations to perform.

    """

    @staticmethod
    def generate_azimuth():
        """Generate a random azimuth

        Showers have a slanted azimuth distribution.

        Idea from: http://math.stackexchange.com/a/499415

        50% of the samples have a uniform distribution.
        The other 50% have a sin(phi)**2 distribution.

        """
        if random.choice([True, False], p=[.4, .6]):
            x = random.uniform(0, pi / 2)
            y = random.uniform(0, 1)
            if not sin(x) ** 2 > y:
                x += pi / 2
            value = 2 * x - pi
        else:
            value = random.uniform(-pi, pi)

        return value

    def simulate_detector_response(self, detector, shower_parameters):
        """Simulate detector response to a shower.

        Return the arrival time of shower front passing the center of
        the detector.

        """
        observables = super(OffsetAzimuthFlatFrontSimulation,
                            self).simulate_detector_response(detector, shower_parameters)
        observables.update({'n': 1.})

        return observables

    def simulate_detector_offset(self):
        return 0.


def run_simulation():
    with tables.open_file(RESULT_PATH, 'w') as data:
        cluster = HiSPARCStations([501])  # , 502, 503, 504, 505, 506, 508, 509])
        sim = OffsetAzimuthFlatFrontSimulation(
            cluster=cluster, datafile=data, output_path='/', N=60000)
        sim.run()


def reconstruct_simulations():
    with tables.open_file(RESULT_PATH, 'a') as data:
        cluster = data.root.coincidences._v_attrs.cluster

        for station in cluster.stations:
            station_group = '/cluster_simulations/station_%d' % station.number
            rec_events = ReconstructESDEvents(data, station_group, station,
                                              overwrite=True, progress=True,
                                              destination='reconstructions_offset')
            rec_events.reconstruct_and_store()
            print(rec_events.offsets)
            rec_events = ReconstructESDEvents(data, station_group, station,
                                              overwrite=True, progress=True,
                                              destination='reconstructions_no_offset')
            rec_events.prepare_output()
            rec_events.store_offsets()
            rec_events.reconstruct_directions()
            rec_events.store_reconstructions()
            print(rec_events.offsets)


def plot_azimuth(azimuth, name=''):

    # graph = PolarPlot(use_radians=True)
    graph = Plot()
    n, bins = histogram(azimuth, bins=linspace(-pi, pi, 21))
    graph.histogram(n, bins)
    graph.set_title('Azimuth distribution')
    graph.set_xlimits(-pi, pi)
    graph.set_ylimits(min=0)
    graph.set_xlabel('Azimuth [rad]')
    graph.set_ylabel('Counts')
    graph.save_as_pdf('azi_norm_%s' % name)


def plot_zenith(zenith, name=''):

    graph = Plot()
    n, bins = histogram(zenith, bins=linspace(0, pi / 2., 41))
    graph.histogram(n, bins)
    graph.set_title('Zenith distribution')
    graph.set_xlimits(0, pi / 2.)
    graph.set_ylimits(min=0)
    graph.set_xlabel('Zenith [rad]')
    graph.set_ylabel('Counts')
    graph.save_as_pdf('zen_%s' % name)


if __name__ == '__main__':

    # run_simulation()
    # reconstruct_simulations()

    with tables.open_file(RESULT_PATH, 'r') as data:
        recs = data.get_node('/cluster_simulations/station_501', 'reconstructions_offset')
        azi = recs.col('azimuth')
        zen = recs.col('zenith')
        plot_azimuth(azi, 'offset')
        plot_zenith(zen, 'offset')
        recs = data.get_node('/cluster_simulations/station_501', 'reconstructions_no_offset')
        azi = recs.col('azimuth')
        zen = recs.col('zenith')
        plot_azimuth(azi, 'no_offset')
        plot_zenith(zen, 'no_offset')

        sims = data.get_node('/coincidences', 'coincidences')
        azi = sims.col('azimuth')
        zen = sims.col('zenith')
        plot_azimuth(azi, 'input')
        plot_zenith(zen, 'input')
