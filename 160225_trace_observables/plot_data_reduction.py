from numpy import array, arange

from artist import Plot

from sapphire import Station
from sapphire.analysis.process_traces import DataReduction

COLORS = ['black', 'red', 'black!40!green', 'blue']


def main(ts, ns):
    station = Station(501)
    traces = station.event_trace(ts, ns, True)

    dr = DataReduction()
    reduced_traces, o = dr.reduce_traces(array(traces).T, return_offset=True)
    reduced_traces = reduced_traces.T
    plot = Plot()

    t = arange(len(traces[0])) * 2.5
    for i, trace in enumerate(traces):
        plot.plot(t, trace, linestyle='%s, thin' % COLORS[i], mark=None)
    plot.draw_vertical_line(o * 2.5, 'gray')
    plot.draw_vertical_line((o + len(reduced_traces[0])) * 2.5, 'gray')

    plot.set_axis_options('line join=round')
    plot.set_xlabel(r'Event time [\si{\ns}]')
    plot.set_ylabel(r'Signal strength [ADCcounts]')
    plot.set_xlimits(t[0], t[-1])

    plot.save_as_pdf('raw_traces_%d_%d' % (ts, ns))

    t = arange(o, o + len(reduced_traces[0])) * 2.5
    for i, trace in enumerate(reduced_traces):
        plot.plot(t, trace, linestyle='%s, thin' % COLORS[i], mark=None)
    plot.set_axis_options('line join=round')
    plot.set_xlabel(r'Event time [\si{\ns}]')
    plot.set_ylabel(r'Signal strength [ADCcounts]')
    plot.set_xlimits(t[0], t[-1])

    plot.save_as_pdf('reduced_traces_%d_%d' % (ts, ns))


if __name__ == "__main__":
    main(1469404810, 874168930)
    main(1432377853, 301187731)
