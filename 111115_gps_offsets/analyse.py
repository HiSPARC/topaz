import numpy as np
from artist import Plot
from scipy.optimize import curve_fit

from sapphire.utils import gauss

from testlist import get_tests
from delta import get
from helper import (nanoseconds_from_ext_timestamp,
                    timestamps_from_ext_timestamp)


PLOT_PATH = '/Users/arne/Dropbox/hisparc/Projects/tijdtest/plots/'


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
    bin_size = 1
    bins = np.arange(low - .5 * bin_size, high + bin_size, bin_size)

    #Begin Figure
    plot = Plot()
    for id in ids:
        ext_timestamps, deltas = get(id)
        n, bins = np.histogram(deltas, bins, normed=1)
        plot.histogram(n, bins)
    if kwargs.keys():
        plot.set_title('Tijdtest ' + kwargs[kwargs.keys()[0]])
    plot.set_xlabel(r'$\Delta$ t (swap - reference) [ns]')
    plot.set_ylabel(r'p')
    plot.set_xlimits(low, high)
    plot.set_ylimits(0., .15)

    #Save Figure
    if len(ids) == 1:
        name = 'tt_delta_hist_%03d' % ids[0]
    elif kwargs.keys():
        name = 'tt_delta_hist_' + kwargs[kwargs.keys()[0]]

    plot.save_as_pdf(PLOT_PATH + name)
    print 'tt_analyse: Plotted histogram'


def plot_delta_histogram(ids, **kwargs):
    """ Plot a histogram of the deltas

    """
    if type(ids) is int:
        ids = [ids]

    # Bin width
    bin_size = 1  # 2.5*n

    # Begin Figure
    plot = Plot()
    for id in ids:
        ext_timestamps, deltas = get(id)
        low = floor(min(deltas))
        high = ceil(max(deltas))
        bins = np.arange(low - .5 * bin_size, high + bin_size, bin_size)
        n, bins = np.histogram(deltas, bins)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        popt, pcov = curve_fit(gauss, bin_centers, n, p0=[.15, np.mean(deltas), np.std(deltas)])
        plot.histogram(n, bins)
        plot.plot(bin_centers, gauss(bin_centers, *popt), mark=None, linestyle='gray')
    if kwargs.keys():
        plot.set_title('Tijdtest ' + kwargs[kwargs.keys()[0]])
    plot.set_label(r'$\mu={1:.1f}$, $\sigma={2:.1f}$'.format(*popt))
    plot.set_xlabel(r'Time difference [ns]')
    plot.set_ylabel(r'Counts')
    plot.set_xlimits(low, high)
    plot.set_ylimits(min=0.)

    #Save Figure
    if len(ids) == 1:
        name = 'delta_histogram/tt_delta_hist_%03d' % ids[0]
    elif kwargs.keys():
        name = 'delta_histogram/tt_delta_hist_' + kwargs[kwargs.keys()[0]]
    plot.save_as_pdf(PLOT_PATH + name)

    print 'tt_analyse: Plotted histogram'


def plot_ns_histogram(ids, **kwargs):
    """ Plot a histogram of the nanosecond part of the ext_timestamps

    """
    if type(ids) is int:
        ids = [ids]

    #Define Bins
    low = 0
    high = int(1e9)
    bin_size = 5e6  # 1e7 = 10ms, 1e6 = 1 ms, 1e3 = 1 us
    bins = np.arange(low, high + bin_size, bin_size)

    #Begin Figure
    plot = Plot()
    for id in ids:
        ext_timestamps, deltas = get(id)
        nanoseconds = nanoseconds_from_ext_timestamp(ext_timestamps)
        n, bins = np.histogram(nanoseconds, bins, normed=1)
        plot.histogram(n, bins)

    if kwargs.keys():
        plot.set_title('Tijdtest ' + kwargs[kwargs.keys()[0]])
    plot.set_xlabel(r'nanosecond part of timestamp [ns]')
    plot.set_ylabel(r'p')
    plot.set_xlimits(0, 1e9)
    plot.set_ylimits(.95e-9, 1.05e-9)

    #Save Figure
    if len(ids) == 1:
        name = 'nanoseconds_histogram/tt_nanos_hist_%03d' % ids[0]
    elif kwargs.keys():
        name = 'nanoseconds_histogram/tt_nanos_hist_' + kwargs[kwargs.keys()[0]]
    try:
        plot.save_as_pdf(PLOT_PATH + name)
    except:
        print 'tt_analyse: Failed ns hist for %s' % str(ids)

    print 'tt_analyse: Plotted histogram'


