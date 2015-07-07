from operator import itemgetter
import subprocess
import os

import tables
from numpy import arange, percentile, logspace, sqrt, log10, pi, abs

from artist import Plot


# proton = 14
# iron = 5626

OVERVIEW = '/Users/arne/Datastore/CORSIKA/corsika_overview_150624.h5'
LOCAL_STORE = '/Users/arne/Datastore/corsika_thickness/'

def select_showers():
    with tables.open_file(OVERVIEW, 'r') as overview:
        sims = overview.get_node('/simulations')
        for e in arange(13, 17.5, .5):
            selection = sims.read_where('(log10(energy) == e) & '
                                        '(zenith == 0.) & '
                                        '(particle_id == 14)')
            sorted_selection = sorted(selection, key=itemgetter('n_electron'))
            small_shower = sorted_selection[0]
            median_shower = sorted_selection[len(sorted_selection) / 2]
            large_shower = sorted_selection[-1]
            yield '%d_%d' % (small_shower['seed1'], small_shower['seed2'])
            yield '%d_%d' % (median_shower['seed1'], median_shower['seed2'])
            yield '%d_%d' % (large_shower['seed1'], large_shower['seed2'])


def copy_shower(seeds):
    cmd = ('rsync -qavz --exclude "DAT000000" '
           'adelaat@login.nikhef.nl:/data/hisparc/corsika/data/{seeds} '
           '{local}').format(seeds=seeds, local=LOCAL_STORE)
    result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    if not result == '':
        print 'Error occured: %s' % seeds
        raise Exception


def area_between(r1, r2):
    return abs((r1 * r1 - r2 * r2) * pi)


def plot_thickness(seed):
    plot = Plot('semilogx')
    plot2 = Plot('loglog')
    data_path = os.path.join(LOCAL_STORE, seed, 'corsika.h5')
    with tables.open_file(data_path) as data:
        particles = data.get_node('/groundparticles')
        core_distances = logspace(0, 5, 31)
        min_t = []
        lower_t = []
        low_t = []
        median_t = []
        high_t = []
        higher_t = []
        max_t = []
        distances = []
        density = []
        for r_inner, r_outer in zip(core_distances[:-1], core_distances[1:]):
            t = particles.read_where('(r >= %f) & (r <= %f) & '
                                     '(particle_id >= 2) & (particle_id <= 6)' %
                                     (r_inner, r_outer), field='t')

            if len(t) < 1:
                continue

            density.append(len(t) / area_between(r_outer, r_inner))
            distances.append(r_inner)
#             distances.append(10**((log10(r_outer) + log10(r_inner)) / 2))
            percentiles_t = percentile(t, [0, 5, 16, 50, 84, 95, 100])
            ref_t, lsig2_t, lsig1_t, med_t, hsig1_t, hsig2_t, m_t = \
                percentiles_t - percentiles_t[0]
            min_t.append(ref_t)
            lower_t.append(lsig2_t)
            low_t.append(lsig1_t)
            median_t.append(med_t)
            high_t.append(hsig1_t)
            higher_t.append(hsig2_t)
            max_t.append(m_t)

        header = data.get_node_attr('/', 'event_header')
        end = data.get_node_attr('/', 'event_end')
        energy = log10(header.energy)
        shower_size = log10(end.n_electrons_levels + end.n_muons_levels)
    plot.set_label('E=$10^{%.1f}$eV, size=$10^{%.1f}$' % (energy, shower_size))

    plot.plot(distances, median_t)
    plot.shade_region(distances, min_t, max_t, color='lightgray,semitransparent')
    plot.shade_region(distances, low_t, high_t, color='lightgray,semitransparent')
    plot.shade_region(distances, lower_t, higher_t, color='lightgray,semitransparent')
    plot.draw_horizontal_line(1500)
    plot.set_xlimits(min=.5, max=1e5)
    plot.set_xlabel(r'core distance')
    plot.set_ylabel(r'time after front')
    plot.save_as_pdf('plots/%.1f_%.1f_%s.pdf' % (energy, shower_size, seed))

    plot2.set_xlimits(min=.5, max=1e5)
    plot2.set_xlabel(r'core distance')
    plot2.set_ylabel(r'particle density')
    plot2.plot(distances, density)
    plot2.draw_horizontal_line(2.46)
#     plot2.draw_horizontal_line(0.6813)
    plot2.save_as_pdf('plots/%.1f_%.1f_%s_dens.pdf' % (energy, shower_size, seed))

if __name__ == "__main__":
#     for seeds in select_showers():
#         copy_shower(seeds)

    for seeds in select_showers():
        plot_thickness(seeds)
