"""Compare predicted detector density to the detected number of particles"""

import tables
from numpy import histogram2d, histogram, linspace, logspace, log10, inf

from artist import Plot, MultiPlot

DATA_PATH = '/Volumes/Tendrando Arms/Datastore/kascade/kascade-20080912.h5'


def plot_kascade_v_hisparc(data):
    recs = data.root.reconstructions
    n1 = recs.col('n1')
    n2 = recs.col('n2')
    n3 = recs.col('n3')
    n4 = recs.col('n4')
    ni = [n1, n2, n3, n4]
    n = (n1 + n2 + n3 + n4) / 4.

    k_ni = recs.col('k_dens_mu') + recs.col('k_dens_e')
    k_n1 = k_ni[:, 0]
    k_n2 = k_ni[:, 1]
    k_n3 = k_ni[:, 2]
    k_n4 = k_ni[:, 3]
    k_n = k_ni.sum(axis=1) / 4.

    lin_bins = linspace(0, 15, 200)
    bins = logspace(-0.5, 1.7, 100)
    bins = linspace(-0.5, log10(50), 100)

    colors = ['black', 'red', 'green', 'blue']

    plot = Plot('semilogy')
    plot.histogram(*histogram(n, bins=lin_bins), linestyle='dotted')
    plot.histogram(*histogram(k_n, bins=lin_bins), linestyle='dashed, gray')

    for i in range(4):
        plot.histogram(*histogram(ni[i], bins=lin_bins), linestyle=colors[i])
        plot.histogram(*histogram(k_ni[:, i], bins=lin_bins), linestyle='gray!50!%s' % colors[i])
    plot.set_ylimits(min=.5)
    plot.set_xlimits(min=lin_bins[0], max=lin_bins[-1])
    plot.set_xlabel(r'Lepton density [\si{\per\meter\squared}]')
    plot.set_ylabel(r'Counts')
    plot.save_as_pdf('histogram')

    mplot = MultiPlot(2, 2, width=r'.3\linewidth', height=r'.3\linewidth')
    for i in range(4):
        splot = mplot.get_subplot_at(i / 2, i % 2)
        counts, xbins, ybins = histogram2d(log10(recs.col('n%d' % (i + 1))), log10(k_ni[:, i]), bins=bins)
        counts = log10(counts)
        counts[counts == -inf] = 0
        splot.histogram2d(counts, xbins, ybins,
                          bitmap=True, type='reverse_bw')
        splot.plot([-10, max(bins)], [-10, max(bins)], linestyle='red', mark=None)
    mplot.show_xticklabels_for_all([(1, 0), (0, 1)])
    mplot.show_yticklabels_for_all([(1, 0), (0, 1)])
    mplot.set_xlabel(r'HiSPARC detected density [$\log(\rho/\si{\per\meter\squared})$]')
    mplot.set_ylabel(r'KASCADE predicted density [$\log(\rho/\si{\per\meter\squared})$]')
    mplot.save_as_pdf('hisparc_v_kascade_detectors')

    plot = Plot()
    counts, xbins, ybins = histogram2d(log10(n), log10(k_n), bins=bins)
    counts = log10(counts)
    counts[counts == -inf] = 0
    plot.histogram2d(counts, xbins, ybins, bitmap=True, type='reverse_bw')
    plot.plot([-10, max(bins)], [-10, max(bins)], linestyle='red', mark=None)
    plot.set_xlabel(r'HiSPARC detected density [$\log(\rho/\si{\per\meter\squared})$]')
    plot.set_ylabel(r'KASCADE predicted density [$\log(\rho/\si{\per\meter\squared})$]')
    plot.save_as_pdf('hisparc_v_kascade')


if __name__ == "__main__":
    with tables.open_file(DATA_PATH, 'r') as data:
        plot_kascade_v_hisparc(data)