def plot_delta_time(ids, **kwargs):
    """ Plot delta versus the timestamps

    """
    if type(ids) is int:
        ids = [ids]

    #Begin Figure
    plot = Plot()
    for index, id in enumerate(ids):
        ext_timestamps, deltas = get(id)
        daystamps = (np.array(ext_timestamps) - min(ext_timestamps)) / 864e11
        plot.scatter(daystamps[::250], deltas[::250], mark='*',
                     markstyle="mark size=.1pt")
    if kwargs.keys():
        plot.set_title('Tijdtest delta time' + kwargs[kwargs.keys()[0]])
    plot.set_xlabel(r'Time in test [days]')
    plot.set_ylabel(r'$\Delta$ t (swap - reference) [ns]')
    plot.set_xlimits(0, max(daystamps))
    plot.set_ylimits(-175, 175)

    #Save Figure
    if len(ids) == 1:
        name = 'delta_time/tt_delta_time_%03d' % ids[0]
    elif kwargs.keys():
        name = 'delta_time/tt_delta_time_' + kwargs[kwargs.keys()[0]]
    plot.save_as_pdf(PLOT_PATH + name)

    print 'tt_analyse: Plotted delta vs time'


def determine_stats(deltas):
    if len(deltas):
        low = min(deltas)
        high = max(deltas)
        avg = np.average(deltas)
        std = np.std(deltas)
        return low, high, avg, std
    else:
        return 0, 0, 0, 0

def plot_box(ids, **kwargs):
    """Box Plot like results"""

    if type(ids) is int:
        ids = [ids]

    #Begin Figure
    plot = Plot()
    data = [determine_stats([x for x in get(id)[1] if abs(x) < 100]) for id in ids]

    low, high, avg, std = zip(*data)

    plot.plot(ids, avg, yerr=std, mark='o', markstyle="mark size=1pt",
              linestyle=None)
    plot.scatter(ids, low, mark='x', markstyle="mark size=.5pt")
    plot.scatter(ids, high, mark='x', markstyle="mark size=.5pt")

    if kwargs.keys():
        plot.set_title('Tijdtest offsets ' + kwargs[kwargs.keys()[0]])
    plot.set_xlabel(r'ids')
    plot.set_ylabel(r'$\Delta$ t (swap - reference) [\si{\nano\second}]')
    plot.set_ylimits(-100, 100)

    #Save Figure
    if len(ids) == 1:
        name = 'box/tt_offset_%03d' % ids[0]
    elif kwargs.keys():
        name = 'box/tt_offset_' + kwargs[kwargs.keys()[0]]
    plot.save_as_pdf(PLOT_PATH + name)

    print 'tt_analyse: Plotted offsets'


def plot_offset_distribution(ids, **kwargs):
    """Offset distribution"""

    #Begin Figure
    plot = Plot()
    offsets = [np.average([x for x in get(id)[1] if abs(x) < 100]) for id in ids]
    bins = np.arange(-70, 70, 2)
    n, bins = np.histogram(offsets, bins)
    plot.histogram(n, bins)

    bin_centers = (bins[:-1] + bins[1:]) / 2
    popt, pcov = curve_fit(gauss, bin_centers, n, p0=[1., np.mean(offsets), np.std(offsets)])
    plot.plot(bin_centers, gauss(bin_centers, *popt), mark=None, linestyle='gray')

    if kwargs.keys():
        plot.set_title('Tijdtest offset distribution ' + kwargs[kwargs.keys()[0]])
    plot.set_label(r'$\mu={1:.1f}$, $\sigma={2:.1f}$'.format(*popt))
    plot.set_xlabel(r'Offset [\si{\nano\second}]')
    plot.set_ylabel(r'Counts')
    plot.set_ylimits(min=0)

    #Save Figure
    name = 'box/tt_offset_distribution'
    if kwargs.keys():
        name += kwargs[kwargs.keys()[0]]
    plot.save_as_pdf(PLOT_PATH + name)

    print 'tt_analyse: Plotted offsets'



if __name__ == '__main__':
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

    ids = get_tests(part='id', subset='Good1')
    plot_box(ids, name='Good1')
    plot_offset_distribution(ids, name='Good1')
    ids = get_tests(part='id', subset='Good2')
    plot_box(ids, name='Good2')
    plot_offset_distribution(ids, name='Good2')
    ids = get_tests(part='id', subset='PMT')
    plot_box(ids, name='PMT')
    plot_offset_distribution(ids, name='PMT')

#     plot_delta_time(62)
#     print_delta_results()

#     for id in ids:
#         plot_ns_histogram(id)
#         plot_delta_histogram([id])
#         plot_delta_time([id])

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
