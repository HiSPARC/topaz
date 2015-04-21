import numpy as np
import tables

from artist import Plot, MultiPlot


COINDATA_PATH = '/Users/arne/Datastore/501_510/c_501_510_141101_150201.h5'


def plot_densities(data):
    """Make particle count plots for each detector to compare densities/responses"""

    e501 = data.get_node('/hisparc/cluster_amsterdam/station_501', 'events')
    e510 = data.get_node('/hisparc/cluster_amsterdam/station_510', 'events')

    sn501 = e501.col('n1') + e501.col('n2') + e501.col('n3') + e501.col('n4')
    sn510 = e510.col('n1') + e510.col('n2') + e510.col('n3') + e510.col('n4')
    n501 = [e501.col('n1'), e501.col('n2'), e501.col('n3'), e501.col('n4')]
    n510 = [e510.col('n1'), e510.col('n2'), e510.col('n3'), e510.col('n4')]

    n_min = 0.001  # remove peak at 0
    n_max = 9
    bins = np.linspace(n_min, n_max, 80)

    for minn in [0, 1, 2, 4, 8, 16]:
        filter = sn501 > minn
        plot = MultiPlot(4, 4, width=r'.25\linewidth',
                               height=r'.25\linewidth')
        for i in range(4):
            for j in range(4):
                ncounts, x, y = np.histogram2d(n501[i].compress(filter),
                                               n510[j].compress(filter),
                                               bins=bins)
                subplot = plot.get_subplot_at(i, j)
                subplot.histogram2d(ncounts, x, y, type='reverse_bw',
                                    bitmap=True)
        plot.set_xlimits_for_all(min=0, max=n_max)
        plot.set_ylimits_for_all(min=0, max=n_max)
        plot.show_xticklabels_for_all([(3, 0), (3, 1), (3, 2), (3, 3)])
        plot.show_yticklabels_for_all([(0, 3), (1, 3), (2, 3), (3, 3)])
    #     plot.set_title(0, 1, 'Particle counts for station 501 and 510')
        for i in range(4):
            plot.set_subplot_xlabel(0, i, 'detector %d' % (i + 1))
            plot.set_subplot_ylabel(i, 0, 'detector %d' % (i + 1))
        plot.set_xlabel('Number of particles 501')
        plot.set_ylabel('Number of particles 510')
        plot.save_as_pdf('n_minn%d_501_510' % minn)


    ncounts, x, y = np.histogram2d(sn501, sn510,
                                   bins=np.linspace(0, 20, 80))
    plot = Plot()
    plot.histogram2d(ncounts, x, y, type='reverse_bw', bitmap=True)
    plot.set_xlimits(min=0)
    plot.set_ylimits(min=0)
    plot.set_title('Particle counts for station 501 and 510')
    plot.set_xlabel('Number of particles 501')
    plot.set_ylabel('Number of particles 510')
    plot.save_as_pdf('n_501_510_sum')


if __name__ == '__main__':
    with tables.open_file(COINDATA_PATH, 'r') as data:
        plot_densities(data)
