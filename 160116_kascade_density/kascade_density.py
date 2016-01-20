"""Compare predicted detector density to the detected number of particles"""

import tables
from numpy import (histogram2d, histogram, linspace, logspace, array,
                   log10, inf, where, sqrt, abs, interp, zeros, mean, diff,
                   empty_like, copyto)
from scipy.stats import poisson, norm

from artist import Plot, MultiPlot

from sapphire.analysis.find_mpv import FindMostProbableValueInSpectrum as FindMPV

from fit_curve import ice_cube_pmt

DATA_PATH = '/Users/arne/Datastore/kascade/kascade-reconstructions.h5'
COLORS = ['black', 'red', 'green', 'blue']
LOG_TICKS = [.1, .2, .3, .4, .5, .6, .7 ,.8, .9,
             1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 20, 30, 40, 50, 60, 70, 80, 90]
LOG_LABELS = [''] * len(LOG_TICKS)
LOG_LABELS[0] = '0.1'
LOG_LABELS[1] = '0.2'
LOG_LABELS[4] = '0.5'
LOG_LABELS[9] = '1'
LOG_LABELS[10] = '2'
LOG_LABELS[13] = '5'
LOG_LABELS[18] = '10'
LOG_LABELS[19] = '20'
LOG_LABELS[22] = '50'


def get_out_for_in(actual_in, ref_in, ref_out):
    return interp(actual_in, ref_in, ref_out)


def fit_mpvs(ni):
    corrected_ni = empty_like(ni)
    copyto(corrected_ni, ni)
    bins = linspace(0, 3800, 300)
    for i in range(4):
        fit_mpv(ni[:, i], bins)
        corrected_ni[:, i] = ni[:, i] * (380 / mpv)
    return corrected_ni


def fit_mpv(n, bins):
    fit = FindMPV(*histogram(n * 380, bins=bins)).find_mpv()
    if not fit[1]:
        RuntimeError("Failed MPV fit.")
    return mpv = fit[0]


def plot_2d_histogram(plot, n, k_n, lin_bins, bins, detected_n,
                      lower, upper, detected_lower, detected_upper,
                      dvindvout, sigma_Vin):
    """Add expected lines to hisparc v kascade density plot"""

    counts, xbins, ybins = histogram2d(log10(k_n), log10(n), bins=bins, normed=True)
    counts[counts == -inf] = 0
    plot.histogram2d(counts, xbins, ybins, bitmap=True, type='reverse_bw')
#     plot.plot([-10, max(bins)], [-10, max(bins)], linestyle='green', mark=None)
    plot.plot(log10(lin_bins), log10(detected_n + 0.00001), linestyle='red', mark=None)
    plot.plot(log10(lin_bins), log10(lower + 0.00001), linestyle='thick, densely dashed, red', mark=None)
    plot.plot(log10(lin_bins), log10(upper + 0.00001), linestyle='thick, densely dashed, red', mark=None)
    plot.plot(log10(lin_bins), log10(detected_lower + 0.00001), linestyle='thick, densely dashed, green', mark=None)
    plot.plot(log10(lin_bins), log10(detected_upper + 0.00001), linestyle='thick, densely dashed, green', mark=None)
    plot.plot(log10(lin_bins[:-1]), log10(detected_n[:-1] + (dvindvout * sigma_Vin)), linestyle='thick, densely dashed, blue', mark=None)
    plot.plot(log10(lin_bins[:-1]), log10(detected_n[:-1] - (dvindvout * sigma_Vin)), linestyle='thick, densely dashed, blue', mark=None)


def plot_2d_histogram_detectors(ni, k_ni, lin_bins, bins, detected_n,
                                lower, upper, detected_lower, detected_upper,
                                dvindvout, sigma_Vin):
    mplot = MultiPlot(2, 2, width=r'.3\linewidth', height=r'.3\linewidth')
    for i in range(4):
        splot = mplot.get_subplot_at(i / 2, i % 2)
        plot_2d_histogram(splot, ni[:, i], k_ni[:, i], lin_bins, bins, detected_n,
                          lower, upper, detected_lower, detected_upper,
                          dvindvout, sigma_Vin)
    mplot.set_ytick_labels_for_all(None, LOG_LABELS)
    mplot.set_xtick_labels_for_all(None, LOG_LABELS)
    mplot.show_xticklabels_for_all([(1, 0), (0, 1)])
    mplot.show_yticklabels_for_all([(1, 0), (0, 1)])
    mplot.set_yticks_for_all(ticks=log10(LOG_TICKS))
    mplot.set_xticks_for_all(ticks=log10(LOG_TICKS))
    mplot.set_ylabel(r'HiSPARC detected density [\si{\per\meter\squared}]')
    mplot.set_xlabel(r'KASCADE predicted density [\si{\per\meter\squared}]')
    mplot.save_as_pdf('hisparc_v_kascade_detectors_mpv')


