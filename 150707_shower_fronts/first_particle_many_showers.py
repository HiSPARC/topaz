"""Arrival times of first particle in detector for certain core distances."""


import tables

from numpy import arange, histogram, isnan, load, nan, save, sqrt

from artist import Plot

OVERVIEW = '/data/hisparc/corsika/corsika_overview.h5'
LOCAL_STORE = '/data/hisparc/corsika/data/{seed}/corsika.h5'


def select_showers(e):
    with tables.open_file(OVERVIEW, 'r') as overview:
        sims = overview.get_node('/simulations')
        selection = sims.read_where('(log10(energy) == e) & ' '(zenith == 0.) & ' '(particle_id == 14)')
        for shower in selection:
            yield '%d_%d' % (shower['seed1'], shower['seed2'])


def get_first_particle(seed, x):
    path = LOCAL_STORE.format(seed=seed)
    detector_boundary = sqrt(0.5) / 2.0
    query = '(x >= %f) & (x <= %f) & (y >= %f) & (y <= %f)' ' & (particle_id >= 2) & (particle_id <= 6)' % (
        x - detector_boundary,
        x + detector_boundary,
        -detector_boundary,
        detector_boundary,
    )
    try:
        with tables.open_file(path, 'r') as data:
            header = data.get_node_attr('/', 'event_header')
            time_first_interaction = (header.first_interaction_altitude - header.observation_heights[0]) / 0.2998
            t = data.root.groundparticles.read_where(query, field='t')
            if not len(t):
                return nan
            else:
                return t.min() - time_first_interaction
    except:
        return nan


def get_times():
    for e in arange(14, 18, 1):
        for core_distance in [1, 5, 10, 50, 100, 500, 1000]:
            tmp_times = [get_first_particle(seed, core_distance) for seed in select_showers(e)]
            times = [t for t in tmp_times if not isnan(t)]
            path = '/data/hisparc/adelaat/first_particle/first_{e}_{r}'.format(e=e, r=core_distance)
            save(path, times)


def plot_distribution():
    for e in arange(14, 18, 1):
        for core_distance in [1, 5, 10, 50, 100, 500, 1000]:
            path = '/Users/arne/Datastore/first_particle/first_{e}_{r}.npy'.format(e=e, r=core_distance)
            times = load(path)
            counts, bins = histogram(times, bins=20)
            plot = Plot()
            plot.histogram(counts, bins)
            plot.set_xlabel('arrival time [ns]')
            plot.set_ylabel('Counts')
            plot.set_ylimits(min=0)
            plot.set_xlimits(bins[0], bins[-1])
            plot.set_label('E=$10^{{{e}}}$eV, r={r}m'.format(e=e, r=core_distance))
            plot.save_as_pdf('plots/first_particle_{e}_{r}_new'.format(e=e, r=core_distance))


if __name__ == "__main__":
    # get_times()
    plot_distribution()
