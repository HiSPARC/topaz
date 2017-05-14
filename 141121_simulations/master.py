"""
Run simulations, reconstruct the results and make some plots..

"""
import tables

from numpy import arange, array, histogram, linspace, pi

from artist import Plot, PolarPlot

from sapphire import GroundParticlesSimulation, HiSPARCStations, ReconstructESDCoincidences, ReconstructESDEvents
from sapphire.utils import angle_between

RESULT_PATH = 'result_400_gen_16394.h5'
CORSIKA_DATA = 'corsika.h5'
GRAYS = ['black', 'darkgray', 'gray', 'lightgray']
COLORS = ['black', 'teal', 'orange', 'purple', 'cyan', 'green', 'blue', 'red',
          'gray']


def run_simulation():
    with tables.open_file(RESULT_PATH, 'w') as data:
        cluster = HiSPARCStations([501, 502, 503, 504, 505, 506, 508, 509])
        sim = GroundParticlesSimulation(
            CORSIKA_DATA, max_core_distance=400, cluster=cluster,
            datafile=data, output_path='/', N=5000)
        sim.run()


def scatter_n():
    r = 420
    with tables.open_file(RESULT_PATH, 'r') as data:
        cluster = data.root.coincidences._v_attrs.cluster
        coincidences = data.root.coincidences.coincidences
        graph = Plot()
        for n in range(0, len(cluster.stations) + 1):
            c = coincidences.read_where('N == n')
            if len(c) == 0:
                continue
            graph.plot(c['x'], c['y'], mark='*', linestyle=None,
                       markstyle='mark size=.2pt,color=%s' % COLORS[n % len(COLORS)])
            graph1 = Plot()
            graph1.plot(c['x'], c['y'], mark='*', linestyle=None,
                        markstyle='mark size=.2pt')
            plot_cluster(graph1, cluster)
            graph1.set_axis_equal()
            graph1.set_ylimits(-r, r)
            graph1.set_xlimits(-r, r)
            graph1.set_ylabel('y [m]')
            graph1.set_xlabel('x [m]')
            graph1.set_title('Showers that caused triggers in %d stations' % n)
            graph1.save_as_pdf('N_%d' % n)

            graph_azi = PolarPlot(use_radians=True)
            plot_azimuth(graph_azi, c['azimuth'])
            graph_azi.set_label('N = %d' % n)
            graph_azi.save('azi_%d' % n)
            graph_azi.save_as_pdf('azi_%d' % n)

        plot_cluster(graph, cluster)
        graph.set_axis_equal()
        graph.set_ylimits(-r, r)
        graph.set_xlimits(-r, r)
        graph.set_ylabel('y [m]')
        graph.set_xlabel('x [m]')
        graph.set_title('Color indicates the number triggered stations by '
                        'a shower.')
        graph.save_as_pdf('N')


def plot_azimuth(graph, azimuth):
    n, bins = histogram(azimuth, bins=linspace(-pi, pi, 21))
    graph.histogram(n, bins)
    graph.set_title('Azimuth distribution')
    graph.set_xlimits(-pi, pi)
    graph.set_ylimits(min=0)
    graph.set_xlabel('Azimuth [rad]')
    graph.set_ylabel('Counts')


def plot_cluster(graph, cluster):
    for station in cluster.stations:
        for detector in station.detectors:
            detector_x, detector_y = detector.get_xy_coordinates()
            graph.plot([detector_x], [detector_y], mark='*', linestyle=None,
                       markstyle='mark size=.4pt,color=red')


def plot_reconstruction_accuracy():

    combinations = ['~d1 | ~d2 | ~d3 | ~d4', 'd1 & d2 & d3 & d4']
    station_path = '/cluster_simulations/station_%d'
    with tables.open_file(RESULT_PATH, 'r') as data:
        cluster = data.root.coincidences._v_attrs.cluster
        coincidences = data.root.coincidences.coincidences
        c_recs = data.root.coincidences.reconstructions
        graph = Plot()
        da = angle_between(c_recs.col('zenith'),
                           c_recs.col('azimuth'),
                           c_recs.col('reference_zenith'),
                           c_recs.col('reference_azimuth'))
        ids = c_recs.col('id')
        N = coincidences.read_coordinates(ids, field='N')
        for k, filter in enumerate([N == 3, N > 3]):
            n, bins = histogram(da.compress(filter), bins=arange(0, pi, .1))
            graph.histogram(n, bins, linestyle=GRAYS[k % len(GRAYS)])

        failed = len(coincidences.get_where_list('N >= 3')) - c_recs.nrows
        graph.set_ylimits(min=0)
        graph.set_xlimits(min=0, max=pi)
        graph.set_ylabel('Count')
        graph.set_xlabel('Angle between input and reconstruction [rad]')
        graph.set_title('Coincidences')
        graph.set_label('Failed to reconstruct %d events' % failed)
        graph.save_as_pdf('coincidences_alt')

        for station in cluster.stations:
            station_group = data.get_node(station_path % station.number)
            recs = station_group.reconstructions
            rows = coincidences.get_where_list('s%d == True' % station.number)
            reference_azimuth = coincidences.read_coordinates(rows, field='azimuth')
            reference_zenith = coincidences.read_coordinates(rows, field='zenith')
            graph = Plot()
            for k, combo in enumerate(combinations):
                selected_reconstructions = recs.read_where(combo)
                filtered_azimuth = array([reference_azimuth[i]
                                          for i in selected_reconstructions['id']])
                filtered_zenith = array([reference_zenith[i]
                                         for i in selected_reconstructions['id']])
                azimuth = selected_reconstructions['azimuth']
                zenith = selected_reconstructions['zenith']

                da = angle_between(zenith, azimuth,
                                   filtered_zenith, filtered_azimuth)
                n, bins = histogram(da, bins=arange(0, pi, .1))
                graph.histogram(n, bins, linestyle=GRAYS[k % len(GRAYS)])
            failed = station_group.events.nrows - recs.nrows

            graph.set_ylimits(min=0)
            graph.set_xlimits(min=0, max=pi)
            graph.set_ylabel('Count')
            graph.set_xlabel('Angle between input and reconstruction [rad]')
            graph.set_title('Station: %d' % station.number)
            graph.set_label('Failed to reconstruct %d events' % failed)
            graph.save_as_pdf('s_%d' % station.number)


def reconstruct_simulations():
    with tables.open_file(RESULT_PATH, 'a') as data:
        cluster = data.root.coincidences._v_attrs.cluster

        for station in cluster.stations:
            station_group = '/cluster_simulations/station_%d' % station.number
            rec_events = ReconstructESDEvents(data, station_group, station,
                                              overwrite=True, progress=True)
            rec_events.prepare_output()
            rec_events.offsets = station.detector_offsets
            rec_events.store_offsets()
            try:
                rec_events.reconstruct_directions()
                rec_events.store_reconstructions()
            except:
                pass

        rec_coins = ReconstructESDCoincidences(data, '/coincidences',
                                               overwrite=True, progress=True)
        rec_coins.prepare_output()
        rec_coins.offsets = {station.number: [o + station.gps_offset
                                              for o in station.detector_offsets]
                             for station in cluster.stations}
        try:
            rec_coins.reconstruct_directions()
            rec_coins.store_reconstructions()
        except:
            pass


if __name__ == '__main__':
    # run_simulation()
    # reconstruct_simulations()
    scatter_n()
    # plot_reconstruction_accuracy()
