import glob
import os

import numpy as np

from artist import Plot

from sapphire.analysis.coincidence_queries import CoincidenceQuery
from sapphire.utils import angle_between

PATHS = '/Users/arne/Datastore/science_park_corsika/*_*/result.h5'


def analyse_reconstructions(path):
    seed = os.path.basename(os.path.dirname(path))

    cq = CoincidenceQuery(path)
    c_ids = cq.coincidences.get_where_list('N >= 3')
    if not len(cq.reconstructions) or not len(c_ids):
        cq.finish()
        return
    c_recs = cq.reconstructions.read_coordinates(c_ids)

    # Angles
    zen_out = c_recs['zenith']
    azi_out = c_recs['azimuth']
    zen_in = c_recs['reference_zenith']
    azi_in = c_recs['reference_azimuth']

    # Cores
    x_out = c_recs['x']
    y_out = c_recs['y']
    x_in = c_recs['reference_x']
    y_in = c_recs['reference_y']

    # Size
    size_out = c_recs['size']
    energy_out = c_recs['energy']
    size_in = c_recs['reference_size']
    energy_in = c_recs['reference_energy']

    energy = np.log10(energy_in[0])
    zenith = np.degrees(zen_in[0])
    label = r'$E=10^{%d}$eV, $\theta={%.1f}^{\circ}$' % (energy, zenith)

    # Azimuth
    bins = np.linspace(-np.pi, np.pi, 21)
    acounts_out, bins = np.histogram(azi_out, bins)
    acounts_in, bins = np.histogram(azi_in, bins)

    plota = Plot()
    plota.histogram(acounts_out, bins)
    plota.histogram(acounts_in, bins, linestyle='red')
    plota.set_xlabel(r'$\phi$ [\si{\radian}]')
    plota.set_xlimits(-np.pi, np.pi)
    plota.set_ylabel(r'Counts')
    plota.set_ylimits(min=0)
    plota.save_as_pdf('plots/azimuth_in_out_%s' % seed)

    # Zenith
    bins = np.linspace(0, np.pi / 2, 21)
    zcounts_out, bins = np.histogram(zen_out, bins)
    zcounts_in, bins = np.histogram(zen_in, bins)

    plotz = Plot()
    plotz.histogram(zcounts_out, bins)
    plotz.histogram(zcounts_in, bins, linestyle='red')
    plotz.set_xlabel(r'$\theta$ [\si{\radian}]')
    plotz.set_xlimits(0, np.pi / 2)
    plotz.set_ylabel(r'Counts')
    plotz.set_ylimits(min=0)
    plotz.save_as_pdf('plots/zenith_in_out_%s' % seed)

    # Angle between
    angle_distances = angle_between(zen_out, azi_out, zen_in, azi_in)
    if len(np.isfinite(angle_distances)):
        bins = np.linspace(0, np.pi / 2, 91)
        counts, bins = np.histogram(angle_distances, bins=bins)
        plotd = Plot()
        plotd.histogram(counts, np.degrees(bins))
        sigma = np.percentile(angle_distances[np.isfinite(angle_distances)], 67)
        plotd.set_label(label + r', 67\%% within \SI{%.1f}{\degree}' % np.degrees(sigma))
        plotd.set_xlabel(r'Angle between reconstructions [\si{\degree}]')
        plotd.set_ylabel('Counts')
        plotd.set_xlimits(np.degrees(bins[0]), np.degrees(bins[-1]))
        plotd.set_ylimits(min=0)
        plotd.save_as_pdf('plots/angle_between_in_out_%s' % seed)

    # Distance beween
    filter = size_out != 1e6
    core_distances = np.sqrt(
        (x_out.compress(filter) - x_in.compress(filter)) ** 2 + (y_out.compress(filter) - y_in.compress(filter)) ** 2
    )
    if len(np.isfinite(core_distances)):
        bins = np.linspace(0, 1000, 100)
        counts, bins = np.histogram(core_distances, bins=bins)
        plotc = Plot()
        plotc.histogram(counts, bins)
        sigma = np.percentile(core_distances[np.isfinite(core_distances)], 67)
        #
        energy = np.log10(energy_in[0])
        zenith = np.degrees(zen_in[0])
        #
        plotc.set_label(
            r'$E=10^{%d}$eV, $\theta={%.1f}^{\circ}$, 67\%% ' r'within \SI{%.1f}{\meter}' % (energy, zenith, sigma)
        )
        plotc.set_xlabel(r'Distance between cores [\si{\meter}]')
        plotc.set_ylabel('Counts')
        plotc.set_xlimits(bins[0], bins[-1])
        plotc.set_ylimits(min=0)
        plotc.save_as_pdf('plots/core_distance_between_in_out_%s' % seed)

    # Core positions
    filter = size_out != 1e6
    plotc = Plot()
    for x0, x1, y0, y1 in zip(x_out, x_in, y_out, y_in):
        plotc.plot([x0, x1], [y0, y1])
    plotc.set_xlabel(r'x [\si{\meter}]')
    plotc.set_ylabel(r'y [\si{\meter}]')
    plotc.set_xlimits(bins[0], bins[-1])
    plotc.set_ylimits(min=0)
    plotc.save_as_pdf('plots/core_positions_in_out_%s' % seed)

    # Shower size
    relative_size = size_out.compress(filter) / size_in.compress(filter)
    counts, bins = np.histogram(relative_size, bins=np.logspace(-2, 2, 21))
    plots = Plot('semilogx')
    plots.histogram(counts, bins)
    plots.set_xlabel('Relative size')
    plots.set_ylabel('Counts')
    plots.set_xlimits(bins[0], bins[-1])
    plots.set_ylimits(min=0)
    plots.save_as_pdf('plots/size_in_out_%s' % seed)

    # Cleanup
    cq.finish()


if __name__ == '__main__':
    for path in glob.glob(PATHS):
        print(path)
        analyse_reconstructions(path)

#     size_out, relative_size = analyse_reconstructions('/Users/arne/Datastore/science_park_corsika/574293039_83699616/result.h5')
