"""Compare predicted detector density to the detected number of particles

Errors on data:
- Scintillator transmission and PMT gain errors (relative error of ~70%).
- Error due to non linearity of the PMT curve.
- Poisson error on both in and output.

Bias:
- There may be a bias in the data, at low particle densities detector 2 is
  more likely to give detect no particles than the other three detectors.
  This may be caused by offline datacuts which prefer events with at least
  a number of particles in the corner detectors. However, there are also
  events with low signals in those detectors.

The MPV is not properly fit in the dataset. The n# columns are simply
pulseheights divided by 380. So determine the MPV (per channel) and correctly
convert pulsehieght to the number of detected particles.

This can probably be improved further by using the pulseintegrals.

The PMT non-linearity needs to be determined per channel. Use the KASCADE
predicted density as the input. After fitting the curve (in = f(out)) the
output can be converted back to the actual expected output.

"""
import tables

from numpy import (
    abs, append, array, copyto, cos, diff, empty_like, histogram, histogram2d, inf, interp, linspace, log10, logspace,
    mean, median, sqrt, std, where, zeros)
from scipy.stats import binned_statistic, norm, poisson

from artist import MultiPlot, Plot

from sapphire.analysis.find_mpv import FindMostProbableValueInSpectrum as FindMPV

from fit_curve import fit_curve, fit_function

DATA_PATH = '/Users/arne/Datastore/kascade/kascade-reconstructions.h5'
COLORS = ['black', 'red', 'green', 'blue']

SRC_PH_MPV = 380.  # Pulseheight MPV used for n columns in data file
SRC_PI_MPV = 5000.  # Pulseintegral MPV used for reconstructions_n in data file


def get_out_for_in(actual_in, ref_in, ref_out):
    """Convert an input signal to expected output"""

    return interp(actual_in, ref_in, ref_out)


def get_in_for_out(detected_out, ref_out, ref_in):
    """Convert an output signal to corresponding input"""

    return interp(detected_out, ref_out, ref_in)


def fit_mpvs(ni):
    corrected_ni = empty_like(ni)
    copyto(corrected_ni, ni)
    bins = linspace(0, 3800, 300)
    mpvs = []
    for i in range(4):
        mpv = fit_mpv(ni[:, i] * SRC_PH_MPV, bins)
        mpvs.append(mpv)
        corrected_ni[:, i] = ni[:, i] * (SRC_PH_MPV / mpv)
    return corrected_ni, mpvs


def fit_mpv(n, bins):
    fit = FindMPV(*histogram(n, bins=bins)).find_mpv()
    if not fit[1]:
        RuntimeError("Failed MPV fit.")
    return fit[0]


def residuals(yfit, ydata):
    return ((yfit - ydata) ** 2 / ydata)


class KascadeDensity(object):

    def __init__(self, data_path=DATA_PATH):
        self.lin_bins = linspace(0.5, 200.5, 201)
        narrow_bins = linspace(0.5, 30.5, 31)
#         wide_bins = linspace(31.5, 40.5, 4)
        self.slice_bins = narrow_bins  # append(narrow_bins, wide_bins)
        self.slice_bins_c = (self.slice_bins[:-1] + self.slice_bins[1:]) / 2.
        self.ref_out = linspace(0.1, 200, 4000)
        self.ref_in_i = zeros((len(self.ref_out), 4))
        self.log_bins = logspace(log10(self.lin_bins[0]),
                                 log10(self.lin_bins[-1]), 100)

        with tables.open_file(DATA_PATH, 'r') as data:
            self.read_densities(data)
