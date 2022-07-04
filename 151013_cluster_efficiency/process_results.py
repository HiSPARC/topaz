import glob

import tables

from numpy import arange, array, degrees, histogram, histogram2d, isnan, linspace, log10, pi, radians, sin, sqrt, where

from artist import MultiPlot, Plot

from sapphire.utils import pbar

# PATHS = '/Users/arne/Datastore/cluster_efficiency/151013*.h5'
# PATHS = '/Users/arne/Datastore/cluster_efficiency/151014_*.h5'
PATHS = '/Users/arne/Datastore/cluster_efficiency/15101*.h5'


def get_combined_results():
    zenith = []
    zenith_in = []
    azimuth = []
    azimuth_in = []
    energy_in = []
    size_in = []
    r_in = []

    zenith_init = []
    azimuth_init = []
    energy_init = []
    size_init = []
    r_init = []

    for path in pbar(glob.glob(PATHS)):
        with tables.open_file(path, 'r') as data:
            recs = data.root.coincidences.reconstructions
            filtered_recs = recs.read_where('s501 & s502 & s503 & s504 & s505 & s506')
            zenith.extend(degrees(filtered_recs['zenith']))
            zenith_in.extend(degrees(filtered_recs['reference_zenith']))
            azimuth.extend(degrees(filtered_recs['azimuth']))
            azimuth_in.extend(degrees(filtered_recs['reference_azimuth']))
            energy_in.extend(log10(filtered_recs['reference_energy']))
            size_in.extend(log10(filtered_recs['reference_size']))
            r_in.extend(sqrt(filtered_recs['reference_x'] ** 2 + filtered_recs['reference_y'] ** 2))

            zenith_init.extend(degrees(recs.col('reference_zenith')))
            azimuth_init.extend(degrees(recs.col('reference_azimuth')))
            energy_init.extend(log10(recs.col('reference_energy')))
            size_init.extend(log10(recs.col('reference_size')))
            r_init.extend(sqrt(recs.col('reference_x') ** 2 + recs.col('reference_y') ** 2))

    zenith = array(zenith)
    filter = ~isnan(zenith)

    zenith = zenith.compress(filter)
    zenith_in = array(zenith_in).compress(filter)
    azimuth = array(azimuth).compress(filter)
    azimuth_in = array(azimuth_in).compress(filter)
    energy_in = array(energy_in).compress(filter)
    size_in = array(size_in).compress(filter)
    r_in = array(r_in).compress(filter)

    zenith_init = array(zenith_init)
    azimuth_init = array(azimuth_init)
    energy_init = array(energy_init)
    size_init = array(size_init)
    r_init = array(r_init)

    print(sum(filter), len(filter))

    return (
        zenith,
        zenith_in,
        azimuth,
        azimuth_in,
        energy_in,
        size_in,
        r_in,
        zenith_init,
        azimuth_init,
        energy_init,
        size_init,
        r_init,
    )


def make_plots():
    # plot_input_v_reconstructed_zenith()
    plot_input_v_reconstructed_azimuth()
    # plot_input_detected_zenith_distribution()
    # plot_input_zenith_distribution()
    # plot_reconstructed_zenith_distribution()
    # plot_detected_v_energy()


def plot_input_v_reconstructed_zenith():
    plot = MultiPlot(2, 2, width=r'.3\textwidth', height=r'.3\textwidth')
    z_in_bins = arange(-3.75, 63.76, 7.5)
    z_out_bins = arange(0, 70, 1)

    for i, e in enumerate([16, 16.5, 17, 17.5]):
        splot = plot.get_subplot_at(int(i / 2), int(i % 2))
        c, xb, yb = histogram2d(
            zenith_in.compress(energy_in == e), zenith.compress(energy_in == e), bins=(z_in_bins, z_out_bins)
        )
        splot.histogram2d(c, xb, yb, bitmap=True, type='reverse_bw')
        splot.plot([0, 60], [0, 60], linestyle='red', mark=None)

    # plot.set_title('Input and detected zeniths for shower energy: %.1f' % e)
    # plot.set_xlimits(0, 65)
    # plot.set_ylimits(0)
    plot.show_xticklabels_for_all([(1, 0), (0, 1)])
    plot.show_yticklabels_for_all([(1, 0), (0, 1)])
    plot.save_as_pdf('reconstructed_v_in_zenith.pdf')


def plot_input_v_reconstructed_azimuth():
    plot = MultiPlot(2, 2, width=r'.3\textwidth', height=r'.3\textwidth')
    a_bins = linspace(-180, 180, 60)

    for i, e in enumerate([16, 16.5, 17, 17.5]):
        splot = plot.get_subplot_at(int(i / 2), int(i % 2))
        c, xb, yb = histogram2d(azimuth_in.compress(energy_in == e), azimuth.compress(energy_in == e), bins=a_bins)
        splot.histogram2d(c, xb, yb, bitmap=True, type='reverse_bw')
        splot.plot([-180, 180], [-180, 180], linestyle='red', mark=None)

    plot.show_xticklabels_for_all([(1, 0), (0, 1)])
    plot.show_yticklabels_for_all([(1, 0), (0, 1)])
    plot.save_as_pdf('reconstructed_v_in_azimuth.pdf')


