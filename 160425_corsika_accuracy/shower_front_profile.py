""" Plot the temporal profile of the shower front

Examine separately for gammas, electrons, muons.
Plot the shower profile as function of the shower core.

The thickness of the shower front increases further from the core.
Moreover, the front is curved, further delayed at increasing core distances.

"""

from functools import partial

import tables
from numpy import (mean, median, logspace, percentile, append,
                   linspace, histogram, log10, sqrt)
from scipy.stats import binned_statistic

from artist import Plot, MultiPlot

# Using showers of various energies, and selected the median shower by size:
# 1115962_287886190   14.5
# 402530248_77483417  15
# 343495036_732802158 15 -smallest
# 318293592_758814709 15 -largest
# 772067892_538968191 16
# 477821264_628079401 17

# Selected by median interaction altitude, proton/iron/gamma.
#
# 14
# 651000510_222963176
# 155366293_265066277
# 758294490_567681579
#
# 15
# 791363922_262129855
# 291305112_897286854
# 683790878_143722028
#
# 16
# 149042664_130233131
# 108507276_832136747
# 458273069_189490816


SEEDS = ['1115962_287886190', '402530248_77483417', '343495036_732802158',
         '318293592_758814709', '772067892_538968191'] #, '477821264_628079401']

SEEDS_14 = ['651000510_222963176', '155366293_265066277', '758294490_567681579']
SEEDS_15 = ['791363922_262129855', '291305112_897286854', '683790878_143722028']
SEEDS_16 = ['149042664_130233131', '108507276_832136747', '458273069_189490816']

SEEDS = SEEDS_16

PATH = '/Users/arne/Datastore/CORSIKA/%s/corsika.h5'


def plot_shower_profile(seeds):

    with tables.open_file(PATH % seeds) as data:
        gp = data.root.groundparticles

        min_t = gp.col('t').min()

        print 'Getting data for %s' % seeds

        gamma = gp.read_where('particle_id == 1')
        electrons = gp.read_where('(particle_id == 3) | (particle_id == 4)')
        muons = gp.read_where('(particle_id == 5) | (particle_id == 6)')

        print 'Determining statistics and plotting data:',

        plot = MultiPlot(3, 1, 'semilogx', height=r'.4\linewidth')

        print 'Gamma,',
        splot = plot.get_subplot_at(0, 0)
        splot.set_ylabel('Gamma')
        plot_statistics(splot, gamma['r'], gamma['t'] - min_t, 'solid')
        print 'Electron,',
        splot = plot.get_subplot_at(1, 0)
        splot.set_ylabel('Electrons')
        plot_statistics(splot, electrons['r'], electrons['t'] - min_t, 'solid')
        print 'Muon.'
        splot = plot.get_subplot_at(2, 0)
        splot.set_ylabel('Muon')
        plot_statistics(splot, muons['r'], muons['t'] - min_t, 'solid')

        plot.set_xlimits_for_all(None, 1e0, 1e3)
        plot.set_ylimits_for_all(None, 0, 120)
        plot.show_xticklabels(2, 0)
        plot.show_yticklabels_for_all()
        plot.set_ylabel(r'Arrival time [\si{\ns}]')
        plot.set_xlabel(r'Core distance [\si{\meter}]')

        plot.save_as_pdf('plots/shower_profile_%s' % seeds)


def plot_shower_profile_for_bin(seeds):

    with tables.open_file(PATH % seeds) as data:
        gp = data.root.groundparticles

        min_r = 44
        max_r = 63

        min_t = gp.col('t').min()

        gamma = gp.read_where('(particle_id == 1) & (r > min_r) & (r < max_r)')
        electrons = gp.read_where('(particle_id >= 3) & (particle_id <= 4) & (r > min_r) & (r < max_r)')
        muons = gp.read_where('(particle_id >= 5) & (particle_id <= 6) & (r > min_r) & (r < max_r)')

        gamma_t = gamma['t'] - min_t
        electrons_t = electrons['t'] - min_t
        muons_t = muons['t'] - min_t
        plot_time_profile_for_bin(seeds, gamma_t, electrons_t, muons_t)

        gamma_e = particle_energies(gamma)
        electrons_e = particle_energies(electrons)
        muons_e = particle_energies(muons)
        plot_energy_profile_for_bin(seeds, gamma_e, electrons_e, muons_e)


