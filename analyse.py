import numpy as np
import pylab as plt

import plot_pref as pp
from paths import paths
from testlist import get_tests
from delta import get


def print_delta_results(ids):
    """ Prints the average delta, the standard deviation and length in days

    """
    if type(ids) is int:
        ids = [ids]

    for id in ids:
        ext_timestamps, deltas = get(id)
        print "    % 3d  %s  % 7.2f  % 6.2f  % 4.2f" % (id,
            get_tests(id=id, part='group')[0].ljust(13),
            round(np.average(deltas), 2), round(np.std(deltas), 2),
            (max(ext_timestamps) - min(ext_timestamps)) / 864e11)


def plot_delta_histogram(ids, **kwargs):
    """ Plot a histogram of the deltas

    """
    if type(ids) is int:
        ids = [ids]

    #Define Bins
    low = -200
    high = 200
    bin_size = 1  # 2.5*n
    bins = np.arange(low - .5 * bin_size, high + bin_size, bin_size)

    #Begin Figure
    with pp.PlotFig(ttex=False, kind='pdf') as plot:
        for id in ids:
            ext_timestamps, deltas = get(id)
            plot.axe.hist(deltas, bins, normed=1, histtype='step', alpha=0.9,
                          label=get_tests(id=id, part='group')[0])
        if kwargs.keys():
            plt.title = 'Tijdtest ' + kwargs[kwargs.keys()[0]]
        plt.xlabel(r'$\Delta$ t (swap - reference) [ns]')
        plt.ylabel(r'p')
        plt.xlim(-200, 200)
        plt.ylim(0.0, 0.15)

        #Save Figure
        plot.path = paths('tt_plot')
        if len(ids) == 1:
            plot.name = 'tt_delta_hist_%03d' % ids[0]
        elif kwargs.keys():
            plot.name = 'tt_delta_hist_' + kwargs[kwargs.keys()[0]]
        plot.ltit = 'HII / GPS / TRIG'

    print 'tt_analyse: Plotted histogram'


def plot_delta_time(ids, **kwargs):
    """ Plot delta versus the timestamps

    """
    if type(ids) is int:
        ids = [ids]

    #Begin Figure
    with pp.PlotFig(ttex=False, kind='png') as plot:
        for id in ids:
            ext_timestamps, deltas = get(id)
            daystamps = (np.array(ext_timestamps) - min(ext_timestamps)) / 864e11
            plot.axe.scatter(daystamps, deltas,
                             marker='.', s=.1, edgecolors='none', alpha=1,
                             label=get_tests(id=id, part='group')[0])
        if kwargs.keys():
            plt.title = 'tt_delta_time_' + kwargs[kwargs.keys()[0]]
        plt.xlabel(r'Date and time of test')
        plt.ylabel(r'$\Delta$ t (swap - reference) [ns]')
        plt.xlim(0, max(daystamps))
        plt.ylim(-200, 200)
#        print (plot.axe.transData.transform([(0, 1)]) -
#               plot.axe.transData.transform((0, 0)))

        #Save Figure
        plot.path = paths('tt_plot')
        if len(ids) == 1:
            plot.name = 'tt_delta_time_%03d' % ids[0]
        elif kwargs.keys():
            plot.name = 'tt_delta_time_' + kwargs[kwargs.keys()[0]]
        plot.ltit = 'HII / GPS / TRIG'

    print 'tt_analyse: Plotted delta vs time'


if __name__ == '__main__':
#
#    all_groups = get_tests(part='group', subset='ALL')
#    plot_delta_histogram(all_groups, name='ALL')
#    pmt_groups = get_tests(part='group', subset='PMT')
#    plot_delta_histogram(pmt_groups, name='PMT')
#    ext_groups = get_tests(part='group', subset='EXT', complement=False)
#    plot_delta_histogram(ext_groups, name='EXT')
#    gps_groups = get_tests(part='group', subset='GPS', complement=False)
#    plot_delta_histogram(gps_groups, name='GPS')
#    bad_groups = get_tests(part='group', subset='Bad', complement=False)
#    plot_delta_histogram(bad_groups, name='Bad')
#    ext_comp_groups = get_tests(part='group', subset='EXT', complement=True)
#    plot_delta_histogram(ext_comp_groups, name='EXT_comp')
#    gps_comp_groups = get_tests(part='group', subset='GPS', complement=True)
#    plot_delta_histogram(gps_comp_groups, name='GPS_comp')
#    bad_comp_groups = get_tests(part='group', subset='Bad', complement=True)
#    plot_delta_histogram(bad_comp_groups, name='Bad_comp')

    groups = ['050/501/PMT2', '050/test/PMT1t']
    for group in groups:
        print_delta_results([group])
#        plot_delta_histogram([group])
#        plot_delta_time([group])

#    083_groups = get_tests(part='group', hisparc='083', complement=False)
#    plot_delta_histogram(083_groups)

#    all_groups = get_tests(part='group', subset='ALL')
#    for group in all_groups:
#        print_delta_results([group])
#        plot_delta_time([group])
#        plot_delta_histogram([group])
#    groups = get_tests(part='group', subset='Bad', complement=False)
#    plot_delta_time(groups, name='Bad')

    print 'Done'