#         self.process_densities()

    def read_densities(self, data):
        """Read and process data points"""

        recs = data.root.reconstructions

        # Pulseheight-based counts (plulseheight / 380.)
        n1 = recs.col('n1')
        n2 = recs.col('n2')
        n3 = recs.col('n3')
        n4 = recs.col('n4')
        self.src_pi = array([n1, n2, n3, n4]).T
        self.src_pi[:, 1] = where(self.src_pi[:, 1] <= 0, 1e-2,
                                  self.src_pi[:, 1])
        self.src_p = self.src_pi.sum(axis=1) / 4.
        self.mpv_pi, _ = fit_mpvs(self.src_pi)
        self.mpv_p = self.mpv_pi.sum(axis=1) / 4.

        # Pulseintegral-based counts (integrals / 5000.)
        self.src_ni = array(data.root.reconstructions_integrals_n)
        self.src_ni[:, 1] = where(self.src_ni[:, 1] <= 0, 1e-2,
                                  self.src_ni[:, 1])
        self.src_n = self.src_ni.sum(axis=1) / 4.

        # Fit MPV per channel
        self.mpv_ni, self.mpv = fit_mpvs(self.src_ni)
        self.mpv_n = self.mpv_ni.sum(axis=1) / 4.

        self.zenith = recs.col('reference_theta')
        self.src_ki = recs.col('k_dens_mu') + recs.col('k_dens_e')
        self.src_k = self.src_ki.sum(axis=1) / 4.
        self.cor_ki = (self.src_ki.T * cos(self.zenith)).T
        self.cor_k = self.src_k * cos(self.zenith)

        # Median actual (KASCADE) for given measurement (HiSPARC)
        self.med_ki = zeros((len(self.slice_bins_c), 4))
        self.std_ki = zeros((len(self.slice_bins_c), 4))
        for i in range(4):
            self.med_ki[:, i] = binned_statistic(self.mpv_ni[:, i], self.src_ki[:, i],
                                                 statistic='mean', bins=self.slice_bins)[0]
            std_ki = binned_statistic(self.mpv_ni[:, i], self.src_ki[:, i],
                                      statistic=std, bins=self.slice_bins)[0]
            self.std_ki[:, i] = where(std_ki < self.med_ki[:, i], std_ki, self.med_ki[:, i] - 0.0001)
        self.med_k = binned_statistic(self.mpv_n, self.src_k,
                                      statistic='mean', bins=self.slice_bins)[0]
        self.std_k = binned_statistic(self.mpv_n, self.src_k,
                                      statistic=std, bins=self.slice_bins)[0]

        # Fit PMT curve
        # Fit on the medians of slices, i.e. for given measured value what is
        # the median expectation.
        self.cor_ni = empty_like(self.mpv_ni)
        self.fit_i = []
        for i in range(4):
            fit = fit_curve(self.slice_bins_c[1:], self.med_ki[:, i][1:])
            self.fit_i.append(fit[0])
            self.ref_in_i[:, i] = fit_function(self.ref_out, *fit[0])
            # Detected n corrected for PMT
            self.cor_ni[:, i] = get_in_for_out(self.mpv_ni[:, i], self.ref_out, self.ref_in_i[:, i])

        fit = fit_curve(self.slice_bins_c[1:], self.med_k[1:])
        self.fit = fit[0]
        self.ref_in = fit_function(self.ref_out, *self.fit)
        # Detected n corrected for PMT
        self.cor_n = get_in_for_out(self.mpv_n, self.ref_out, self.ref_in)

        self.res_ni = residuals(self.cor_ni, self.src_ki)
        self.res_n = residuals(self.cor_n, self.src_k)

    def process_densities(self):
        """Determine errors on the data"""

        # Error due to PMT linearity and ADC/mV resolution
