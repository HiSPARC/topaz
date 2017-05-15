""" Perform ground particle simulation on a station at various core distances

Examine the spread of the arrival time of the first particle for a station at
various core distances. At large core distances the particle density becomes
low and the probabiliy of detection/trigger quickly decreases.

First this is examined for a specific shower, and compared to the particle
arrival time profiles of the shower (without sampling).

Next figure out what the spread in distributions is for showers of same energy
and particle. Next also constrainother parameters first intreraction altitude,
and/or shower size.


This simultion currently ignores gammas


"""
import sys

import tables

from numpy import around, array, degrees, log10, logspace, percentile, sqrt

from artist import MultiPlot

from sapphire import CorsikaQuery
from sapphire.analysis.event_utils import station_arrival_time
from sapphire.clusters import SingleDiamondStation
from sapphire.corsika.particles import name
from sapphire.simulations.groundparticles import FixedCoreDistanceSimulation

# local seeds
SEEDS_14 = ['651000510_222963176', '155366293_265066277', '758294490_567681579']
SEEDS_15 = ['791363922_262129855', '291305112_897286854', '683790878_143722028']
SEEDS_16 = ['149042664_130233131', '108507276_832136747', '458273069_189490816']

SEEDS = SEEDS_14 + SEEDS_15 + SEEDS_16


class ModSim(FixedCoreDistanceSimulation):

    """Use fixed core distance, perfect particle counting, and no offsets"""

    @classmethod
    def simulate_detector_offsets(cls, n_detectors):

        return [0.] * n_detectors

    @classmethod
    def simulate_detector_offset(cls):

        return 0.

    @classmethod
    def simulate_station_offset(cls):

        return 0.

    @classmethod
    def simulate_detector_mips(cls, n, theta):

        return n


def do_simulations(data, seeds):
    cluster = SingleDiamondStation()
    distances = around(logspace(1.3, 2.7, 10))
    for distance in distances:
        sim = ModSim(corsikafile_path=CORSIKA_DATA % seeds,
                     max_core_distance=distance, cluster=cluster,
                     data=data, N=5000, progress=False,
                     output_path=make_sim_path(seeds, distance))
        sim.run()


def get_info(seeds):
    cq = CorsikaQuery(OVERVIEW)
    info = cq.get_info(seeds)
    cq.finish()
    return info


def get_info_string(seeds):
    info = get_info(seeds)
    return ('%s_E_%.1f_Z_%.1f_I_%d_%s' %
            (name(info['particle_id']), log10(info['energy']),
             degrees(info['zenith']), info['first_interaction_altitude'] / 1e3,
             seeds))


def make_sim_path(seeds, distance):
    info = get_info(seeds)
    return ('/%s/e%.1f/z%.1f/i%d/s%s/r%d' %
            (name(info['particle_id']), log10(info['energy']),
             degrees(info['zenith']), info['first_interaction_altitude'] / 1e3,
             seeds, distance)).replace('.', '_')


def plot_arrival_time_distribution_v_distance(data, seeds):

    results = []
    cor_t = None

    for group in data.walk_groups('/'):
        if (seeds not in group._v_pathname or
                group._v_name != 'coincidences'):
            continue
        coincidences = group.coincidences
        events = data.get_node(group.s_index[0]).events

        r = next(int(y[1:]) for y in group._v_pathname.split('/')
                 if y.startswith('r'))
        seeds = next(y[1:] for y in group._v_pathname.split('/')
                     if y.startswith('s'))

        if cor_t is None:
            with tables.open_file(CORSIKA_DATA % seeds) as data:
                gp = data.root.groundparticles
                query = '(x < 10) & (x > -10) & (r < 10)'
                cor_t = gp.read_where(query, field='t').min()

