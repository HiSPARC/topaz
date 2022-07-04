import itertools

import tables

from numpy import arange, histogram
from scipy.optimize import curve_fit
from scipy.stats import norm, tukeylambda

from artist import Plot

PATH = '/Users/arne/Datastore/expected_dt/test_station_dt_spa.h5'


def tl(x, loc, scale):
    return tukeylambda.pdf(x, 0.27, loc, scale)


def plot_fits(plot, counts, bins):
    """Fit dt distribution and plot results"""

    colors = (c for c in ['gray', 'lightgray', 'blue', 'red'])
    x = (bins[:-1] + bins[1:]) / 2
    for fit_f, p0, offset_idx in [
        # (gauss, (sum(counts), 0., 30), 1),
        (norm.pdf, (0.0, 30.0), 0),
        # (t.pdf, (1., 0., 1.), 0),
        (tl, (0.0, 450.0), 0),
    ]:
        popt, pcov = curve_fit(fit_f, x, counts, p0=p0)
        plot.plot(x - popt[offset_idx], fit_f(x, *popt), mark=None, linestyle=next(colors))
        if fit_f == norm.pdf:
            plot.set_label(r'$\mu$: {:.2f}, $\sigma$: {:.2f}'.format(popt[0], popt[1]))
            offset = popt[0]
    return offset


def plot_offset_distributions():
    with tables.open_file(PATH, 'r') as data:
        station_groups = [data.get_node(sidx, 'events') for sidx in data.root.flat.coincidences.s_index]
        for ref_events, events in itertools.combinations(station_groups, 2):
            ref_s = ref_events._v_parent._v_name[8:]
            s = events._v_parent._v_name[8:]
            if 511 in [ref_s, s]:
                # skip for now
                continue
            dt = ref_events.col('ext_timestamp').astype(int) - events.col('ext_timestamp').astype(int)

            bins = arange(-2000, 2000.1, 40)
            counts, bins = histogram(dt, bins=bins, density=True)

            plot = Plot()
            offset = plot_fits(plot, counts, bins)
            plot.histogram(counts, bins - offset)
            plot.set_xlabel(r'$\Delta t$ [\si{\ns}]')
            plot.set_ylabel('Counts')
            plot.set_ylimits(min=0)
            plot.set_xlimits(-2000, 2000)
            plot.save_as_pdf('plots/pair_dt_{}_{}'.format(ref_s, s))


if __name__ == "__main__":
    plot_offset_distributions()