def plot_2d_histogram_station(n, k_n, lin_bins, bins, detected_n,
                              lower, upper, detected_lower, detected_upper,
                              dvindvout, sigma_Vin):
    plot = Plot()
    plot_2d_histogram(plot, n, k_n, lin_bins, bins, detected_n,
                      lower, upper, detected_lower, detected_upper,
                      dvindvout, sigma_Vin)
    plot.set_ylabel(r'HiSPARC detected density [\si{\per\meter\squared}]')
    plot.set_xlabel(r'KASCADE predicted density [\si{\per\meter\squared}]')
    plot.set_yticks(log10(LOG_TICKS))
    plot.set_xticks(log10(LOG_TICKS))
    plot.set_ytick_labels(LOG_LABELS)
    plot.set_xtick_labels(LOG_LABELS)
    plot.save_as_pdf('hisparc_v_kascade_average_mpv')


def plot_2d_histogram_detector_average(n, ni, lin_bins, bins):
    mplot = MultiPlot(2, 2, width=r'.3\linewidth', height=r'.3\linewidth')
    for i in range(4):
        splot = mplot.get_subplot_at(i / 2, i % 2)
        counts, xbins, ybins = histogram2d(log10(ni[:, i]), log10(n), bins=bins)
        counts[counts == -inf] = 0
        splot.histogram2d(counts, xbins, ybins, bitmap=True, type='reverse_bw')

    mplot.set_yticks_for_all(ticks=log10(LOG_TICKS))
    mplot.set_xticks_for_all(ticks=log10(LOG_TICKS))
    return mplot


def plot_2d_histogram_detector_v_average_kascade(k_n, k_ni, lin_bins, bins):
    mplot = plot_2d_histogram_detector_average(k_n, k_ni, lin_bins, bins)
    mplot.set_ylabel(r'KASCADE predicted density average [\si{\per\meter\squared}]')
    mplot.set_xlabel(r'KASCADE predicted density detector i [\si{\per\meter\squared}]')
    mplot.save_as_pdf('detector_v_average_kascade')


def plot_2d_histogram_detector_v_average_hisparc(n, ni, lin_bins, bins):
    mplot = plot_2d_histogram_detector_average(n, ni, lin_bins, bins)
    mplot.set_ylabel(r'HiSPARC detected density average [\si{\per\meter\squared}]')
    mplot.set_xlabel(r'HiSPARC detected density detector i [\si{\per\meter\squared}]')
    mplot.save_as_pdf('detector_v_average_hisparc')


def plot_slice_histogram(n, k_n, density):
    plot = Plot()
    for dens in density:
        counts, bins = histogram(n.compress(abs(k_n - dens) < round(sqrt(dens) / 2.)),
                                 bins=linspace(0, 9, 100), density=True)
        plot.histogram(counts, bins)
        plot.add_pin(r'\SI[multi-part-units=single, separate-uncertainty]{%d\pm%d}{\per\meter\squared}' %
                    (dens, round(sqrt(dens) / 2.)), 'above', bins[counts.argmax()])
    plot.set_ylimits(min=0)
    plot.set_xlimits(min=0, max=9)
    plot.set_xlabel(r'HiSPARC detected density [\si{\per\meter\squared}]')
    plot.set_ylabel(r'Counts')
    plot.save_as_pdf('histogram_slice')


def plot_contribution_histogram(n, k_n):
    plot = Plot('semilogy')
    sum_counts = zeros(100)
    colors = ['red', 'blue', 'green', 'purple', 'gray', 'brown', 'cyan', 'magenta', 'orange', 'teal']
    max_n = 11
    padding = 0.5
    bins = linspace(0, 9, 50)
    for i, density in enumerate(range(1, max_n)):
        counts, bins = histogram(n.compress(abs(k_n - density) < padding), bins=bins)
        plot.histogram(counts, bins + (i / 100.), linestyle=colors[i % len(colors)])
#         counts, bins = histogram(n.compress(k_n > i + padding), bins=bins)
#         plot.histogram(counts, bins, linestyle='%s, thick, densely dashed' % colors[i % len(colors)])
    counts, bins = histogram(n.compress(k_n > (max_n - padding)), bins=bins)
    plot.histogram(counts, bins, linestyle='red, thick, densely dashed')

    counts, bins = histogram(n, bins=bins)
    plot.histogram(counts, bins)
    plot.set_ylimits(min=0.9)
    plot.set_xlimits(min=0, max=9)
    plot.set_xlabel(r'HiSPARC detected density [\si{\per\meter\squared}]')
    plot.set_ylabel(r'Counts')
    plot.save_as_pdf('histogram_contribution_detector')


