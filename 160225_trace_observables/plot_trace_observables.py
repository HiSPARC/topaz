from numpy import arange, where, zeros, array, nan

from artist import Plot

from sapphire import Station
from sapphire.analysis.process_traces import (BASELINE_THRESHOLD,
                                              TraceObservables)


def get_trace(s):
    d_id = 0
    traces = s.event_trace(1441065624, 686526755, raw=True)
    filtered_traces = s.event_trace(1441065624, 686526755, raw=False)
    baselines = [t[0] - ft[0] for t, ft in zip(traces, filtered_traces)]
    to = TraceObservables(array(traces).T)
    to.baselines = baselines
    integrals = to.integrals
    pulseheights = to.pulseheights
    return (array(traces[d_id]), baselines[d_id], integrals[d_id],
            pulseheights[d_id])


def plot_integral(trace, baseline):
    plot = Plot()

    time = arange(0, len(trace) * 2.5, 2.5)
    plot.plot(time, trace, mark=None, linestyle='const plot')
    integral_trace = where(trace > baseline + BASELINE_THRESHOLD, trace, baseline)
    plot.shade_region(time + 2.5, [baseline] * len(trace), integral_trace,
                      color='lightgray, const plot')

    plot.draw_horizontal_line(baseline, linestyle='densely dashed, gray')
    plot.draw_horizontal_line(baseline + BASELINE_THRESHOLD,
                              linestyle='densely dotted, gray')
    plot.draw_horizontal_line(max(trace), linestyle='densely dashed, gray')

    plot.set_ylimits(0)
    plot.set_xlabel(r'Trace time [\si{\ns}]')
    plot.set_ylabel(r'Signal strength [ADC]')
    plot.save_as_pdf('integral')


if __name__ == "__main__":
    if 'trace' not in globals():
        s = Station(510)
        trace, baseline, integral, pulseheight = get_trace(s)
    plot_integral(trace, baseline)
    print '%d ADC, %d ADC.sample, %d ADC' % (baseline, integral, pulseheight)
