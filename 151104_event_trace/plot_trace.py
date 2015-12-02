"""Get/plot event trace

Call plot_trace with the station number of the station and the timestamp and
nanoseconds of the event for which you want the trace.

For example::

    ./plot_trace 501 1362960030 490443679

The script will retrieve the traces for the event and plot them using artist.

"""

import argparse

from numpy import arange
from artist import Plot

from sapphire import Station


def get_traces(station_number, ts, ns, raw=False):
    """Retrieve the traces

    :param station_number: number of the station to which the event belongs.
    :param ts: timestamp of the event in seconds.
    :param ns: subsecond part of the extended timestamp in nanoseconds.
    :return: the traces.

    """
    traces = Station(station_number).event_trace(ts, ns, raw)
    return traces


def plot_traces(traces, label='', raw=False):
    """Plot traces

    :param traces: list of lists of trace values.
    :param label: name (suffix) for the output pdf.

    """
    colors = ['black', 'red', 'black!40!green', 'blue']
    plot = Plot(width=r'1.\textwidth')
    times = arange(0, len(traces[0]) * 2.5, 2.5)
    for i, trace in enumerate(traces):
        if not raw:
            trace = [t * -0.57 / 1e3 for t in trace]
        plot.plot(times, trace, linestyle='%s, thin' % colors[i], mark=None)
    if len(traces[0]) == 2400 and raw:
        plot.add_pin_at_xy(500, 10, 'pre-trigger', location='below', use_arrow=False)
        plot.add_pin_at_xy(1750, 10, 'trigger', location='below', use_arrow=False)
        plot.add_pin_at_xy(4250, 10, 'post-trigger', location='below', use_arrow=False)
        plot.draw_vertical_line(1000, 'gray')
        plot.draw_vertical_line(2500, 'gray')
    if raw:
        plot.set_ylabel(r'Signal strength [ADCcounts]')
    else:
        plot.set_ylabel(r'Signal strength [\si{\volt}]')
    plot.set_xlabel(r'Event time [\si{\ns}]')
    plot.set_xlimits(0, times[-1])
    plot.set_axis_options('line join=round')
    plot.save_as_pdf('trace_' + label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('number', type=int, help="Station number")
    parser.add_argument('timestamp', type=int, help="Timestamp of the event")
    parser.add_argument('nanoseconds', type=int, help="Nanosecond part of the timestamp")
    parser.add_argument('--raw', action='store_true', help="Get raw trace values")
    args = parser.parse_args()

    label = '%d_%d_%d' % (args.number, args.timestamp, args.nanoseconds)
    traces = get_traces(args.number, args.timestamp, args.nanoseconds, args.raw)
    plot_traces(traces, label, args.raw)


if __name__ == "__main__":
    station_number = 501
    ts = 1362960030
    ns = 490443679
    traces = get_traces(station_number, ts, ns)
    plot_traces(traces)