#         self.lin_out_i = zeros((len(self.lin_bins), 4))
#         for i in range(4):
#             self.lin_out_i[:, i] = get_out_for_in(self.lin_bins, self.ref_in_i[:, i], self.ref_out)
#         self.lin_out = get_out_for_in(self.lin_bins, self.ref_in, self.ref_out)
#         self.dvindvout = (diff(self.lin_bins) / diff(self.lin_out_i[:,1])).tolist()  # dVin/dVout
#         self.dvindvout.extend([self.dvindvout[-1]])
#         self.dvindvout = array(self.dvindvout)
#         self.sigma_Vout = 0.57 / 2.  # Error on Vout
#         self.sigma_Vin = self.sigma_Vout * self.dvindvout

        # Resolution of the detector
        sigma_res = 0.7
        r_lower, r_upper = norm.interval(0.68, self.lin_bins, sqrt(self.lin_bins) * sigma_res)
        self.response_lower = r_lower
        self.response_upper = r_upper
        self.response_lower_pmt = get_out_for_in(r_lower, self.ref_in, self.ref_out)
        self.response_upper_pmt = get_out_for_in(r_upper, self.ref_in, self.ref_out)

        # Poisson error 68% interval (one sigma)
        # Note; Poisson error is less for average because of larger area.
        # Calculate std of expected given x,

        p_lower, p_upper = poisson.interval(0.68, self.lin_bins)
        self.poisson_lower = p_lower
        self.poisson_upper = p_upper
        self.poisson_lower_pmt = get_out_for_in(p_lower, self.ref_in, self.ref_out)
        self.poisson_upper_pmt = get_out_for_in(p_upper, self.ref_in, self.ref_out)

    def make_plots(self):

        return
        self.plot_pmt_curves()
        self.plot_fit_residuals_detector()
        self.plot_fit_residuals_station()

        self.plot_kas_n_histogram()
        self.plot_src_n_histogram()
        self.plot_mpv_n_histogram()
        self.plot_cor_n_histogram()
        self.plot_mpv_p_n_histogram()

        self.plot_src_hisparc_kascade_station()
        self.plot_mpv_hisparc_kascade_station()
        self.plot_cor_hisparc_kascade_station()
        self.plot_mpv_p_hisparc_kascade_station()
        self.plot_mpv_p_hisparc_hisparc_station()

        self.plot_src_hisparc_kascade_detector()
        self.plot_mpv_hisparc_kascade_detector()
        self.plot_cor_hisparc_kascade_detector()
        self.plot_mpv_p_hisparc_kascade_detector()
        self.plot_mpv_p_hisparc_hisparc_detector()

        self.plot_kascade_detector_average()
        self.plot_src_hisparc_detector_average()
        self.plot_mpv_hisparc_detector_average()
        self.plot_cor_hisparc_detector_average()
        self.plot_mpv_p_hisparc_detector_average()

        self.plot_src_contribution_detector()
        self.plot_mpv_contribution_detector()
        self.plot_cor_contribution_detector()
        self.plot_kas_contribution_detector()
        self.plot_mpv_p_contribution_detector()

        self.plot_src_contribution_station()
        self.plot_mpv_contribution_station()
        self.plot_cor_contribution_station()
        self.plot_kas_contribution_station()
        self.plot_mpv_p_contribution_station()

#         self.plot_derrivative_pmt()

        self.plot_slice_src()
        self.plot_slice_mpv()
        self.plot_slice_cor()
        return

    def plot_xy(self, plot):
        """Add x=y line to plots"""
        xy = [min(self.lin_bins), max(self.lin_bins)]
        plot.plot(xy, xy, linestyle='thick, orange', mark=None)

    def plot_errors_log(self, plot):
        """Add expected lines to hisparc v kascade density plot"""

#         plot.plot(self.lin_bins - self.sigma_Vin, self.lin_bins, linestyle='thick, blue', mark=None)
#         plot.plot(self.lin_bins + self.sigma_Vin, self.lin_bins, linestyle='thick, blue', mark=None)
#         plot.shade_region(self.lin_bins, self.response_lower, self.response_upper, color='red, opacity=0.2')
#         plot.plot(self.lin_bins, self.response_lower + 0.0001, linestyle='thick, red', mark=None)
#         plot.plot(self.lin_bins, self.response_upper + 0.0001, linestyle='thick, red', mark=None)
#         plot.plot(self.lin_bins, self.poisson_lower + 0.0001, linestyle='thick, green', mark=None)
#         plot.plot(self.lin_bins, self.poisson_upper + 0.0001, linestyle='thick, green', mark=None)
        plot.shade_region(self.lin_bins, self.poisson_lower, self.poisson_upper, color='green, opacity=0.2')

    def plot_2d_histogram_lines(self, plot, n, k_n):
        """Add expected lines to hisparc v kascade density plot"""

#         plot.plot([-10, max(self.lin_bins)], [-10, max(self.lin_bins)], linestyle='thick, green', mark=None)
#         plot.plot(self.lin_bins, self.lin_bins, xerr=self.sigma_Vin, linestyle='thick, blue', mark=None)
        plot.shade_region(self.lin_bins, self.response_lower, self.response_upper, color='red, opacity=0.2')
        plot.shade_region(self.lin_bins, self.poisson_lower, self.poisson_upper, color='green, opacity=0.2')
