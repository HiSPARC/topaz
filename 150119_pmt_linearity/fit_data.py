from numpy import linspace

from artist import Plot

from fit_curve import fit_curve, ice_cube_pmt_p1, P1
from data_senstech_integral import M_PH as senstech_m_ph, E_PH as senstech_e_ph
from data_nikhef_final_integral import M_PH as nikhef_m_ph, E_PH as nikhef_e_ph


FIT = (r"$\mathrm{ln}V_{\mathrm{in}}=\mathrm{ln}V + "
       r"\frac{p_0\left(\frac{V}{p_1}\right)^{p_2}}"
       r"{\left(1-\frac{V}{p_1}\right)^{\frac{1}{4}}}$"
       r", \scriptsize{($p_0=%.1f$, $p_1=%d$, $p_2=%.1f$)}")


def plot_compared():
    popt, perr = fit_curve(senstech_m_ph, senstech_e_ph)
    fit = FIT % (popt[0], P1, popt[1])

    plot = Plot(width=r'.67\linewidth', height=r'.67\linewidth')
    plot.set_label(fit, location='upper left')
    plot.scatter(senstech_e_ph, senstech_m_ph, mark='*')
    plot.scatter(nikhef_e_ph, nikhef_m_ph, mark='o')
    inputs = linspace(min(senstech_m_ph), max(senstech_m_ph), 500)
    plot.plot(ice_cube_pmt_p1(inputs, *popt), inputs, mark=None)
    plot.plot([0, 6], [0, 6], mark=None, linestyle='gray')
    plot.set_xlimits(0, 6)
    plot.set_ylimits(0, 6)
    plot.set_axis_equal()
    plot.set_xlabel(r'Sum individual LED pulseheights [\si{\volt}]')
    plot.set_ylabel(r'Multiple-LED pulseheight [\si{\volt}]')
    plot.save_as_pdf('plots/linearity_compared')


def plot_fit_pulseheight(ph_in, ph_out):

    popt, perr = fit_curve(ph_out, ph_in)
    fit = FIT % (popt[0], P1, popt[1])

    outputs = linspace(0, max(ph_out) + 0.2, 500)

    plot = Plot(width=r'.67\linewidth', height=r'.67\linewidth')
    plot.scatter(ph_in, ph_out, mark='o')

    plot.plot(ice_cube_pmt_p1(outputs, *popt), outputs, mark=None)

    plot.plot([0, 6], [0, 6], mark=None, linestyle='gray')
    plot.set_xlimits(0, 6)
    plot.set_ylimits(0, 6)
    plot.set_axis_equal()

    plot.set_xlabel(r'Sum individual LED pulseheights [\si{\volt}]')
    plot.set_ylabel(r'Multiple-LED pulseheight [\si{\volt}]')

    return plot


def plot_senstech_integral():
    plot = plot_fit_pulseheight(senstech_e_ph, senstech_m_ph)
    plot.save_as_pdf('plots/ph_sentech_integral')


def plot_nikhef_final_integral():
    plot = plot_fit_pulseheight(nikhef_e_ph, nikhef_m_ph)
    plot.save_as_pdf('plots/ph_nikhef_final_integral')


def plot_fitted_curves():
    plot_senstech_integral()
    plot_nikhef_final_integral()

if __name__ == '__main__':
    plot_fitted_curves()
