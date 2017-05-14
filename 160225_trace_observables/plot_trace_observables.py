from numpy import arange, array, where

from artist import Plot

from sapphire import Station
from sapphire.analysis.process_traces import BASELINE_THRESHOLD, MeanFilter, TraceObservables


def get_trace(s):
    d_id = 0
    traces = s.event_trace(1441065624, 686526755, raw=False)
    raw_traces = s.event_trace(1441065624, 686526755, raw=True)
    baselines = [t[0] - ft[0] for t, ft in zip(raw_traces, traces)]
    to = TraceObservables(array(raw_traces).T)
    to.baselines = baselines
    integrals = to.integrals
    pulseheights = to.pulseheights
    filter = MeanFilter()
    filtered_traces = filter.filter_traces(raw_traces)
    return (array(raw_traces[d_id]), baselines[d_id], integrals[d_id],
            pulseheights[d_id], array(filtered_traces[d_id]))


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

#     plot.set_ylimits(0)
    plot.set_xlabel(r'Trace time [\si{\ns}]')
    plot.set_ylabel(r'Signal strength [ADC]')
    plot.save_as_pdf('integral')


def plot_filtered(filtered_trace):
    plot = Plot()

    time = arange(0, len(filtered_trace) * 2.5, 2.5)
    plot.plot(time, filtered_trace, mark=None, linestyle='const plot')

    plot.set_xlabel(r'Trace time [\si{\ns}]')
    plot.set_ylabel(r'Signal strength [ADC]')
    plot.save_as_pdf('mean_filter')


if __name__ == "__main__":
    if 'trace' not in globals():
        s = Station(510)
    plot_integral(trace, baseline)
    trace, baseline, integral, pulseheight, filtered_trace = get_trace(s)
    plot_filtered(filtered_trace)
    print '%d ADC, %d ADC.sample, %d ADC' % (baseline, integral, pulseheight)
