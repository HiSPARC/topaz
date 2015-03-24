import itertools

import numpy as np
from numpy import nan, isnan, arange, histogram, linspace, pi, array, sqrt, degrees
from scipy.stats import scoreatpercentile
import tables

from artist import Plot, PolarPlot

from sapphire.utils import pbar, gauss, ERR, angle_between


DATA_PATH = 'kascade.h5'


def plot_angles(data):
    """Make azimuth and zenith plots to compare the results"""

    rec = data.root.reconstructions

    zenhis = rec.col('reconstructed_theta')
    zenkas = rec.col('reference_theta')
    azihis = rec.col('reconstructed_phi')
    azikas = rec.col('reference_phi')
    min_n = rec.col('min_n134')

    high_zenith = (zenhis > .2) & (zenkas > .2)

    for minn in [0, 1, 2, 4]:
        filter = (min_n > minn)

        azicounts, x, y = np.histogram2d(azihis.compress(high_zenith & filter),
                                         azikas.compress(high_zenith & filter),
                                         bins=np.linspace(-pi, pi, 73))
        plota = Plot()
        plota.histogram2d(azicounts, degrees(x), degrees(y), type='reverse_bw', bitmap=True)
#         plota.set_title('Reconstructed azimuths for events in coincidence (zenith gt .2 rad)')
        plota.set_xlabel(r'$\phi_\textrm{HiSPARC}$ [\si{\degree}]')
        plota.set_ylabel(r'$\phi_\textrm{KASCADE}$ [\si{\degree}]')
        plota.set_xticks([-180, -90, 0, 90, 180])
        plota.set_yticks([-180, -90, 0, 90, 180])
        plota.save_as_pdf('azimuth_his_kas_minn%d' % minn)

        zencounts, x, y = np.histogram2d(zenhis.compress(filter),
                                         zenkas.compress(filter),
                                         bins=np.linspace(0, pi / 3., 41))
        plotz = Plot()
        plotz.histogram2d(zencounts, degrees(x), degrees(y), type='reverse_bw', bitmap=True)
#         plotz.set_title('Reconstructed zeniths for station events in coincidence')
        plotz.set_xlabel(r'$\theta_\textrm{HiSPARC}$ [\si{\degree}]')
        plotz.set_ylabel(r'$\theta_\textrm{KASCADE}$ [\si{\degree}]')
        plotz.set_xticks([0, 15, 30, 45, 60])
        plotz.set_yticks([0, 15, 30, 45, 60])
        plotz.save_as_pdf('zenith_his_kas_minn%d' % minn)

        distances = angle_between(zenhis.compress(filter), azihis.compress(filter),
                                  zenkas.compress(filter), azikas.compress(filter))
        counts, bins = np.histogram(distances, bins=linspace(0, pi, 100))
        plotd = Plot()
        plotd.histogram(counts, degrees(bins))
        sigma = degrees(scoreatpercentile(distances, 67))
        plotd.set_title(r'$N_\textrm{MIP} \geq %d$' % minn)
        plotd.set_label(r'67\%% within \SI{%.1f}{\degree}' % sigma)
        # plotd.set_title('Distance between reconstructed angles for station events')
        plotd.set_xlabel('Angle between reconstructions [\si{\degree}]')
        plotd.set_ylabel('Counts')
        plotd.set_xlimits(min=0, max=90)
        plotd.set_ylimits(min=0)
        plotd.save_as_pdf('angle_between_his_kas_minn%d' % minn)


if __name__ == '__main__':
    with tables.open_file(DATA_PATH, 'r') as data:
        plot_angles(data)
