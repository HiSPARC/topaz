""" Perform ground particle simulation on a station to guage reconstruction accuracy

Examine effects for core distance and particle density

Using simulations with approximate median size for their zenith/energy/particle:

477821264_628079401 - Zenith: 0, Energy: 10 ** 17, Particle: proton.
1115962_287886195 - Zenith: 0, Energy: 10 ** 14.5, Particle: proton.

"""
import tables

from numpy import degrees, histogram2d, isnan, sqrt

from artist import Plot

from sapphire import GroundParticlesSimulation, HiSPARCStations, ReconstructESDEvents

CORSIKA_DATA = '/Users/arne/Datastore/CORSIKA/477821264_628079401/corsika.h5'
RESULT_DATA = '/Users/arne/Datastore/corsika_accuracy/sim.h5'
CORSIKA_DATA_SMALL = '/Users/arne/Datastore/CORSIKA/1115962_287886195/corsika.h5'
RESULT_DATA_SMALL = '/Users/arne/Datastore/corsika_accuracy/sim_small.h5'


class ModGroundParticlesSimulation(GroundParticlesSimulation):

    """Require three detection points in a station"""

    def simulate_trigger(self, detector_observables):
        detectors_low = sum(True for observables in detector_observables if observables['n'] > 0.3)
        if detectors_low >= 3:
            return True
        else:
            return False


def do_simulation():
    with tables.open_file(RESULT_DATA, 'w') as data:
        cluster = HiSPARCStations([501], force_stale=True)
        sim = ModGroundParticlesSimulation(CORSIKA_DATA, 400, cluster, data, N=3000, progress=True)
        sim.run()


def do_simulation_small():
    with tables.open_file(RESULT_DATA_SMALL, 'w') as data:
        cluster = HiSPARCStations([501], force_stale=True)
        sim = ModGroundParticlesSimulation(CORSIKA_DATA_SMALL, 100, cluster, data, N=4000, progress=True)
        sim.run()


def do_reconstructions():
    with tables.open_file(RESULT_DATA, 'a') as data:
        s_group = data.root.coincidences.s_index[0]
        station = data.root.coincidences._v_attrs.cluster.stations[0]
        rec = ReconstructESDEvents(data, s_group, station, overwrite=True)
        rec.reconstruct_and_store()


def do_reconstructions_small():
    with tables.open_file(RESULT_DATA_SMALL, 'a') as data:
        s_group = data.root.coincidences.s_index[0]
        station = data.root.coincidences._v_attrs.cluster.stations[0]
        rec = ReconstructESDEvents(data, s_group, station, overwrite=True)
        rec.reconstruct_and_store()


def plot_zenith_density():
    with tables.open_file(RESULT_DATA, 'r') as data:
        e = data.root.cluster_simulations.station_501.events.read()
        density = (e['n1'] + e['n2'] + e['n3'] + e['n4']) / 2.0
        zenith = data.root.cluster_simulations.station_501.reconstructions.col('zenith')
        plot = Plot('semilogx')
        plot.scatter(density, degrees(zenith), markstyle='thin, mark size=.75pt')
        plot.set_xlabel(r'Particle density [\si{\per\meter\squared}]')
        plot.set_ylabel(r'Reconstructed zenith [\si{\degree}]')
        plot.set_xlimits(1, 1e4)
        plot.set_ylimits(-5, 95)
        plot.save_as_pdf('plots/zenith_density_e17_z0')


def plot_zenith_density_small():
    with tables.open_file(RESULT_DATA_SMALL, 'r') as data:
        e = data.root.cluster_simulations.station_501.events.read()
        density = (e['n1'] + e['n2'] + e['n3'] + e['n4']) / 2.0
        zenith = data.root.cluster_simulations.station_501.reconstructions.col('zenith')
        plot = Plot('semilogx')
        plot.scatter(density, degrees(zenith), markstyle='thin, mark size=.75pt')
        plot.set_xlabel(r'Particle density [\si{\per\meter\squared}]')
        plot.set_ylabel(r'Reconstructed zenith [\si{\degree}]')
        plot.set_xlimits(1, 1e4)
        plot.set_ylimits(-5, 95)
        plot.save_as_pdf('plots/zenith_density_e14_5_z0')


def plot_zenith_core_distance():
    with tables.open_file(RESULT_DATA, 'r') as data:
        sim = data.root.coincidences.coincidences.read_where('N == 1')
        core_distance = sqrt(sim['x'] ** 2 + sim['y'] ** 2)
        zenith = data.root.cluster_simulations.station_501.reconstructions.col('zenith')
        plot = Plot('semilogx')
        plot.scatter(core_distance, degrees(zenith), markstyle='thin, mark size=.75pt')
        plot.set_xlabel(r'Core distance [\si{\meter}]')
        plot.set_ylabel(r'Reconstructed zenith [\si{\degree}]')
        plot.set_xlimits(1, 1e3)
        plot.set_ylimits(-5, 95)
        plot.save_as_pdf('plots/zenith_distance_e17_z0')


def plot_zenith_core_distance_small():
    with tables.open_file(RESULT_DATA_SMALL, 'r') as data:
        sim = data.root.coincidences.coincidences.read_where('N == 1')
        core_distance = sqrt(sim['x'] ** 2 + sim['y'] ** 2)
        zenith = data.root.cluster_simulations.station_501.reconstructions.col('zenith')
        plot = Plot('semilogx')
        plot.scatter(core_distance, degrees(zenith), markstyle='thin, mark size=.75pt')
        plot.set_xlabel(r'Core distance [\si{\meter}]')
        plot.set_ylabel(r'Reconstructed zenith [\si{\degree}]')
        plot.set_xlimits(1, 1e3)
        plot.set_ylimits(-5, 95)
        plot.save_as_pdf('plots/zenith_distance_e14_5_z0')


def plot_zenith_core_distance_small_2d():
    with tables.open_file(RESULT_DATA_SMALL, 'r') as data:
        sim = data.root.coincidences.coincidences.read_where('N == 1')
        core_distance = sqrt(sim['x'] ** 2 + sim['y'] ** 2)
        zenith = data.root.cluster_simulations.station_501.reconstructions.col('zenith')
        plot = Plot('semilogx')
        core_distance = core_distance[~isnan(zenith)]
        zenith = zenith[~isnan(zenith)]
        counts, x, y = histogram2d(core_distance, degrees(zenith), bins=50)
        plot.histogram2d(counts, x, y, type='color', bitmap=True)
        plot.set_xlabel(r'Core distance [\si{\meter}]')
        plot.set_ylabel(r'Reconstructed zenith [\si{\degree}]')
        plot.save_as_pdf('zenith_distance_e14_5_z0_2d')


if __name__ == "__main__":
    # do_simulation()
    # do_reconstructions()
    plot_zenith_density()
    plot_zenith_core_distance()
    # do_simulation_small()
    # do_reconstructions_small()
    plot_zenith_density_small()
    plot_zenith_core_distance_small()
    # plot_zenith_core_distance_small_2d()
