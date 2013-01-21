import numpy as np
import pylab as plt

import plot_pref as pp
from paths import paths
from testlist import get_tests
from delta import get
from helper import nanoseconds_from_ext_timestamp, timestamps_from_ext_timestamp

def print_delta_results(ids=None):
    """ Prints the average delta, the standard deviation and length in days

    """
    if not ids:
        ids = get_tests(part='id')

    if type(ids) is int:
        ids = [ids]

    for id in ids:
        ext_timestamps, deltas = get(id)
        print "    % 3d  %s  % 7.2f  % 6.2f  % 4.2f" % (
                id, get_tests(id=id, part='group')[0].ljust(13),
                round(np.average(deltas), 2), round(np.std(deltas), 2),
                (max(ext_timestamps) - min(ext_timestamps)) / 864e11)


def print_pulse_frequency(ids=None):
    """ Prints the average delta, the standard deviation and length in days

    """
    if not ids:
        ids = get_tests(part='id')

    if type(ids) is int:
        ids = [ids]

    print "     id  his/gps/trg            mean           std           max           min"
    for id in ids:
        ts, deltas = get(id)
        intervals = np.array(ts[1:]) - np.array(ts[:-1])
        print "    % 3d  %s  % 12d  % 12d  % 12d  % 12d" % (
                id, get_tests(id=id, part='group')[0].ljust(13),
                round(np.average(intervals)), round(np.std(intervals)),
                max(intervals), min(intervals))


def plot_delta_test(ids, **kwargs):
    """ Plot the delta with std

    """
    if type(ids) is int:
        ids = [ids]

    #Define Bins
    low = -200
    high = 200
    bin_size = 1  # 2.5*n?
    bins = np.arange(low - .5 * bin_size, high + bin_size, bin_size)

    #Begin Figure
    with pp.PlotFig(texttex=True, kind='pdf', **kwargs) as plot:
        for id in ids:
            ext_timestamps, deltas = get(id)
            plot.axe.hist(deltas, bins, normed=1, histtype='step', alpha=0.9,
                          label=get_tests(id=id, part='legend')[0])
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
        plot.ltit = 'Tests'

    print 'tt_analyse: Plotted histogram'


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
    with pp.PlotFig(texttex=True, kind='pdf', **kwargs) as plot:
        for id in ids:
            label = get_tests(id=id, part='legend')[0]
            ext_timestamps, deltas = get(id)
            plot.axe.hist(deltas, bins, normed=1, histtype='step', alpha=0.9,
                          label=label)
        if kwargs.keys():
            plt.title = 'Tijdtest ' + kwargs[kwargs.keys()[0]]
        plt.xlabel(r'$\Delta$ t (swap - reference) [ns]')
        plt.ylabel(r'p')
        plt.xlim(-200, 200)
        plt.ylim(0.0, 0.15)

        #Save Figure
        plot.path = paths('tt_plot') + 'delta_histogram_alltests/'
        if len(ids) == 1:
            plot.name = 'tt_delta_hist_%03d' % ids[0]
        elif kwargs.keys():
            plot.name = 'tt_delta_hist_' + kwargs[kwargs.keys()[0]]
        plot.ltit = 'Tests'

    print 'tt_analyse: Plotted histogram'


def plot_ns_histogram(ids, **kwargs):
    """ Plot a histogram of the nanosecond part of the ext_timestamps

    """
    if type(ids) is int:
        ids = [ids]

    #Define Bins
    low = 0
    high = long(1e9)
    bin_size = 1e6  # 1e7 = 10ms, 1e6 = 1 ms, 1e3 = 1 us
    bins = np.arange(low, high + bin_size, bin_size)

    #Begin Figure
    with pp.PlotFig(texttex=False, kind='pdf', **kwargs) as plot:
        for id in ids:
            ext_timestamps, deltas = get(id)
            nanoseconds = nanoseconds_from_ext_timestamp(ext_timestamps[:40])
            plot.axe.hist(nanoseconds, bins, normed=1, histtype='step',
                          alpha=0.9, label=get_tests(id=id, part='legend')[0])
        if kwargs.keys():
            plt.title = 'Tijdtest ' + kwargs[kwargs.keys()[0]]
        plt.xlabel(r'nanosecond part of timestamp [ns]')
        plt.ylabel(r'p')
        plt.xlim(0, 1e9)
#         plt.ylim(.95e-9, 1.05e-9)

        #Save Figure
        plot.path = paths('tt_plot') + 'nanos_histogram/'
        if len(ids) == 1:
            plot.name = 'tt_nanos_hist_%03d' % ids[0]
        elif kwargs.keys():
            plot.name = 'tt_nanos_hist_' + kwargs[kwargs.keys()[0]]
        plot.ltit = 'Tests'

    print 'tt_analyse: Plotted histogram'


def plot_delta_time(ids, **kwargs):
    """ Plot delta versus the timestamps

    """
    if type(ids) is int:
        ids = [ids]

    #Begin Figure
    with pp.PlotFig(texttex=True, kind='png', legend=False,
                    legendtitle='Tests') as plot:
        colors = plt.rcParams['axes.color_cycle']
        for index, id in enumerate(ids):
            ext_timestamps, deltas = get(id)
            daystamps = (np.array(ext_timestamps) - min(ext_timestamps)) / 864e11
            plot.axe.scatter(daystamps, deltas,
                             c=colors[index % len(colors)],
                             marker='.', s=1, edgecolors='none', alpha=1,
                             label=get_tests(id=id, part='legend')[0])
        if kwargs.keys():
            plt.title = 'tt_delta_time_' + kwargs[kwargs.keys()[0]]
        plt.xlabel(r'Time in test [days]')
        plt.ylabel(r'$\Delta$ t (swap - reference) [ns]')
        plt.xlim(0, max(daystamps))
        plt.ylim(-175, 175)
#        print (plot.axe.transData.transform([(0, 1)]) -
#               plot.axe.transData.transform((0, 0)))

        #Save Figure
        plot.path = paths('tt_plot') + 'delta_time_alltests/'
        if len(ids) == 1:
            plot.name = 'tt_delta_time_%03d' % ids[0]
        elif kwargs.keys():
            plot.name = 'tt_delta_time_' + kwargs[kwargs.keys()[0]]

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

    groups = get_tests(part='id', subset='ALL')
    for group in groups:
        plot_ns_histogram(group)
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
