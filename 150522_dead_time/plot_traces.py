"""Plot multiple traces

This script is used to plot traces from multiple events which overlap.

"""

from numpy import arange, array

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


def plot_traces(traces1, traces2, overlap=0, label=''):
    """Plot traces

    :param traces: list of lists of trace values.
    :param label: name (suffix) for the output pdf.

    """
    colors1 = ['black', 'red', 'black!40!green', 'blue']
    colors2 = ['gray', 'black!40!red', 'black!60!green', 'black!40!blue']
    plot = Plot(width=r'1.\textwidth', height=r'.3\textwidth')

    times1 = arange(0, len(traces1[0]) * 2.5, 2.5)
    times2 = arange((len(traces1[0]) - overlap) * 2.5,
                    (len(traces1[0]) + len(traces2[0]) - overlap) * 2.5, 2.5)

    for i, trace in enumerate(traces1):
        plot.plot(times1, array(trace) + i * 20, linestyle='%s, ultra thin' % colors1[i], mark=None)
    plot.draw_vertical_line(1000, 'gray, very thin')
    plot.draw_vertical_line(2500, 'gray, very thin')
    plot.draw_vertical_line(6000, 'pink, dashed, very thin')
    plot.add_pin_at_xy(0, 450, r'\tiny{pre-trigger}', location='right', use_arrow=False)
    plot.add_pin_at_xy(1000, 450, r'\tiny{trigger}', location='right', use_arrow=False)
    plot.add_pin_at_xy(2500, 450, r'\tiny{post-trigger}', location='right', use_arrow=False)
    plot.add_pin_at_xy(6000, 450, r'\tiny{end of first event}', location='left', use_arrow=True)

    for i, trace in enumerate(traces2):
        plot.plot(times2, array(trace) + i * 20, linestyle='%s, ultra thin' % colors2[i], mark=None)
    plot.draw_vertical_line(6000 - (overlap * 2.5), 'pink, very thin')
    plot.draw_vertical_line(7000 - (overlap * 2.5), 'gray, very thin')
    plot.draw_vertical_line(8500 - (overlap * 2.5), 'gray, very thin')
    plot.add_pin_at_xy(6000 - (overlap * 2.5), 400, r'\tiny{pre-trigger}', location='right', use_arrow=False)
    plot.add_pin_at_xy(7000 - (overlap * 2.5), 400, r'\tiny{trigger}', location='right', use_arrow=False)
    plot.add_pin_at_xy(8500 - (overlap * 2.5), 400, r'\tiny{post-trigger}', location='right', use_arrow=False)

    plot.set_ylabel(r'Signal strength [ADCcounts]')
    plot.set_xlabel(r'Event time [\si{\ns}]')
    plot.set_ylimits(0, 500)
    plot.set_xlimits(0, times2[-1])
    plot.set_axis_options('line join=round')
    plot.save_as_pdf('trace_' + label)


if __name__ == "__main__":
    station_number = 501

    ts1 = 1432377853
    ns1 = 301187731
    ns1b = 301193386

    if 'traces1' not in globals():
        traces1 = get_traces(station_number, ts1, ns1, raw=True)
    if 'traces1b' not in globals():
        traces1b = get_traces(station_number, ts1, ns1b, raw=True)
    plot_traces(traces1, traces1b, overlap=700, label='501_1')

    ts2 = 1452149092
    ns2 = 363815846
    ns2b = 363820896

    if 'traces2' not in globals():
        traces2 = get_traces(station_number, ts2, ns2, raw=True)
    if 'traces2b' not in globals():
        traces2b = get_traces(station_number, ts2, ns2b, raw=True)
    plot_traces(traces2, traces2b, overlap=942, label='501_2')
