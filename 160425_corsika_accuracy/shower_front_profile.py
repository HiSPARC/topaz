""" Plot the temporal profile of the shower front

Examine separately for gammas, electrons, muons.
Plot the shower profile as function of the shower core.

The thickness of the shower front increases further from the core.
Moreover, the front is curved, further delayed at increasing core distances.

"""

from functools import partial

import tables

from numpy import degrees, histogram, histogram2d, log10, logspace, median, percentile, sqrt
from scipy.stats import binned_statistic

from artist import MultiPlot

from sapphire import CorsikaQuery
from sapphire.corsika.particles import name

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


SEEDS = [
    '1115962_287886190',
    '402530248_77483417',
    '343495036_732802158',
    '318293592_758814709',
    '772067892_538968191',
]  # , '477821264_628079401']

SEEDS_14 = ['651000510_222963176', '155366293_265066277', '758294490_567681579']
SEEDS_15 = ['791363922_262129855', '291305112_897286854', '683790878_143722028']
SEEDS_16 = ['149042664_130233131', '108507276_832136747', '458273069_189490816']

SEEDS = SEEDS_16  # SEEDS_14 + SEEDS_15 + SEEDS_16

OVERVIEW = '/Users/arne/Datastore/CORSIKA/corsika_overview.h5'
PATH = '/Users/arne/Datastore/CORSIKA/%s/corsika.h5'


def plot_shower_profile(seeds):

    with tables.open_file(PATH % seeds) as data:
        gp = data.root.groundparticles

        min_t = gp.col('t').min()

        print('Making plots for %s' % seeds)

        gamma = gp.read_where('particle_id == 1')
        electrons = gp.read_where('(particle_id == 3) | (particle_id == 4)')
        muons = gp.read_where('(particle_id == 5) | (particle_id == 6)')

        for correction in ['none', 'median_self']:
            plot = MultiPlot(3, 1, 'semilogx', height=r'.4\linewidth')

            splot = plot.get_subplot_at(0, 0)
            splot.set_ylabel('Gamma')
            plot_statistics(seeds, splot, gamma['r'], gamma['t'] - min_t, 'solid', correction=correction)

            splot = plot.get_subplot_at(1, 0)
            splot.set_ylabel('Electrons')
            plot_statistics(seeds, splot, electrons['r'], electrons['t'] - min_t, 'solid', correction=correction)

            splot = plot.get_subplot_at(2, 0)
            splot.set_ylabel('Muon')
            plot_statistics(seeds, splot, muons['r'], muons['t'] - min_t, 'solid', correction=correction)

            plot.set_xlimits_for_all(None, 1e0, 1e3)
            if correction == 'median_self':
                plot.set_ylimits_for_all(None, -120, 120)
            else:
                plot.set_ylimits_for_all(None, 0, 120)
            plot.show_xticklabels(2, 0)
            plot.show_yticklabels_for_all()
            plot.set_ylabel(r'Arrival time [\si{\ns}]')
            plot.set_xlabel(r'Core distance [\si{\meter}]')
            plot.set_title(0, 0, get_info_string_tex(seeds))
            plot.save_as_pdf('plots/time_profile/%s_%s.pdf' % (get_info_string(seeds), correction))


def plot_shower_profile_for_bin(seeds):

    with tables.open_file(PATH % seeds) as data:
        gp = data.root.groundparticles

        min_r = 40
        max_r = 60

        min_t = gp.col('t').min()

        gamma = gp.read_where('(particle_id == 1) & (r > min_r) & (r < max_r)')
        electrons = gp.read_where('(particle_id >= 3) & (particle_id <= 4) & (r > min_r) & (r < max_r)')
        muons = gp.read_where('(particle_id >= 5) & (particle_id <= 6) & (r > min_r) & (r < max_r)')

        gamma_t = gamma['t'] - min_t
        electrons_t = electrons['t'] - min_t
        muons_t = muons['t'] - min_t
        #         plot_time_profile_for_bin(seeds, gamma_t, electrons_t, muons_t)

        gamma_e = particle_energies(gamma)
        electrons_e = particle_energies(electrons)
        muons_e = particle_energies(muons)
        #         plot_energy_profile_for_bin(seeds, gamma_e, electrons_e, muons_e)

        plot_energy_v_time_for_bin(seeds, gamma_t, electrons_t, muons_t, gamma_e, electrons_e, muons_e)


def plot_time_profile_for_bin(seeds, gamma_t, electrons_t, muons_t):

    plot = MultiPlot(3, 1, 'semilogx', height=r'.4\linewidth')
    bins = logspace(
        log10(min(gamma_t.min(), electrons_t.min(), muons_t.min())),
        log10(max(gamma_t.max(), electrons_t.max(), muons_t.max())),
        25,
    )
    for splot, data, particle_name in zip(
        plot.subplots, [gamma_t, electrons_t, muons_t], ['Gamma', 'Electrons', 'Muons']
    ):
        splot.set_ylabel(particle_name)
        splot.histogram(*histogram(data, bins=bins))

    plot.set_xlimits_for_all(None, bins[0], bins[-1])
    #         plot.set_ylimits_for_all(None, 0, 120)
    plot.show_xticklabels(2, 0)
    plot.show_yticklabels_for_all()
    plot.set_ylabel(r'Number of particles')
    plot.set_xlabel(r'Arrival time [\si{\ns}]')
    plot.save_as_pdf('plots/time_profile_bin/%s.pdf' % get_info_string(seeds))