#         plot.plot(self.lin_bins, self.response_lower, linestyle='thick, red', mark=None)
#         plot.plot(self.lin_bins, self.response_upper, linestyle='thick, red', mark=None)
#         plot.plot(self.lin_bins, self.poisson_lower, linestyle='thick, green', mark=None)
#         plot.plot(self.lin_bins, self.poisson_upper, linestyle='thick, green', mark=None)

    def plot_hisparc_kascade_station(self, n, k_n):
        plot = Plot('loglog')
        counts, xbins, ybins = histogram2d(n, k_n,
                                           bins=self.log_bins, normed=True)
        counts[counts == -inf] = 0
        plot.histogram2d(counts, xbins, ybins,
                         bitmap=True, type='reverse_bw')
        self.plot_xy(plot)
        plot.set_xlabel(r'HiSPARC detected density [\si{\per\meter\squared}]')
        plot.set_ylabel(r'KASCADE predicted density [\si{\per\meter\squared}]')
        return plot

    def plot_hisparc_kascade_station_fit(self, plot):
        filter = self.ref_out < 500
        filter2 = self.ref_in < 500
        pin = self.ref_in.compress(filter & filter2)
        pout = self.ref_out.compress(filter & filter2)
        plot.plot(pout, pin, linestyle='blue', mark=None)
        plot.scatter(self.slice_bins_c, self.med_k,
                     xerr=(self.slice_bins[1:] - self.slice_bins[:-1]) / 2.,
                     yerr=self.std_k,
                     markstyle='red, mark size=.5pt')

    def plot_src_hisparc_kascade_station(self):
        plot = self.plot_hisparc_kascade_station(self.src_n, self.src_k)
        plot.save_as_pdf('plots/hisparc_kascade_station_src')

    def plot_mpv_hisparc_kascade_station(self):
        plot = self.plot_hisparc_kascade_station(self.mpv_n, self.src_k)
        self.plot_hisparc_kascade_station_fit(plot)
        plot.save_as_pdf('plots/hisparc_kascade_station_mpv')

    def plot_cor_hisparc_kascade_station(self):
        plot = self.plot_hisparc_kascade_station(self.cor_n, self.src_k)
        plot.save_as_pdf('plots/hisparc_kascade_station_cor')

    def plot_mpv_p_hisparc_kascade_station(self):
        plot = self.plot_hisparc_kascade_station(self.mpv_p, self.src_k)
        plot.save_as_pdf('plots/hisparc_kascade_station_mpv_p')

    def plot_mpv_p_hisparc_hisparc_station(self):
        """Compare counts from pulseheight versus counts from integral"""
        plot = self.plot_hisparc_kascade_station(self.mpv_p, self.mpv_n)
        plot.set_xlabel(r'HiSPARC pulseheight derived particle density [\si{\per\meter\squared}]')
        plot.set_ylabel(r'HiSPARC integral derived particle density [\si{\per\meter\squared}]')
        plot.save_as_pdf('plots/hisparc_hisparc_station_mpv_p')

    def plot_hisparc_kascade_detector(self, ni, k_ni):
        plot = MultiPlot(2, 2, 'loglog', width=r'.3\linewidth', height=r'.3\linewidth')
        for i in range(4):
            splot = plot.get_subplot_at(i / 2, i % 2)
            counts, xbins, ybins = histogram2d(ni[:, i], k_ni[:, i],
                                               bins=self.log_bins, normed=True)
            counts[counts == -inf] = 0
            splot.histogram2d(counts, xbins, ybins,
                              bitmap=True, type='reverse_bw')
            self.plot_xy(splot)

        plot.show_xticklabels_for_all([(1, 0), (0, 1)])
        plot.show_yticklabels_for_all([(1, 0), (0, 1)])
        plot.set_xlabel(r'HiSPARC detected density [\si{\per\meter\squared}]')
        plot.set_ylabel(r'KASCADE predicted density [\si{\per\meter\squared}]')
        return plot

    def plot_hisparc_kascade_detector_fit(self, plot):
        filter = self.ref_out < 500
        for i in range(4):
            filter2 = self.ref_in_i[:, i] < 500
            pin = self.ref_in_i[:, i].compress(filter & filter2)
            pout = self.ref_out.compress(filter & filter2)
            splot = plot.get_subplot_at(i / 2, i % 2)
            splot.plot(pout, pin, linestyle=COLORS[i], mark=None)
            splot.scatter(self.slice_bins_c, self.med_ki[:, i],
                          xerr=(self.slice_bins[1:] - self.slice_bins[:-1]) / 2.,
                          yerr=self.std_ki[:, i],
                          markstyle='red, mark size=.5pt')

    def plot_src_hisparc_kascade_detector(self):
        plot = self.plot_hisparc_kascade_detector(self.src_ni, self.src_ki)
        plot.save_as_pdf('plots/hisparc_kascade_detector_src')

    def plot_mpv_hisparc_kascade_detector(self):
        plot = self.plot_hisparc_kascade_detector(self.mpv_ni, self.src_ki)
        self.plot_hisparc_kascade_detector_fit(plot)
        plot.save_as_pdf('plots/hisparc_kascade_detector_mpv')

    def plot_cor_hisparc_kascade_detector(self):
        plot = self.plot_hisparc_kascade_detector(self.cor_ni, self.src_ki)
        plot.save_as_pdf('plots/hisparc_kascade_detector_cor')

    def plot_mpv_p_hisparc_kascade_detector(self):
        plot = self.plot_hisparc_kascade_detector(self.mpv_pi, self.src_ki)
        plot.save_as_pdf('plots/hisparc_kascade_detector_mpv_p')

    def plot_mpv_p_hisparc_hisparc_detector(self):
        """Compare counts from pulseheight versus counts from integral"""
        plot = self.plot_hisparc_kascade_detector(self.mpv_pi, self.mpv_ni)
        plot.set_xlabel(r'HiSPARC pulseheight derived particle density [\si{\per\meter\squared}]')
        plot.set_ylabel(r'HiSPARC integral derived particle density [\si{\per\meter\squared}]')
        plot.save_as_pdf('plots/hisparc_hisparc_detector_mpv_p')

    def plot_detector_average(self, n, ni):
        plot = MultiPlot(2, 2, width=r'.3\linewidth', height=r'.3\linewidth')
        for i in range(4):
            splot = plot.get_subplot_at(i / 2, i % 2)
            counts, xbins, ybins = histogram2d(ni[:, i], n, bins=self.log_bins)
            counts[counts == -inf] = 0
            splot.histogram2d(counts, xbins, ybins, bitmap=True, type='reverse_bw')
        plot.show_xticklabels_for_all([(1, 0), (0, 1)])
        plot.show_yticklabels_for_all([(1, 0), (0, 1)])
        return plot

    def plot_kascade_detector_average(self):
        mplot = self.plot_detector_average(self.src_k, self.src_ki)
        mplot.set_xlabel(r'KASCADE predicted density detector i [\si{\per\meter\squared}]')
        mplot.set_ylabel(r'KASCADE predicted density average [\si{\per\meter\squared}]')
        mplot.save_as_pdf('plots/detector_average_kas')

    def plot_src_hisparc_detector_average(self):
        mplot = self.plot_detector_average(self.src_n, self.src_ni)
        mplot.set_xlabel(r'HiSPARC detected density detector i [\si{\per\meter\squared}]')
        mplot.set_ylabel(r'HiSPARC detected density average [\si{\per\meter\squared}]')
        mplot.save_as_pdf('plots/detector_average_src')

    def plot_mpv_hisparc_detector_average(self):
        mplot = self.plot_detector_average(self.mpv_n, self.mpv_ni)
        mplot.set_xlabel(r'HiSPARC detected density detector i [\si{\per\meter\squared}]')
        mplot.set_ylabel(r'HiSPARC detected density average [\si{\per\meter\squared}]')
        mplot.save_as_pdf('plots/detector_average_mpv')

    def plot_cor_hisparc_detector_average(self):
        mplot = self.plot_detector_average(self.cor_n, self.cor_ni)
        mplot.set_xlabel(r'HiSPARC detected density detector i [\si{\per\meter\squared}]')
        mplot.set_ylabel(r'HiSPARC detected density average [\si{\per\meter\squared}]')
        mplot.save_as_pdf('plots/detector_average_cor')

    def plot_mpv_p_hisparc_detector_average(self):
        mplot = self.plot_detector_average(self.mpv_p, self.mpv_pi)
        mplot.set_xlabel(r'HiSPARC detected density detector i [\si{\per\meter\squared}]')
        mplot.set_ylabel(r'HiSPARC detected density average [\si{\per\meter\squared}]')
        mplot.save_as_pdf('plots/detector_average_mpv_p')

    def plot_pmt_curves(self):
        plot = Plot('loglog')
        filter = self.ref_out < 50

        for i in range(4):
            filter2 = self.ref_in_i[:, i] < 500
            pin = self.ref_in_i[:, i].compress(filter & filter2)
            pout = self.ref_out.compress(filter & filter2)
            plot.plot(pout, pin, linestyle=COLORS[i], mark=None)

        filter2 = self.ref_in < 500
        pin = self.ref_in.compress(filter & filter2)
        pout = self.ref_out.compress(filter & filter2)
        plot.plot(pout, pin, linestyle='pink', mark=None)

        plot.set_ylimits(min=min(self.lin_bins), max=max(self.lin_bins))
        plot.set_xlimits(min=min(self.lin_bins), max=max(self.lin_bins))
        plot.set_ylabel(r'Input signal')
        plot.set_xlabel(r'Output signal')
        plot.save_as_pdf('plots/pmt_curves')

    def plot_fit_residuals_detector(self):
        plot = MultiPlot(2, 2, width=r'.3\linewidth', height=r'.3\linewidth')
        for i in range(4):
            splot = plot.get_subplot_at(i / 2, i % 2)
            res = fit_function(self.slice_bins_c, *self.fit_i[i]) - self.med_ki[:, i]
            splot.scatter(self.slice_bins_c, res,
                          xerr=(self.slice_bins[1:] - self.slice_bins[:-1]) / 2.,
                          yerr=self.std_ki[:, i],
                          markstyle='red, mark size=1pt')
            splot.draw_horizontal_line(0, linestyle='gray')
