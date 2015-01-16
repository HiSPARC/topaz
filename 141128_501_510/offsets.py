import itertools

from numpy import nan, isnan, arange, histogram, linspace
from scipy.optimize import curve_fit
import tables

from sapphire.analysis.coincidence_queries import CoincidenceQuery
from sapphire.utils import pbar, gauss, ERR
from artist import Plot


COLORS = ['black', 'teal', 'orange', 'purple', 'cyan', 'green', 'blue', 'red',
          'gray']


def determine_detector_timing_offsets(d, s, events):
    """Determine the offsets between the station detectors.

    ADL: Currently assumes detector 1 is a good reference.
    But this is not always the best choice. Perhaps it should be
    determined using more data (more than one day) to be more
    accurate.

    """
    bins = arange(-100 + 1.25, 100, 2.5)
    col = (cl for cl in COLORS)
    graph = Plot()
    for i, j in itertools.combinations(range(1, 5), 2):
        ti = events.col('t%d' % i)
        tj = events.col('t%d' % j)
        dt = (ti - tj).compress((ti >= 0) & (tj >= 0))
        y, bins = histogram(dt, bins=bins)
        graph.histogram(y, bins, linestyle='color=%s' % col.next())
        x = (bins[:-1] + bins[1:]) / 2
        try:
            popt, pcov = curve_fit(gauss, x, y, p0=(len(dt), 0., 10.))
            print '%d-%d: %f (%f)' % (i, j, popt[1], popt[2])
        except (IndexError, RuntimeError):
            print '%d-%d: failed' % (i, j)
    graph.set_title('Time difference, station %d' % (s))
    graph.set_label('%s' % d.replace('_', ' '))
    graph.set_xlimits(-100, 100)
    graph.set_ylimits(min=0)
    graph.set_xlabel('$\Delta t$')
    graph.set_ylabel('Counts')
    graph.save_as_pdf('%s_%d' % (d, s))



def determine_detector_timing_offsets2(events):

    bins = arange(-100 + 1.25, 100, 2.5)
    offsets = [0., 0., 0., 0.]
    ti = events.col('t1')
    for j in [1, 3, 4]:
        tj = events.col('t%d' % j)
        dt = (ti - tj).compress((ti >= 0) & (tj >= 0))
        y, bins = histogram(dt, bins=bins)
        x = (bins[:-1] + bins[1:]) / 2
        try:
            popt, pcov = curve_fit(gauss, x, y, p0=(len(dt), 0., 10.))
            offsets[j] = popt[1]
        except (IndexError, RuntimeError):
            pass

    return offsets


def determine_station_timing_offsets(d, data):
    # First determine detector offsets for each station
    offsets = {}
    for s in [501, 510]:
        station_group = data.get_node('/hisparc/cluster_amsterdam/station_%d' % s)
        offsets[s] = determine_detector_timing_offsets2(station_group.events)

    ref_station = 501
    ref_d_off = offsets[ref_station]

    station = 510

    cq = CoincidenceQuery(data, '/coincidences')
    dt = []
    d_off = offsets[station]
    stations = [ref_station, station]
    coincidences = cq.all(stations)
    c_events = cq.events_from_stations(coincidences, stations)
    for events in c_events:
        # Filter for possibility of same station twice in coincidence
        if len(events) is not 2:
            continue
        if events[0][0] == ref_station:
            ref_event = events[0][1]
            event = events[1][1]
        else:
            ref_event = events[1][1]
            event = events[0][1]

        try:
            ref_t = min([ref_event['t%d' % (i + 1)] - ref_d_off[i]
                         for i in range(4)
                         if ref_event['t%d' % (i + 1)] not in ERR])
            t = min([event['t%d' % (i + 1)] - d_off[i]
                     for i in range(4)
                     if event['t%d' % (i + 1)] not in ERR])
        except ValueError:
            continue
        if (ref_event['t_trigger'] in ERR or event['t_trigger'] in ERR):
            continue
        dt.append((int(event['ext_timestamp']) -
                   int(ref_event['ext_timestamp'])) -
                  (event['t_trigger'] - ref_event['t_trigger']) +
                  (t - ref_t))

    bins = linspace(-150, 150, 200)
    y, bins = histogram(dt, bins=bins)
    x = (bins[:-1] + bins[1:]) / 2
    try:
        popt, pcov = curve_fit(gauss, x, y, p0=(len(dt), 0., 50))
        station_offset = popt[1]
    except RuntimeError:
        station_offset = 0.
    offsets[station] = [detector_offset + station_offset
                        for detector_offset in offsets[station]]
    print 'Station 501 - 510: %f (%f)' % (popt[1], popt[2])
    graph = Plot()
    graph.histogram(y, bins)
    graph.set_title('Time difference, between station 501-510')
    graph.set_label('%s' % d.replace('_', ' '))
    graph.set_xlimits(-150, 150)
    graph.set_ylimits(min=0)
    graph.set_xlabel('$\Delta t$')
    graph.set_ylabel('Counts')
    graph.save_as_pdf('%s' % d)


if __name__ == '__main__':
    for d in ['e_501_510_141001_141011', 'e_501_510_141101_141111']:
        print d
        with tables.open_file(d + '.h5', 'r') as data:
            for s in [501, 510]:
                print 'Station: %d' % s
                e = data.get_node('/s%d/events' % s)
                determine_detector_timing_offsets(d, s, e)

#     for d in ['c_501_510_141001_141011', 'c_501_510_141101_141111']:
#         print d
#         with tables.open_file(d + '.h5', 'r') as data:
#             determine_station_timing_offsets(d, data)