def plot_n_histogram(n, k_n, ni, k_ni):
    bins = linspace(0, 11, 200)
    plot = Plot('semilogy')
    plot.histogram(*histogram(n, bins=bins), linestyle='dotted')
    plot.histogram(*histogram(k_n, bins=bins), linestyle='thick, densely dashed, gray')

    for i in range(4):
        plot.histogram(*histogram(ni[:, i], bins=bins), linestyle=COLORS[i])
#         plot.histogram(*histogram(k_ni[:, i], bins=bins), linestyle='gray!50!%s' % COLORS[i])
    plot.set_ylimits(min=.99)
    plot.set_xlimits(min=bins[0], max=bins[-1])
    plot.draw_vertical_line(1)
    plot.set_xlabel(r'Lepton density [\si{\per\meter\squared}]')
    plot.set_ylabel(r'Counts')
    plot.save_as_pdf('histogram')


def plot_derrivative_pmt(lin_bins, dvindvout, sigma):
    plot = Plot()
    plot.plot(lin_bins[:-1], sigma / dvoutdvin, mark=None)
    plot.set_xlimits(min=lin_bins[0], max=lin_bins[-1])
    plot.set_xlabel(r'Lepton density [\si{\per\meter\squared}]')
    plot.set_ylabel(r'$\sigmaV_{\mathrm{in}}\frac{\mathrm{d}V_{\mathrm{out}}}{\mathrm{d}V_{\mathrm{in}}}$')
    plot.save_as_pdf('derrivative_pmt_saturation')


def get_densities(data):
    recs = data.root.reconstructions

    n1 = recs.col('n1')
    n2 = recs.col('n2')
    n3 = recs.col('n3')
    n4 = recs.col('n4')
    ni = array([n1, n2, n3, n4]).T
    n = ni.sum(axis=1) / 4.

    k_ni = recs.col('k_dens_mu') + recs.col('k_dens_e')
    k_n = k_ni.sum(axis=1) / 4.
    return n, ni, k_n, k_ni


def plot_kascade_v_hisparc(n, ni, k_n, k_ni):

    lin_bins = linspace(0.001, 50, 1000)
    bins = linspace(-0.5, log10(50), 100)

    n_to_ph = 415. # 3900. / max(n)
    ref_out = lin_bins
    ref_in = ice_cube_pmt(ref_out * n_to_ph, 29.1, 9000, 2.6) / n_to_ph
    detected_n = get_out_for_in(lin_bins, ref_in, ref_out)

    # Error due to saturation
    dvindvout = diff(lin_bins) / diff(detected_n) # dVin/dVout
    sigma_Vin = 0.05  # Error on Vin

    # Resolution of the detector
    sigma_res = 0.68
    g_lower, g_upper = norm.interval(0.68, lin_bins, sqrt(lin_bins) * 0.68)
    detected_g_lower = get_out_for_in(g_lower, ref_in, ref_out)
    detected_g_upper = get_out_for_in(g_upper, ref_in, ref_out)

    # Poisson error 68% interval (one sigma)
    lower, upper = poisson.interval(0.68, lin_bins)
    detected_lower = get_out_for_in(lower, ref_in, ref_out)
    detected_upper = get_out_for_in(upper, ref_in, ref_out)

    # Fit MPV
    corrected_ni = fit_mpv(ni)
    corrected_n = corrected_ni.sum(axis=1) / 4.

    plot_derrivative_pmt(lin_bins, dvindvout, sigma_Vin)
    plot_n_histogram(n, k_n, ni, k_ni)
    plot_n_histogram(corrected_n, k_n, corrected_ni, k_ni)
    plot_slice_histogram(n, k_n, [1, 3, 8, 15, 30])
    plot_contribution_histogram(ni[:, 1], k_ni[:, 1])
    plot_contribution_histogram(n, k_n)
    plot_2d_histogram_detectors(corrected_ni, k_ni, lin_bins, bins, detected_n, detected_g_lower, detected_g_upper, detected_lower, detected_upper, dvindvout, sigma_Vin)
    plot_2d_histogram_station(corrected_n, k_n, lin_bins, bins, detected_n, detected_g_lower, detected_g_upper, detected_lower, detected_upper, dvindvout, sigma_Vin)
    plot_2d_histogram_detector_v_average_kascade(k_n, k_ni, lin_bins, bins)
    plot_2d_histogram_detector_v_average_hisparc(n, ni, lin_bins, bins)


if __name__ == "__main__":
    if 'densities' not in globals():
        with tables.open_file(DATA_PATH, 'r') as data:
            densities = get_densities(data)

    plot_kascade_v_hisparc(*densities)