def plot_input_detected_zenith_distribution():
    plot = Plot()
    z_bins = arange(-3.75, 63.76, 7.5)
    shades = ['black', 'black!75', 'black!50', 'black!25']
    for i, e in enumerate([16, 16.5, 17, 17.5]):
        c_init, b = histogram(zenith_init.compress(energy_init == e), bins=z_bins)
        c_in, b = histogram(zenith_in.compress(energy_in == e), bins=z_bins)
        corrected_counts = where(isnan(c_in / c_init), 0, sin(radians(b[1:])) * c_in / c_init)
        plot.histogram(corrected_counts, b, linestyle=shades[i])

    # plot.set_title('Input and detected zeniths for shower energy: %.1f' % e)
    plot.set_xlimits(0, 65)
    plot.set_ylimits(0)
    plot.save_as_pdf('e%.1f.pdf' % e)


def plot_input_zenith_distribution():
    plot = MultiPlot(2, 2, width=r'.3\textwidth', height=r'.3\textwidth')
    for i, e in enumerate([16, 16.5, 17, 17.5]):
        splot = plot.get_subplot_at(int(i / 2), int(i % 2))
        c, b = histogram(zenith_init.compress(energy_init == e), bins=arange(0, 65, 1))
        splot.histogram(c, b)
    plot.set_title('Input zeniths per shower energy')
    plot.set_xlimits_for_all(None, 0, 65)
    plot.set_ylimits_for_all(None, 0)
    plot.save_as_pdf('zenith_input')


def plot_reconstructed_zenith_distribution():
    plot = MultiPlot(2, 2, width=r'.3\textwidth', height=r'.3\textwidth')
    for i, e in enumerate([16, 16.5, 17, 17.5]):
        splot = plot.get_subplot_at(int(i / 2), int(i % 2))
        c, b = histogram(zenith.compress(energy_in == e), bins=arange(0, 65, 1))
        splot.histogram(c, b)
    plot.set_title('Reconstructed zeniths per shower energy')
    plot.set_xlimits_for_all(None, 0, 65)
    plot.set_ylimits_for_all(None, 0)
    plot.save_as_pdf('zenith_reconstructed')


def plot_detected_zenith_distribution():
    plot = MultiPlot(2, 2, width=r'.3\textwidth', height=r'.3\textwidth')
    for i, e in enumerate([16, 16.5, 17, 17.5]):
        splot = plot.get_subplot_at(int(i / 2), int(i % 2))
        c, b = histogram(zenith.compress(energy_in == e), bins=arange(0, 65, 1))
        splot.histogram(c, b)
    plot.set_title('Reconstructed zeniths per shower energy')
    plot.set_xlimits_for_all(None, 0, 65)
    plot.set_ylimits_for_all(None, 0)
    plot.save_as_pdf('zenith_reconstructed')


def plot_detected_v_energy():
    plot = Plot(width=r'.6\textwidth')
    # plot.set_title('Detected core distances vs shower energy')
    c, xb, yb = histogram2d(r_in, energy_in, bins=(arange(0, 600, 40), arange(15.75, 17.76, 0.5)))
    plot.histogram2d(c, xb, yb, bitmap=True)
    plot.set_yticks([16, 16.5, 17, 17.5])
    plot.set_ytick_labels(['$10^{%.1f}$' % e for e in [16, 16.5, 17, 17.5]])
    plot.set_ylabel(r'Shower energy [\si{\eV}]')
    plot.set_xlabel(r'Core distance [\si{\meter}]')
    plot.save_as_pdf('detected_v_energy')

    plot = Plot(width=r'.6\textwidth')
    # plot.set_title('Detected core distances vs shower energy, scaled to bin area')
    counts, xbins, ybins = histogram2d(r_in, energy_in, bins=(arange(0, 600, 40), arange(15.75, 17.76, 0.5)))
    plot.histogram2d((-counts.T / (pi * (xbins[:-1] ** 2 - xbins[1:] ** 2))).T, xbins, ybins, type='area')
    plot.set_yticks([16, 16.5, 17, 17.5])
    plot.set_ytick_labels(['$10^{%.1f}$' % e for e in [16, 16.5, 17, 17.5]])
    plot.set_ylabel(r'Shower energy [\si{\eV}]')
    plot.set_xlabel(r'Core distance [\si{\meter}]')
    plot.save_as_pdf('detected_v_energy_scaled_area')
    # print counts.T/(pi * (xbins[:-1]**2 - xbins[1:] **2))


if __name__ == "__main__":
    if not 'zenith' in globals():
        (
            zenith,
            zenith_in,
            azimuth,
            azimuth_in,
            energy_in,
            size_in,
            r_in,
            zenith_init,
            azimuth_init,
            energy_init,
            size_init,
            r_init,
        ) = get_combined_results()
    make_plots()
