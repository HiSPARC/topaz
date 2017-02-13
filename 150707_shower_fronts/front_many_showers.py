"""Arrival times of first particle in detector for certain core distances."""

import tables
from numpy import arange, save, load, sqrt, nan, isnan, histogram, median, std, mean

from artist import Plot

OVERVIEW = '/data/hisparc/corsika/corsika_overview.h5'
LOCAL_STORE = '/data/hisparc/corsika/data/{seed}/corsika.h5'
CORE_DISTANCES = [3, 5, 7, 10, 20, 30, 50, 70, 100, 200, 300, 400, 500]
ENERGIES = arange(15, 18, 1)


def select_showers(e):
    with tables.open_file(OVERVIEW, 'r') as overview:
        sims = overview.get_node('/simulations')
        selection = sims.read_where('(log10(energy) == e) & '
                                    '(zenith == 0.) & '
                                    '(particle_id == 14)')
        for shower in selection:
            yield '%d_%d' % (shower['seed1'], shower['seed2'])


def get_first_median_particles(seed, x):
    path = LOCAL_STORE.format(seed=seed)
    detector_boundary = 2
    query = ('(x >= %f) & (x <= %f) & (y >= %f) & (y <= %f)'
             ' & (particle_id >= 2) & (particle_id <= 6)' %
             (x - detector_boundary, x + detector_boundary,
              -detector_boundary, detector_boundary))
    try:
        with tables.open_file(path, 'r') as data:
            header = data.get_node_attr('/', 'event_header')
            time_first_interaction = (header.first_interaction_altitude -
                                      header.observation_heights[0]) / .2998
            t = data.root.groundparticles.read_where(query, field='t')
            if not len(t):
                return nan, nan
            else:
                return t.min() - time_first_interaction, median(t) - time_first_interaction
    except:
        return nan, nan


def get_times():
    for e in ENERGIES:
        for core_distance in CORE_DISTANCES:
            times = [get_first_median_particles(seed, core_distance)
                     for seed in select_showers(e)]
            first_times, median_times = zip(*times)
            first_times = [t for t in first_times if not isnan(t)]
            median_times = [t for t in median_times if not isnan(t)]
            first_path = ('/data/hisparc/adelaat/first_particle/first_{e}_{r}'
                          .format(e=e, r=core_distance))
            save(first_path, first_times)
            median_path = ('/data/hisparc/adelaat/first_particle/median_{e}_{r}'
                           .format(e=e, r=core_distance))
            save(median_path, median_times)


def plot_distribution():
    distances = CORE_DISTANCES
    for e in ENERGIES:
        first_t = []
        first_t_std = []
        median_t = []
        median_t_std = []
        for core_distance in distances:
            first_path = ('/Users/arne/Datastore/first_particle/first_{e}_{r}.npy'
                          .format(e=e, r=core_distance))
            median_path = ('/Users/arne/Datastore/first_particle/median_{e}_{r}.npy'
                           .format(e=e, r=core_distance))
            first_times = load(first_path)
            first_t.append(mean(first_times))
            first_t_std.append(std(first_times))
            median_times = load(median_path)
            median_t.append(mean(median_times))
            median_t_std.append(std(median_times))
        plot = Plot('semilogx')
        plot.plot(distances, first_t, yerr=first_t_std, markstyle='mark size=1pt', linestyle=None)
        plot.plot(distances, median_t, yerr=median_t_std, markstyle='mark size=1pt,gray', linestyle=None)
        plot.set_xlabel('Core distance [m]')
        plot.set_ylabel('Time after first [ns]')
        plot.set_ylimits(min=-10)
        plot.set_xlimits(0, 1e3)
        plot.set_label('E=$10^{{{e}}}$eV'.format(e=e), location='upper left')
        plot.save_as_pdf('plots/first_particle_{e}'.format(e=e))


if __name__ == "__main__":
    # get_times()
    plot_distribution()
