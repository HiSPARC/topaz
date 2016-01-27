import numpy as np
import tables

from artist import MultiPlot


EVENTDATA_PATH = '/Users/arne/Datastore/501_510/e_501_510_141101_150201.h5'


def plot_densities(data):
    """Make particle count plots for each detector to compare densities/responses"""

    n_min = 0.5  # remove gamma peak
    n_max = 50
    bins = np.linspace(np.log10(n_min), np.log10(n_max), 60)

    for station_number in [501, 510]:
        events = data.get_node('/s%d' % station_number, 'events')
        average_n = (events.col('n1') + events.col('n2') + events.col('n3') + events.col('n4')) / 4.
        n = [events.col('n1'), events.col('n2'), events.col('n3'), events.col('n4')]

        for minn in [0, 1, 2, 4, 8, 16]:
            filter = (average_n > minn) & (n[0] > 0) & (n[1] > 0) & (n[2] > 0) & (n[3] > 0)
            plot = MultiPlot(4, 4, width=r'.25\linewidth',
                                   height=r'.25\linewidth')
            for i in range(4):
                for j in range(4):
                    if i < j:
                        continue
                    elif i == j:
                        ncounts, x, y = np.histogram2d(np.log10(average_n.compress(filter)),
                                                       np.log10(n[i].compress(filter)),
                                                       bins=bins)
                    else:
                        ncounts, x, y = np.histogram2d(np.log10(n[i].compress(filter)),
                                                       np.log10(n[j].compress(filter)),
                                                       bins=bins)
                    subplot = plot.get_subplot_at(i, j)
                    subplot.histogram2d(ncounts, x, y, type='reverse_bw',
                                        bitmap=True)
            plot.set_xlimits_for_all(min=0, max=np.log10(n_max))
            plot.set_ylimits_for_all(min=0, max=np.log10(n_max))
            plot.show_xticklabels_for_all([(3, 0), (3, 1), (3, 2), (3, 3)])
            plot.show_yticklabels_for_all([(0, 3), (1, 3), (2, 3), (3, 3)])
        #     plot.set_title(0, 1, 'Particle counts for station 501 and 510')
            for i in range(4):
                plot.set_subplot_xlabel(0, i, 'detector %d' % (i + 1))
                plot.set_subplot_ylabel(i, 0, 'detector %d' % (i + 1))
            plot.set_xlabel('Number of particles')
            plot.set_ylabel('Number of particles')
            plot.save_as_pdf('plots/n_minn%d_%d' % (minn, station_number))


if __name__ == '__main__':
    with tables.open_file(EVENTDATA_PATH, 'r') as data:
        plot_densities(data)