def plot_time_profile_for_bin(seeds, gamma_t, electrons_t, muons_t):

        plot = MultiPlot(3, 1, 'semilogx', height=r'.4\linewidth')
        bins = logspace(log10(min(gamma_t.min(), electrons_t.min(), muons_t.min())),
                        log10(max(gamma_t.max(), electrons_t.max(), muons_t.max())),
                        25)
        for splot, data, name in zip(plot.subplots, [gamma_t, electrons_t, muons_t],
                                     ['Gamma', 'Electrons', 'Muons']):
            splot.set_ylabel(name)
            splot.histogram(*histogram(data, bins=bins))

        plot.set_xlimits_for_all(None, bins[0], bins[-1])
#         plot.set_ylimits_for_all(None, 0, 120)
        plot.show_xticklabels(2, 0)
        plot.show_yticklabels_for_all()
        plot.set_ylabel(r'Number of particles')
        plot.set_xlabel(r'Arrival time [\si{\ns}]')
        plot.save_as_pdf('plots/shower_profile_for_bin_%s' % seeds)


def plot_energy_profile_for_bin(seeds, gamma_e, electrons_e, muons_e):

        plot = MultiPlot(3, 1, 'semilogx', height=r'.4\linewidth')
        print 'Min gamma/electron energy:', gamma_e.min() * 1e-6, electrons_e.min() * 1e-6
        print 'Min muon energy:', muons_e.min() * 1e-6
        bins = logspace(6, 12, 40)
        for splot, data, name in zip(plot.subplots, [gamma_e, electrons_e, muons_e],
                                     ['Gamma', 'Electrons', 'Muons']):
            splot.set_ylabel(name)
            splot.histogram(*histogram(data, bins=bins))

        plot.set_xlimits_for_all(None, bins[0], bins[-1])
#         plot.set_ylimits_for_all(None, 0, 120)
        plot.show_xticklabels(2, 0)
        plot.show_yticklabels_for_all()
        plot.set_ylabel(r'Number of particles')
        plot.set_xlabel(r'Particle energy')
        plot.save_as_pdf('plots/energy_profile_for_bin_%s' % seeds)


def particle_energies(particles):
    return sqrt(particles['p_x'] ** 2 + particles['p_y'] ** 2 +
                particles['p_z'] ** 2)


def plot_statistics(plot, r, t, style, correction='none'):
    """Plot statistics for shower front particles."""

    bins = logspace(0, 3, 20)
    bin_mid = (bins[1:] + bins[:-1]) / 2.

    n = bin_stats(r, t, 'count', bins)
    bins = bins.compress(n > 9)
    bin_mid = (bins[1:] + bins[:-1]) / 2.

    quantiles = [2, 16, 25, 75, 84, 98]
    percentiles = [partial(percentile, q=q) for q in quantiles]

    if correction == 'median_self':
        cor_t = bin_stats(r, t, median, bins)
    if correction == 'min_self':
        cor_t = bin_stats(r, t, min, bins)
    if correction == 'none':
        cor_t = 0

    for quan, perc in zip(quantiles, percentiles):
        plot.plot(bin_mid, bin_stats(r, t, perc, bins) - cor_t,
                  mark=None, linestyle='black!%d!gray, %s' % (quan, style))

    plot.plot(bin_mid, bin_stats(r, t, max, bins) - cor_t,
              mark=None, linestyle='red, %s' % style)
    plot.plot(bin_mid, bin_stats(r, t, median, bins) - cor_t,
              mark=None, linestyle='green, %s' % style)
    plot.plot(bin_mid, bin_stats(r, t, min, bins) - cor_t,
              mark=None, linestyle='blue, %s' % style)
#     plot.plot(bin_mid, bin_stats(r, t, mean, bins) - med_t,
#               mark=None, linestyle='orange, %s' % style)


def bin_stats(r, t, stat, bins):
    return binned_statistic(r, t, statistic=stat, bins=bins)[0]


if __name__ == "__main__":
    for seeds in SEEDS:
#         plot_shower_profile_for_bin(seeds)
        plot_shower_profile(seeds)
