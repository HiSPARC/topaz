from itertools import chain

from numpy import arange, around, mean, nan, nanmax, nanmin, sign

from artist import Plot

from sapphire import Station

COLORS = ['black', 'red', 'green', 'blue']
FILTER_THRESHOLD = 25


def get_traces():
    station = Station(502)
    raw_traces = station.event_trace(1385942677, 963603990, raw=True)
    return raw_traces


def filter_traces(raw_traces, use_threshold=True, threshold=FILTER_THRESHOLD):
    """Apply the mean filter to multiple traces"""

    return [filter_trace(raw_trace, use_threshold, threshold) for raw_trace in raw_traces]


def filter_trace(raw_trace, use_threshold=True, threshold=FILTER_THRESHOLD):
    """Apply the mean filter to a single trace

    First separate the even and odd ADC traces, filter each separately.
    Then recombine them and pass the entire trace through the filter.

    """
    even_trace = raw_trace[::2]
    odd_trace = raw_trace[1::2]

    filtered_even = mean_filter(even_trace, use_threshold, threshold)
    filtered_odd = mean_filter(odd_trace, use_threshold, threshold)

    recombined_trace = [v for eo in zip(filtered_even, filtered_odd) for v in eo]
    filtered_trace = mean_filter(recombined_trace, use_threshold, threshold)
    return filtered_trace


def mean_filter(trace, use_threshold=True, threshold=FILTER_THRESHOLD):
    """Apply either the filter with or without the threshold"""

    if use_threshold:
        return mean_filter_with_threshold(trace)
    else:
        return mean_filter_without_threshold(trace)


def mean_filter_with_threshold(trace, threshold=FILTER_THRESHOLD):
    """The mean filter in case use_threshold is True

    Verified with the LabView VI and Bachelor thesis Oostenbrugge2014.

    """
    filtered_trace = []
    local_mean = mean(trace[:4])

    if all([abs(v - local_mean) <= threshold for v in trace[:4]]):
        filtered_trace.extend([int(around(local_mean))] * 4)
    else:
        filtered_trace.extend(trace[:4])

    for i in range(4, len(trace)):
        if abs(trace[i] - trace[i - 1]) > 2 * threshold:
            filtered_trace.append(trace[i])
        elif sign(trace[i] - local_mean) == sign(trace[i - 1] - local_mean):
            # Both values on same side of the local_mean
            filtered_trace.append(trace[i])
        elif abs(trace[i] - local_mean) > threshold:
            filtered_trace.append(trace[i])
        else:
            filtered_trace.append(int(around(local_mean)))

    return filtered_trace


def mean_filter_without_threshold(trace):
    """The mean filter in case use_threshold is False

    Verified with the LabView VI and Bachelor thesis Oostenbrugge2014.

    """
    local_mean = mean(trace[:4])
    filtered_trace = [int(around(local_mean))] * 4

    for i in range(4, len(trace)):
        local_mean = mean(trace[i - 4 : i])
        if sign(trace[i] - local_mean) == sign(trace[i - 1] - local_mean):
            # Both values on same side of the local_mean
            filtered_trace.append(trace[i])
        else:
            filtered_trace.append(int(around(local_mean)))
    return filtered_trace


def plot_raw(raw_traces):
    length = 2.5 * len(raw_traces[0])
    plot = Plot()
    max_signal = max(chain.from_iterable(raw_traces))
    plot.add_pin_at_xy(500, max_signal, 'pre-trigger', location='above', use_arrow=False)
    plot.draw_vertical_line(1000, 'gray')
    plot.add_pin_at_xy(1750, max_signal, 'trigger', location='above', use_arrow=False)
    plot.draw_vertical_line(2500, 'gray')
    plot.add_pin_at_xy(4250, max_signal, 'post-trigger', location='above', use_arrow=False)

    for i, raw_trace in enumerate(raw_traces):
        plot.plot(arange(0, length, 2.5), raw_trace, mark=None, linestyle=COLORS[i])

    plot.set_ylimits(min=0)
    plot.set_xlimits(min=0, max=length)
    plot.set_ylabel(r'Signal strength [ADC counts]')
    plot.set_xlabel(r'Sample [\si{\nano\second}]')
    plot.save_as_pdf('raw')


def zoom_baseline(raw_traces):
    plot = Plot()
    length = 500  # ns

    #     for i, raw_trace in enumerate(raw_traces):
    #         plot.plot(arange(0, length, 2.5), raw_trace[:int(length / 2.5)], mark=None, linestyle=COLORS[i])

    #     plot.plot(arange(0, length, 2.5), raw_traces[0][:int(length / 2.5)], mark=None, linestyle=COLORS[0])

    plot.plot(arange(0, length, 5), raw_traces[0][: int(length / 2.5) : 2], mark=None, linestyle=COLORS[0])
    plot.plot(arange(2.5, length, 5), raw_traces[0][1 : int(length / 2.5) : 2], mark=None, linestyle=COLORS[1])

    plot.set_ylimits(min=180, max=220)
    plot.set_xlimits(min=0, max=length)
    plot.set_ylabel(r'Signal strength [ADC counts]')
    plot.set_xlabel(r'Sample [\si{\nano\second}]')
    plot.save_as_pdf('baseline')


def zoom_pulse(raw_traces):
    plot = Plot()
    start, end = get_outer_limits(raw_traces, 253)

    for i, raw_trace in enumerate(raw_traces):
        plot.plot(arange(start * 2.5, end * 2.5, 2.5), raw_trace[start:end], mark=None, linestyle=COLORS[i])

    hisparc_version = 2

    if hisparc_version == 3:
        low = 81
        high = 150
    elif hisparc_version == 2:
        low = 253
        high = 323

    plot.draw_horizontal_line(low, 'gray')
    plot.add_pin_at_xy(start * 2.5, low, 'low', location='above right', use_arrow=False)
    plot.draw_horizontal_line(high, 'gray')
    plot.add_pin_at_xy(start * 2.5, high, 'high', location='above right', use_arrow=False)

    plot.set_ylimits(min=0)
    plot.set_xlimits(min=start * 2.5, max=end * 2.5 - 2.5)
    plot.set_ylabel(r'Signal strength [ADC counts]')
    plot.set_xlabel(r'Sample [\si{\nano\second}]')
    plot.save_as_pdf('pulse')


def get_outer_limits(traces, threshold, padding=25):
    starts, ends = list(zip(*[get_limits(trace, threshold) for trace in traces]))
    start = max(0, nanmin(starts) - padding)
    end = min(len(traces[0]), nanmax(ends) + padding)
    return start, end


def get_limits(trace, threshold):
    start = first_above_threshold(trace, threshold)
    end = first_above_threshold(trace[::-1], threshold)
    return start, len(trace) - end


def first_above_threshold(trace, threshold):
    return next((i for i, x in enumerate(trace) if x >= threshold), nan)


if __name__ == "__main__":
    raw_traces = get_traces()
    #    plot_raw(raw_traces)
    zoom_baseline(raw_traces)
    zoom_pulse(raw_traces)
#     filtered_traces = filter_traces(raw_traces)
