"""
Check for significant pulses in the pre-coincidence window

This can indicate pulses that are in the post coincidence of another
event, or simply not close enough to other pulses for a trigger.

This only works for stations with data reduction disabled. Because only
then do you know for certain which regions of the trace you are looking
at.

"""
import tables

from numpy import arange

from artist import Plot

from sapphire import Station

COLORS = ['black', 'red!80!black', 'green!80!black', 'blue!80!black']


def plot_traces(event, station):
    s = Station(station)
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
    plot.set_ylimits(min=150, max=500)  # max=2 ** 12
    plot.draw_horizontal_line(253, linestyle='gray')
    plot.draw_horizontal_line(323, linestyle='gray')
    plot.draw_horizontal_line(event['baseline'][0] + 20, linestyle='thin,gray')
    plot.draw_horizontal_line(event['baseline'][1] + 20, linestyle='thin,red!40!black')
    plot.draw_horizontal_line(event['baseline'][2] + 20, linestyle='thin,green!40!black')
    plot.draw_horizontal_line(event['baseline'][3] + 20, linestyle='thin,blue!40!black')
    plot.save_as_pdf('traces_%d_%d' % (station, event['ext_timestamp']))


if __name__ == "__main__":
    with tables.open_file('/Users/arne/Datastore/esd/2015/4/2015_4_27.h5', 'r') as data:
        station = 501
        events = data.get_node('/hisparc/cluster_amsterdam/station_%d' % station, 'events')
        query = ' | '.join(['((t%d > 0) & (t%d < 900))' % (i, i) for i in range(1, 5)])
        pre_events = events.read_where(query)
        print len(pre_events)
        for event in pre_events:
            plot_traces(event, station)

        t_trigger_events = pre_events.read_where('(t_trigger != -999_ & (t_trigger < 1000)')
        t_trigger_events.sort(order='t_trigger')
        print len(t_trigger_events)
        for event in t_trigger_events:
            plot_traces(event, station)