def plot_energy_profile_for_bin(seeds, gamma_e, electrons_e, muons_e):

    plot = MultiPlot(3, 1, 'semilogx', height=r'.4\linewidth')
    print('Min gamma/electron energy: %d MeV,  %d MeV' % (gamma_e.min() * 1e-6, electrons_e.min() * 1e-6))
    print('Min muon energy: %d MeV' % (muons_e.min() * 1e-6,))
    bins = logspace(6, 12, 40)
    for splot, data, particle_name in zip(
        plot.subplots, [gamma_e, electrons_e, muons_e], ['Gamma', 'Electrons', 'Muons']
    ):
        splot.set_ylabel(particle_name)
        splot.draw_vertical_line(300e6 if particle_name == 'Muons' else 3e6, 'red')
        splot.histogram(*histogram(data, bins=bins))

    plot.set_xlimits_for_all(None, bins[0], bins[-1])
    # plot.set_ylimits_for_all(None, 0, 120)
    plot.show_xticklabels(2, 0)
    plot.show_yticklabels_for_all()
    plot.set_ylabel(r'Number of particles')
    plot.set_xlabel(r'Particle energy [\si{\MeV}]')
    plot.save_as_pdf('plots/energy_profile_bin/%s.pdf' % get_info_string(seeds))


def plot_energy_v_time_for_bin(seeds, gamma_t, electrons_t, muons_t, gamma_e, electrons_e, muons_e):

    plot = MultiPlot(3, 1, 'loglog', height=r'.3\linewidth')
    e_bins = logspace(6, 12, 40)
    t_bins = logspace(
        log10(min(gamma_t.min(), electrons_t.min(), muons_t.min())),
        log10(max(gamma_t.max(), electrons_t.max(), muons_t.max())),
        25,
    )

    for splot, t_data, e_data, particle_name in zip(
        plot.subplots, [gamma_t, electrons_t, muons_t], [gamma_e, electrons_e, muons_e], ['Gamma', 'Electrons', 'Muons']
    ):
        splot.set_ylabel(particle_name)
        counts, e_bins, t_bins = histogram2d(e_data, t_data, bins=[e_bins, t_bins])
        splot.histogram2d(counts, e_bins, t_bins, type='color', colormap='viridis', bitmap=True)
        splot.draw_vertical_line(300e6 if particle_name == 'Muons' else 3e6, 'red')

    #         plot.set_xlimits_for_all(None, bins[0], bins[-1])
    #         plot.set_ylimits_for_all(None, 0, 120)
    plot.show_xticklabels(2, 0)
    plot.show_yticklabels_for_all()
    plot.subplots[-1].set_xlabel(r'Particle energy [\si{\MeV}]')
    plot.set_ylabel(r'Arrival time [\si{\ns}]')
    plot.save_as_pdf('plots/time_energy_profile/%s.pdf' % get_info_string(seeds))


def plot_energy_v_time(seeds):

    with tables.open_file(PATH % seeds) as data:
        gp = data.root.groundparticles

        min_t = gp.col('t').min()

        gamma = gp.read_where('(particle_id == 1)')
        electrons = gp.read_where('(particle_id >= 3) & (particle_id <= 4)')
        muons = gp.read_where('(particle_id >= 5) & (particle_id <= 6)')

        gamma_t = gamma['t'] - min_t
        electrons_t = electrons['t'] - min_t
        muons_t = muons['t'] - min_t

        gamma_e = particle_energies(gamma)
        electrons_e = particle_energies(electrons)
        muons_e = particle_energies(muons)

    plot = MultiPlot(3, 1, 'loglog', height=r'.3\linewidth')
    e_bins = logspace(6, 12, 40)
    t_bins = logspace(-1, 3, 25)

    for splot, t_data, e_data, particle_name in zip(
        plot.subplots, [gamma_t, electrons_t, muons_t], [gamma_e, electrons_e, muons_e], ['Gamma', 'Electrons', 'Muons']
    ):
        splot.set_ylabel(particle_name)
        counts, e_bins, t_bins = histogram2d(e_data, t_data, bins=[e_bins, t_bins])
        splot.histogram2d(counts, e_bins, t_bins, type='color', colormap='viridis', bitmap=True)
        splot.draw_vertical_line(300e6 if particle_name == 'Muons' else 3e6, 'red')

    #         plot.set_xlimits_for_all(None, bins[0], bins[-1])
    #         plot.set_ylimits_for_all(None, 0, 120)
    plot.show_xticklabels(2, 0)
    plot.show_yticklabels_for_all()
    plot.subplots[-1].set_xlabel(r'Particle energy [\si{\MeV}]')
    plot.set_ylabel(r'Arrival time [\si{\ns}]')
    plot.save_as_pdf('plots/time_energy_2D/%s.pdf' % get_info_string(seeds))


