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


def get_traces(station_number, ts, ns):
    """Retrieve the traces

    :param station_number: number of the station to which the event belongs.
    :param ts: timestamp of the event in seconds.
    :param ns: subsecond part of the extended timestamp in nanoseconds.
    :return: the traces.

    """
    traces = Station(station_number).event_trace(ts, ns, raw=False)
    return traces


def plot_traces(traces, label=''):
    """Plot traces

    :param traces: list of lists of trace values.
    :param label: name (suffix) for the output pdf.

    """
    colors = ['black', 'red', 'black!40!green', 'blue']
    plot = Plot(width=r'.5\textwidth')
    times = arange(0, len(traces[0]) * 2.5, 2.5)
    for i, trace in enumerate(traces):
        plot.plot(times, [t * -0.57 / 1e3 for t in trace],
                  linestyle='%s, thick' % colors[i], mark=None)
    plot.set_xlimits(0, times[-1])
    plot.set_ylabel(r'Signal strength [V]')
    plot.set_xlabel(r'Event time [\si{\ns}]')
    plot.set_axis_options('line join=round')
    plot.save_as_pdf('trace_' + label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('number', type=int, help="Station number")
    parser.add_argument('timestamp', type=int, help="Timestamp of the event")
    parser.add_argument('nanoseconds', type=int, help="Nanosecond part of the timestamp")
    args = parser.parse_args()

    label = '%d_%d_%d' % (args.number, args.timestamp, args.nanoseconds)
    traces = get_traces(args.number, args.timestamp, args.nanoseconds)
    plot_traces(traces, label)


if __name__ == "__main__":
    station_number = 501
    ts = 1362960030
    ns = 490443679
    traces = get_traces(station_number, ts, ns)
    plot_traces(traces)