#         i = get_info(seeds)['first_interaction_altitude']
#         cor_t = i / 0.299792458

        # Round ts to seconds because it is the ts for first event, not the shower
        t = [station_arrival_time(event, int(cets['ext_timestamp'] / int(1e9)) * int(1e9),
                                  detector_ids=[0, 1, 2, 3]) - cor_t
             for event, cets in zip(events[:], coincidences.read_where('N == 1'))]

        if not len(t) or len(t) < 10:
            continue

        quantiles = [25, 50, 75]
        qt = percentile(t, q=quantiles)

        results.append([r] + list(qt) + [100 * events.nrows / float(coincidences.nrows)])

    if not len(results):
        return

    results = sorted(results)

    (core_distances, arrival_times_low, arrival_times, arrival_times_high,
     efficiency) = zip(*results)

    causal = causal_front(i, core_distances)

    plot = MultiPlot(2, 1)

    splot = plot.get_subplot_at(0, 0)
    plot_shower_profile(seeds, splot, core_distances, cor_t)
    splot.plot(core_distances, causal, mark=None, linestyle='purple, dashed')
    splot.plot(core_distances, arrival_times, mark='*')
    splot.shade_region(core_distances, arrival_times_low, arrival_times_high,
                       color='blue, semitransparent')
    splot.set_ylabel(r'Arrival time [\si{\ns}]')

    splot = plot.get_subplot_at(1, 0)
    splot.plot(core_distances, efficiency)
    splot.set_ylabel(r'Detection efficiency [\si{\percent}]')
    splot.set_axis_options(r'height=0.25\textwidth')

    plot.set_ylimits(0, 0, min=-10, max=210)
    plot.set_ylimits(1, 0, min=-5, max=105)
    plot.set_xlimits_for_all(None, 0, 550)
    plot.set_xlabel(r'Core distance [\si{\meter}]')
    plot.show_xticklabels(1, 0)
    plot.show_yticklabels_for_all()
    plot.save_as_document('/data/hisparc/adelaat/corsika_accuracy/plots/%s.tex' %
                          get_info_string(seeds))


def causal_front(first_interaction_altitude, x):
    r = first_interaction_altitude
    x = array(x)
    return r - sqrt(r ** 2 - x ** 2)


def plot_shower_profile(seeds, splot, core_distances, cor_t):

    query = ('((particle_id == 3) | (particle_id == 4) |'
             ' (particle_id == 5) | (particle_id == 6)) & '
             '(abs(r - core_distance) < 10)')

    with tables.open_file(CORSIKA_DATA % seeds) as data:
        gp = data.root.groundparticles

        t = []

        for core_distance in core_distances:
            lepton_t = (gp.read_where(query, field='t') - cor_t)
            quantiles = [25, 50, 75]
            t.append(percentile(lepton_t, q=quantiles))

    t_low, t, t_high = zip(*t)
    splot.plot(core_distances, t)
    splot.shade_region(core_distances, t_low, t_high)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        # Stoomboot
        CORSIKA_DATA = '/data/hisparc/corsika/data/%s/corsika.h5'
        RESULT_SEED = '/data/hisparc/adelaat/corsika_accuracy/%s.h5'
        OVERVIEW = '/data/hisparc/corsika/corsika_overview.h5'
        seeds = sys.argv[1]
        filters = tables.Filters(complevel=1)
#         with tables.open_file(RESULT_SEED % seeds, 'a', filters=filters) as data:
#             do_simulations(data, seeds)
        with tables.open_file(RESULT_SEED % seeds, 'r') as data:
            plot_arrival_time_distribution_v_distance(data, seeds)
    elif len(sys.argv) > 2:
        print 'Wrong number of arguments'
    else:
        # Local
        CORSIKA_DATA = '/Users/arne/Datastore/CORSIKA/%s/corsika.h5'
        RESULT_DATA = '/Users/arne/Datastore/corsika_accuracy/fixed_core_sim.h5'
        OVERVIEW = '/Users/arne/Datastore/CORSIKA/corsika_overview.h5'
        filters = tables.Filters(complevel=1)
        with tables.open_file(RESULT_DATA, 'a', filters=filters) as data:
            for seeds in SEEDS:
                do_simulations(data, seeds)
        with tables.open_file(RESULT_DATA, 'r') as data:
            for seeds in SEEDS:
                plot_arrival_time_distribution_v_distance(data, seeds)