def plot_energy_v_distance(seeds):

    with tables.open_file(PATH % seeds) as data:
        gp = data.root.groundparticles

        gamma = gp.read_where('particle_id == 1')
        electrons = gp.read_where('(particle_id == 3) | (particle_id == 4)')
        muons = gp.read_where('(particle_id == 5) | (particle_id == 6)')

        gamma_r = gamma['r']
        electrons_r = electrons['r']
        muons_r = muons['r']

        gamma_e = particle_energies(gamma)
        electrons_e = particle_energies(electrons)
        muons_e = particle_energies(muons)

        plot = MultiPlot(3, 1, 'loglog', height=r'.3\linewidth')
        r_bins = logspace(1, 3, 20)
        e_bins = logspace(6, 12, 40)

        for splot, r_data, e_data, particle_name in zip(
            plot.subplots,
            [gamma_r, electrons_r, muons_r],
            [gamma_e, electrons_e, muons_e],
            ['Gamma', 'Electrons', 'Muons'],
        ):
            splot.set_ylabel(particle_name)
            counts, r_bins, e_bins = histogram2d(r_data, e_data, bins=[r_bins, e_bins])
            splot.histogram2d(counts, r_bins, e_bins, type='color', colormap='viridis', bitmap=True)
            splot.draw_horizontal_line(300e6 if particle_name == 'Muons' else 3e6, 'red')

        #         plot.set_xlimits_for_all(None, bins[0], bins[-1])
        #         plot.set_ylimits_for_all(None, 0, 120)
        plot.show_xticklabels(2, 0)
        plot.show_yticklabels_for_all()
        plot.subplots[-1].set_xlabel(r'Core distance [\si{\meter}]')
        plot.set_ylabel(r'Particle energy [\si{\MeV}]')
        plot.save_as_pdf('plots/distance_energy_2D/%s.pdf' % get_info_string(seeds))


def particle_energies(particles):
    return sqrt(particles['p_x'] ** 2 + particles['p_y'] ** 2 + particles['p_z'] ** 2)


def plot_statistics(seeds, plot, r, t, style, correction='none'):
    """Plot statistics for shower front particles."""

    bins = logspace(1, 3, 20)
    n = bin_stats(r, t, 'count', bins)
    # FIXME; changes bin widths/centers..
    bins = bins.compress(n > 9)
    bin_mid = (bins[1:] + bins[:-1]) / 2.0

    quantiles = [2, 16, 25, 75, 84, 98]
    percentiles = [partial(percentile, q=q) for q in quantiles]

    if correction == 'median_self':
        cor_t = bin_stats(r, t, median, bins)
    if correction == 'min_self':
        cor_t = bin_stats(r, t, min, bins)
    if correction == 'none':
        cor_t = 0

    first_interaction_altitude = get_info(seeds)['first_interaction_altitude']
    causal = causal_front(first_interaction_altitude, bin_mid) - cor_t
    plot.plot(bin_mid, causal, mark=None, linestyle='purple, dashed')

    for quan, perc in zip(quantiles, percentiles):
        plot.plot(
            bin_mid, bin_stats(r, t, perc, bins) - cor_t, mark=None, linestyle='black!%d!gray, %s' % (quan, style)
        )

    plot.plot(bin_mid, bin_stats(r, t, max, bins) - cor_t, mark=None, linestyle='red, %s' % style)
    plot.plot(bin_mid, bin_stats(r, t, median, bins) - cor_t, mark=None, linestyle='green, %s' % style)
    plot.plot(bin_mid, bin_stats(r, t, min, bins) - cor_t, mark=None, linestyle='blue, %s' % style)


#     plot.plot(bin_mid, bin_stats(r, t, mean, bins) - med_t,
#               mark=None, linestyle='orange, %s' % style)


def causal_front(first_interaction_altitude, x):
    r = first_interaction_altitude
    return r - sqrt(r**2 - x**2)


def bin_stats(r, t, stat, bins):
    return binned_statistic(r, t, statistic=stat, bins=bins)[0]


def get_info(seeds):
    cq = CorsikaQuery(OVERVIEW)
    info = cq.get_info(seeds)
    cq.finish()
    return info


def get_info_string(seeds):
    info = get_info(seeds)
    return '%s_E_%.1f_Z_%.1f_I_%d_%s' % (
        name(info['particle_id']),
        log10(info['energy']),
        degrees(info['zenith']),
        info['first_interaction_altitude'] / 1e3,
        seeds,
    )


def get_info_string_tex(seeds):
    info = get_info(seeds)
    return r'%s, log10[E/\si{\eV}] = \SI{%.1f}, ' r'$\theta$ = \SI{%.1f}{\degree}, I = \SI{%d}{\km}' % (
        name(info['particle_id']),
        log10(info['energy']),
        degrees(info['zenith']),
        info['first_interaction_altitude'] / 1e3,
    )


if __name__ == "__main__":
    for seeds in SEEDS:
        plot_energy_v_time(seeds)
        plot_shower_profile_for_bin(seeds)
        plot_energy_v_distance(seeds)
        plot_shower_profile(seeds)
