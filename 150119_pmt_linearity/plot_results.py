from numpy import linspace

from artist import Plot

from fit_curve import fit_curve, ice_cube_pmt_p1, P1


FIT = (r"$\mathrm{ln}V_{\mathrm{in}}=\mathrm{ln}V + "
       r"\frac{p_0\left(\frac{V}{p_1}\right)^{p_2}}"
       r"{\left(1-\frac{V}{p_1}\right)^{\frac{1}{4}}}$"
       r", \scriptsize{($p_0=%.1f$, $p_1=%d$, $p_2=%.1f$)}")


def plot_fit(plot, expected, measured, expected_err=[]):
    """

    :param plot: an artist.Plot object.
    :param expected: expected values from sum individual measurements.
    :param measured: measured values.

    """
    popt, perr = fit_curve(measured, expected, expected_err)
    print perr
    fit = FIT % (popt[0], P1, popt[1])
    plot.set_label(fit, location='upper left')
    outputs = linspace(0, max(measured) + 0.2, 500)
    plot.plot(ice_cube_pmt_p1(outputs, *popt), outputs, mark=None)


def plot_ph(expected, measured, name, expected_err=[], measured_err=[]):
    """

    :param expected: expected pulseheight from sum individual measurements.
    :param measured: measured pulseheight.
    :param name: name for output

    """
    plot = Plot(height=r".67\linewidth")
    plot.scatter(expected, measured, xerr=expected_err, yerr=measured_err,
                 markstyle='mark size=1pt')
    plot_fit(plot, expected, measured, expected_err)
    plot.plot([0, 6], [0, 6], mark=None, linestyle='gray')
    plot.set_xlabel(r'Sum individual LED pulseheights [\si{\volt}]')
    plot.set_ylabel(r'Multiple-LED pulseheight [\si{\volt}]')
    plot.set_xlimits(0, 6)
    plot.set_ylimits(0, 6)
    plot.set_axis_equal()
    plot.save_as_pdf('plots/data_ph_' +name)


def plot_pi(expected, measured, name, expected_err=[], measured_err=[]):
    """

    :param expected: expected pulseintegral from sum individual measurements.
    :param measured: measured pulseintegral.
    :param name: name for output

    """
    plot = Plot(height=r".67\linewidth")
    plot.scatter(expected, measured, xerr=expected_err, yerr=measured_err,
                 markstyle='mark size=1pt')
    plot_fit(plot, expected, measured)
    plot.plot([0, 120], [0, 120], mark=None, linestyle='gray')
    plot.set_xlabel(r'Sum individual LED pulseintegrals [\si{\nano\volt\second}]')
    plot.set_ylabel(r'Multiple-LED pulseintegrals [\si{\nano\volt\second}]')
    plot.set_xlimits(0, 120)
    plot.set_ylimits(0, 120)
    plot.set_axis_equal()
    plot.save_as_pdf('plots/data_pi_' +name)


def plot_pi_ph(measured_pi, measured_ph, name, ratio, pi_err=[], ph_err=[]):
    """

    :param measured_pi: measured pulseintegral.
    :param measured_ph: measured pulseheight.
    :param name: name for output
    :param ratio: pi / ph ratio (from individual fibers, before saturation)

    """
    plot = Plot(height=r".67\linewidth")
    plot.scatter(measured_pi, measured_ph, xerr=pi_err, yerr=ph_err,
                 markstyle='mark size=1pt')
    plot.plot([0, 6 * ratio], [0, 6], mark=None, linestyle='gray')
    plot.set_xlabel(r'Multiple-LED pulseintegrals [\si{\nano\volt\second}]')
    plot.set_ylabel(r'Multiple-LED pulseheights [\si{\volt}]')
    plot.set_xlimits(0, 6 * ratio)
    plot.set_ylimits(0, 6)
    plot.save_as_pdf('plots/data_piph_' +name)
