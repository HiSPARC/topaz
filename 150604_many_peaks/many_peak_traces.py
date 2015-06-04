import tables
from numpy import any, arange, histogram
from sapphire.api import Station
from artist import Plot

COLORS = ['black', 'red!80!black', 'green!80!black', 'blue!80!black']


def plot_n_peaks_histogram(events, station):
    plot = Plot('semilogy')
    counts, bins = histogram(events.col('n_peaks').ravel(), bins=range(100))
    plot.histogram(counts, bins)
    plot.set_ylimits(min=0.5)
    plot.set_xlimits(min=0, max=100)
    plot.save_as_pdf('n_peaks_%d' % station)


def plot_traces_with_many_peaks(events, station, min_peaks=10):
    filter = any(events.col('n_peaks') > min_peaks, axis=1)
    neve = events.read_coordinates(filter)
    s = Station(station)
    for event in neve:
        plot = Plot()
        traces = s.event_trace(event['timestamp'], event['nanoseconds'], raw=True)
        for j, trace in enumerate(traces):
            t = arange(0, (2.5 * len(traces[0])), 2.5)
            plot.plot(t, trace, mark=None, linestyle=COLORS[j])
        n_peaks = event['n_peaks']
        plot.set_title('%d - %d' % (station, event['ext_timestamp']))
        plot.set_label('%d ' * 4 % tuple(n_peak for n_peak in n_peaks))
        plot.set_xlabel('t [\si{n\second}]')
        plot.set_ylabel('Signal strength')
        plot.set_xlimits(min=0, max=2.5 * len(traces[0]))
        plot.set_ylimits(min=0, max=2 ** 12)
        plot.draw_horizontal_line(253, linestyle='gray')
        plot.draw_horizontal_line(323, linestyle='gray')
        plot.save_as_pdf('traces_%d_%d' % (station, event['ext_timestamp']))


if __name__ == "__main__":
    with tables.open_file('/Users/arne/Datastore/esd/2015/4/2015_4_27.h5', 'r') as data:
        station = 504
        events = data.get_node('/hisparc/cluster_amsterdam/station_%d' % station,
                               'events')
        plot_n_peaks_histogram(events)
        plot_traces_with_many_peaks(events, station)
