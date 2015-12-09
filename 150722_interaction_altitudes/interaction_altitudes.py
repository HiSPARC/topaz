from artist import Plot
import tables
from numpy import (median, percentile, histogram, arange, histogram2d,
                   logspace, linspace, log10, floor, ceil)

from sapphire import CorsikaQuery

# proton = 14
# iron = 5626

OVERVIEW = '/Users/arne/Datastore/CORSIKA/corsika_overview.h5'


def plot_interaction_height(cq):
    plot = Plot()
    sims = cq.sims

    p = 'proton'
    for e in sorted(cq.available_parameters('energy', particle=p)):
        median_altitude = []
        min_altitude = []
        max_altitude = []
        zeniths = []
        for z in sorted(cq.available_parameters('zenith', particle=p, energy=e)):
            selection = cq.simulations(particle=p, energy=e, zenith=z)
            if len(selection) > 100:
                interaction_altitudes = selection['first_interaction_altitude'] / 1e3
                median_altitude.append(median(interaction_altitudes))
                min_altitude.append(percentile(interaction_altitudes, 2))
                max_altitude.append(percentile(interaction_altitudes, 98))
                zeniths.append(z)
        if len(zeniths):
            plot.plot(zeniths + (e - 12) / 3., median_altitude)
#             plot.shade_region(zeniths, min_altitude, max_altitude,
#                               color='lightgray,semitransparent')
            plot.add_pin('%.1f' % e, relative_position=0)
    plot.set_ylabel(r'First interaction altitude [\si{\kilo\meter}]')
    plot.set_xlabel(r'Zenith [\si{\radian}]')
    plot.save_as_pdf('interaction_altitude')


def plot_interaction_altitude_distribution(cq):
    altitudes = cq.sims.col('first_interaction_altitude') / 1e3
    bins = arange(0, 100, 2)
    counts, bins = histogram(altitudes, bins, normed=True)
    plot = Plot()
    plot.histogram(counts, bins)
    plot.draw_vertical_line(median(altitudes), linestyle='red')
    plot.set_xlabel(r'First interaction altitude [m]')
    plot.set_ylabel(r'Counts')
    plot.save_as_pdf('interaction_altitude_distribution')


def plot_interaction_altitude_size(cq):
    for z in cq.available_parameters('zenith'):
        sims = cq.simulations(zenith=z)
        altitudes = sims['first_interaction_altitude'] / 1e3
        size = sims['n_electron'] + sims['n_muon']
        alt_size_hist = histogram2d(altitudes, size,
                                    bins=[linspace(0, 70, 100),
                                          logspace(0, 9, 100)])
    #                                       logspace(max(floor(log10(min(size))), 0),
    #                                                ceil(log10(max(size))), 100)])
        plot = Plot('semilogy')
        plot.histogram2d(*alt_size_hist, bitmap=True, type='color')
        plot.set_xlabel(r'First interaction altitude [m]')
        plot.set_ylabel(r'Shower size')
        plot.save_as_pdf('interaction_altitude_v_size_%.1f.pdf' % z)


if __name__ == "__main__":
    cq = CorsikaQuery(OVERVIEW)
    plot_interaction_height(cq)
    plot_interaction_altitude_distribution(cq)
    plot_interaction_altitude_size(cq)
    cq.finish()