#             splot.plot(self.lin_bins, fit_function(self.lin_bins, self.fit_i[i])

        plot.set_ylimits_for_all(min=-30, max=30)
        plot.set_xlimits_for_all(min=0, max=max(self.slice_bins))
        plot.show_xticklabels_for_all([(1, 0), (0, 1)])
        plot.show_yticklabels_for_all([(1, 0), (0, 1)])
        plot.set_xlabel(r'HiSPARC detected density [\si{\per\meter\squared}]')
        plot.set_ylabel(r'Residuals (Predicted - Fit) [\si{\per\meter\squared}]')
        plot.save_as_pdf('plots/fit_residuals_detector')

    def plot_fit_residuals_station(self):
        plot = Plot()
        res = fit_function(self.slice_bins_c, *self.fit) - self.med_k
        plot.scatter(self.slice_bins_c, res,
                     xerr=(self.slice_bins[1:] - self.slice_bins[:-1]) / 2.,
                     yerr=self.std_k,
                     markstyle='red, mark size=1pt')
        plot.draw_horizontal_line(0, linestyle='gray')

        plot.set_ylimits(min=-30, max=30)
        plot.set_xlimits(min=0, max=max(self.slice_bins))
        plot.set_xlabel(r'HiSPARC detected density [\si{\per\meter\squared}]')
        plot.set_ylabel(r'Residuals (Predicted - Fit) [\si{\per\meter\squared}]')
        plot.save_as_pdf('plots/fit_residuals_station')

    def plot_slice(self, n):
        densities = [1, 3, 8, 15, 30]
        bins = linspace(0, 15, 150)
        plot = Plot()
        for density in densities:
            padding = round(sqrt(density) / 2.)
            counts, bins = histogram(n.compress(abs(self.src_k - density) < padding),
                                     bins=bins, density=True)
            plot.histogram(counts, bins)
            plot.add_pin(r'\SI[multi-part-units=single, separate-uncertainty]{%d\pm%d}{\per\meter\squared}' %
                         (density, padding), 'above', bins[counts.argmax()])
        plot.set_ylimits(min=0)
        plot.set_xlimits(min=bins[0], max=bins[-1])
        plot.set_xlabel(r'HiSPARC detected density [\si{\per\meter\squared}]')
        plot.set_ylabel(r'Counts')
        return plot

    def plot_slice_src(self):
        plot = self.plot_slice(self.src_n)
        plot.save_as_pdf('plots/slice_src')

    def plot_slice_mpv(self):
        plot = self.plot_slice(self.mpv_n)
        plot.save_as_pdf('plots/slice_mpv')

    def plot_slice_cor(self):
        plot = self.plot_slice(self.cor_n)
        plot.save_as_pdf('plots/slice_cor')

    def plot_contribution_station(self, n, ref_n):
        plot = Plot('semilogy')
        colors = ['red', 'blue', 'green', 'purple', 'gray', 'brown', 'cyan',
                  'magenta', 'orange', 'teal']
        padding = 0.25
        bins = linspace(0, 20, 150)
        plot.histogram(*histogram(n, bins=bins))
        plot.draw_vertical_line(1)
        for j, density in enumerate(range(1, 8) + [15] + [20]):
            n_slice = n.compress(abs(ref_n - density) < padding)
            counts, bins = histogram(n_slice, bins=bins)
            plot.histogram(counts, bins + (j / 100.), linestyle=colors[j % len(colors)])
        plot.set_ylimits(min=0.9, max=1e5)
        plot.set_xlimits(min=bins[0], max=bins[-1])
        plot.set_xlabel(r'HiSPARC detected density [\si{\per\meter\squared}]')
        plot.set_ylabel(r'Counts')
        return plot

    def plot_src_contribution_station(self):
        plot = self.plot_contribution_station(self.src_n, self.src_k)
        plot.save_as_pdf('plots/contribution_station_scr')

    def plot_mpv_contribution_station(self):
        plot = self.plot_contribution_station(self.mpv_n, self.src_k)
        plot.save_as_pdf('plots/contribution_station_mpv')

    def plot_cor_contribution_station(self):
        plot = self.plot_contribution_station(self.cor_n, self.src_k)
        plot.save_as_pdf('plots/contribution_station_cor')

    def plot_kas_contribution_station(self):
        plot = self.plot_contribution_station(self.src_k, self.mpv_n)
        plot.set_xlabel(r'KASCADE predicted density [\si{\per\meter\squared}]')
        plot.save_as_pdf('plots/contribution_station_kas')

    def plot_mpv_p_contribution_station(self):
        plot = self.plot_contribution_station(self.mpv_p, self.src_k)
        plot.save_as_pdf('plots/contribution_station_mpv_p')

    def plot_contribution_detector(self, ni, ref_ni):
        plot = MultiPlot(2, 2, 'semilogy', width=r'.3\linewidth', height=r'.3\linewidth')
        colors = ['red', 'blue', 'green', 'purple', 'gray', 'brown', 'cyan',
                  'magenta', 'orange', 'teal']
        padding = 0.2
        bins = linspace(0, 20, 100)
        for i in range(4):
            splot = plot.get_subplot_at(i / 2, i % 2)
            splot.histogram(*histogram(ni[:, i], bins=bins))
            splot.draw_vertical_line(1)
            for j, density in enumerate(range(1, 8) + [15] + [20]):
                ni_slice = ni[:, i].compress(abs(ref_ni[:, i] - density) < padding)
                counts, bins = histogram(ni_slice, bins=bins)
                splot.histogram(counts, bins + (j / 100.), linestyle=colors[j % len(colors)])
        plot.set_ylimits_for_all(min=0.9, max=1e5)
        plot.set_xlimits_for_all(min=bins[0], max=bins[-1])
        plot.show_xticklabels_for_all([(1, 0), (0, 1)])
        plot.show_yticklabels_for_all([(1, 0), (0, 1)])
        plot.set_xlabel(r'HiSPARC detected density [\si{\per\meter\squared}]')
        plot.set_ylabel(r'Counts')
        return plot

    def plot_src_contribution_detector(self):
        plot = self.plot_contribution_detector(self.src_ni, self.src_ki)
        plot.save_as_pdf('plots/contribution_detector_scr')

    def plot_mpv_contribution_detector(self):
        plot = self.plot_contribution_detector(self.mpv_ni, self.src_ki)
        plot.save_as_pdf('plots/contribution_detector_mpv')

    def plot_cor_contribution_detector(self):
        plot = self.plot_contribution_detector(self.cor_ni, self.src_ki)
        plot.save_as_pdf('plots/contribution_detector_cor')

    def plot_kas_contribution_detector(self):
        plot = self.plot_contribution_detector(self.src_ki, self.mpv_ni)
        plot.set_xlabel(r'KASCADE predicted density [\si{\per\meter\squared}]')
        plot.save_as_pdf('plots/contribution_detector_kas')

    def plot_mpv_p_contribution_detector(self):
        plot = self.plot_contribution_detector(self.mpv_pi, self.src_ki)
        plot.save_as_pdf('plots/contribution_detector_mpv_p')

    def plot_n_histogram(self, n, ni, bins):
        """Plot histogram of detected signals"""

        plot = Plot('semilogy')
        plot.histogram(*histogram(n, bins=bins), linestyle='dotted')
        for i in range(4):
            plot.histogram(*histogram(ni[:, i], bins=bins), linestyle=COLORS[i])
        plot.set_ylimits(min=.99, max=1e4)
        plot.set_xlimits(min=bins[0], max=bins[-1])
        plot.set_ylabel(r'Counts')
        return plot

    def plot_kas_n_histogram(self):
        bins = linspace(0, 20, 300)
        plot = self.plot_n_histogram(self.src_k, self.src_ki, bins)
        plot.set_xlabel(r'Particle count')
        plot.save_as_pdf('plots/histogram_kas')

    def plot_src_n_histogram(self):
        bins = linspace(0, 4000, 200)
        plot = self.plot_n_histogram(self.src_n * SRC_PH_MPV,
                                     self.src_ni * SRC_PH_MPV, bins)
        for i, mpv in enumerate(self.mpv):
            plot.draw_vertical_line(mpv, linestyle=COLORS[i])
        plot.set_xlabel(r'Pulseheight [ADC]')
        plot.save_as_pdf('plots/histogram_src')

    def plot_mpv_n_histogram(self):
        bins = linspace(0, 20, 300)
        plot = self.plot_n_histogram(self.mpv_n, self.mpv_ni, bins)
        plot.draw_vertical_line(1)
        plot.set_xlabel(r'Particle count')
        plot.save_as_pdf('plots/histogram_mpv')

    def plot_cor_n_histogram(self):
        bins = linspace(0, 20, 300)
        plot = self.plot_n_histogram(self.cor_n, self.cor_ni, bins)
        plot.draw_vertical_line(1)
        plot.set_xlabel(r'Particle count')
        plot.save_as_pdf('plots/histogram_cor')

    def plot_mpv_p_n_histogram(self):
        bins = linspace(0, 10, 200)
        plot = self.plot_n_histogram(self.mpv_p, self.mpv_pi, bins)
        plot.draw_vertical_line(1)
        plot.set_xlabel(r'Particle count')
        plot.save_as_pdf('plots/histogram_mpv_p')

    def plot_derrivative_pmt(self):
        plot = Plot()
        plot.plot(self.lin_bins, self.dvindvout, mark=None)
        plot.set_xlimits(min=self.lin_bins[0], max=self.lin_bins[-1])
        plot.set_xlabel(r'Particle density [\si{\per\meter\squared}]')
        plot.set_ylabel(r'$\sigma V_{\mathrm{in}}\frac{\mathrm{d}V_{\mathrm{out}}}'
                        r'{\mathrm{d}V_{\mathrm{in}}}$')
        plot.save_as_pdf('plots/derrivative_pmt_saturation')


if __name__ == "__main__":
    kd = KascadeDensity()
    kd.make_plots()
