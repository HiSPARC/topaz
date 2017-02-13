"""
This script was used to test the groundparticle simulations.
We found inconsistencies in the simulations so an easy way to
run simulations and check the results was needed, so I wrote
this little script.

"""
import tables

from artist import Plot

from sapphire.simulations.groundparticles import GroundParticlesSimulationWithoutErrors
from sapphire.clusters import BaseCluster, ScienceParkCluster

RESULT_PATH = '/Users/arne/Datastore/temp/test_groundparticle_sim_square.h5'
CORSIKA_DATA = '/Users/arne/Datastore/CORSIKA/821280921_182096636/corsika.h5'


def run_simulation():
    with tables.open_file(RESULT_PATH, 'w') as data:
        cluster = ScienceParkCluster()
        sim = GroundParticlesSimulationWithoutErrors(
            CORSIKA_DATA, max_core_distance=500, cluster=cluster,
            datafile=data, output_path='/', N=3000, seed=153957)
        sim.run()


def scatter_n():
    with tables.open_file(RESULT_PATH, 'r') as data:
        cluster = data.root.coincidences._v_attrs.cluster
        coincidences = data.root.coincidences.coincidences
        for n in range(0, len(cluster.stations) + 1):
            graph = Plot()
            c = coincidences.read_where('N == n')
            print 'N = %d: %d' % (n, len(c))
            graph.plot(c['x'], c['y'], mark='*', linestyle=None,
                       markstyle='mark size=.3pt')
            plot_cluster(graph, cluster)
            r = 520
            graph.set_ylimits(-r, r)
            graph.set_xlimits(-r, r)
            graph.set_ylabel('y (m)')
            graph.set_xlabel('x (m)')
            graph.save_as_pdf('N_%d' % n)


def plot_cluster(graph, cluster):
    for station in cluster.stations:
        for detector in station.detectors:
            detector_x, detector_y = detector.get_xy_coordinates()
            graph.plot([detector_x], [detector_y], mark='*', linestyle=None,
                       markstyle='mark size=.4pt,color=red')


def test_cluster():
    cluster = BaseCluster()
    detectors = [((-1, 0, 0), 'UD'), ((1, 0, 0), 'UD')]

    l = 20
    cluster._add_station((0, 0, 0), 0, detectors)
    cluster._add_station((l, l, 0), 0, detectors)
    cluster._add_station((l, -l, 0), 0, detectors)
    cluster._add_station((-l, l, 0), 0, detectors)
    cluster._add_station((-l, -l, 0), 0, detectors)
    return cluster


def rerun_shower():
    data = tables.open_file(RESULT_PATH + 'temp.h5', 'w')
    bla = tables.open_file(RESULT_PATH, 'r')

    cluster = bla.root.coincidences._v_attrs.cluster

    sim = GroundParticlesSimulationWithoutErrors(
        CORSIKA_DATA, 0, cluster, datafile=data, output_path='/',
        N=100, seed=153957)

    shower_parameters = bla.root.coincidences.coincidences[0]
    alpha = shower_parameters['azimuth'] - sim.corsikafile.get_node_attr('/', 'event_header').azimuth
    sim._prepare_cluster_for_shower(shower_parameters['x'], shower_parameters['y'], alpha)
    sim.simulate_events_for_shower(bla.root.coincidences.coincidences[0])


if __name__ == '__main__':

    run_simulation()
    scatter_n()
