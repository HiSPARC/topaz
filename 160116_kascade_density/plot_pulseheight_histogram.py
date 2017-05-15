import tables

from numpy import arange, histogram, linspace, where

from artist import Plot

from sapphire.analysis import landau


def plot_pulseheight_histogram(data):
    events = data.root.hisparc.cluster_kascade.station_601.events
    ph = events.col('n1')

    s = landau.Scintillator()
    mev_scale = 3.38 / 1.
    count_scale = 6e3 / .32

    n, bins = histogram(ph, bins=arange(0, 9, 0.025))
    x = linspace(0, 9, 1500)

    plot = Plot()
    n_trunc = where(n <= 100000, n, 100000)
    plot.histogram(n_trunc, bins, linestyle='gray')

    plot.plot(x, s.conv_landau_for_x(x, mev_scale=mev_scale,
                                     count_scale=count_scale, gauss_scale=.68),
              mark=None)
#     plot.add_pin('convolved Landau', x=1.1, location='above right',
#                   use_arrow=True)

    plot.plot(x, count_scale * s.landau_pdf(x * mev_scale), mark=None,
              linestyle='black')
#     plot.add_pin('Landau', x=1., location='above right', use_arrow=True)

    plot.set_xlabel(r"Number of particles")
    plot.set_ylabel(r"Number of events")
    plot.set_xlimits(0, 9)
    plot.set_ylimits(0, 21000)
    plot.save_as_pdf("plot_pulseheight_histogram_pylandau")


if __name__ == '__main__':
    if 'data' not in globals():
        data = tables.open_file('/Users/arne/Datastore/kascade/kascade-20080912.h5')

    plot_pulseheight_histogram(data)
