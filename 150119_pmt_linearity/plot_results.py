from numpy import linspace

from artist import Plot, MultiPlot

from fit_curve import fit_curve, fit_function


def plot_fit(plot, expected, measured, expected_err=[]):
    """

    :param plot: an artist.Plot object.
    :param expected: expected values from sum individual measurements.
    :param measured: measured values.

    """
    popt, perr = fit_curve(measured, expected)#, expected_err)
    print popt, perr
    outputs = linspace(0.01, max(measured) + 0.2, 500)
    splot = plot.get_subplot_at(0, 0)
    splot.plot(fit_function(outputs, *popt), outputs, mark=None)
    splot = plot.get_subplot_at(0, 1)
    splot.scatter(expected - fit_function(measured, *popt), measured, markstyle='mark size=1pt')
    splot.draw_vertical_line(0, linestyle='gray')
    splot.set_axis_options('width={2.5cm},scaled ticks=base 10:2')
#     splot.set_xlimits(-15e-2, 15e-2)


def plot_ph(expected, measured, name, expected_err=[], measured_err=[]):
    """

    :param expected: expected pulseheight from sum individual measurements.
    :param measured: measured pulseheight.
    :param name: name for output

    """
    plot = MultiPlot(1, 2, height=r".67\linewidth")
    splot = plot.get_subplot_at(0, 0)
    splot.scatter(expected, measured, xerr=expected_err, yerr=measured_err,
                 markstyle='mark size=1pt')
    splot.plot([0, 6], [0, 6], mark=None, linestyle='gray')
    splot.set_ylabel(r'Multiple-LED pulseheight [\si{\volt}]')
    splot.set_xlabel(r'Sum individual LED pulseheights [\si{\volt}]')
    splot.set_xlimits(0, 5.5)
    splot.set_axis_equal()
    plot_fit(plot, expected, measured, expected_err)
    plot.set_ylimits_for_all(None, 0, 5.5)
    plot.show_xticklabels_for_all(None)
    plot.show_yticklabels(0, 0)

    plot.save_as_pdf('plots/data_ph_' +name)


def plot_pi(expected, measured, name, expected_err=[], measured_err=[]):
    """

    :param expected: expected pulseintegral from sum individual measurements.
    :param measured: measured pulseintegral.
    :param name: name for output

    """
    plot = MultiPlot(1, 2, height=r".67\linewidth")
    splot = plot.get_subplot_at(0, 0)
    splot.scatter(expected, measured, xerr=expected_err, yerr=measured_err,
                  markstyle='mark size=1pt')
    splot.plot([0, 120], [0, 120], mark=None, linestyle='gray')
    splot.set_xlabel(r'Sum individual LED pulseintegrals [\si{\nano\volt\second}]')
    splot.set_ylabel(r'Multiple-LED pulseintegrals [\si{\nano\volt\second}]')
    splot.set_xlimits(0, 105)
    splot.set_axis_equal()
    plot_fit(plot, expected, measured, expected_err)
    plot.set_ylimits_for_all(None, 0, 105)
    plot.show_xticklabels_for_all(None)
    plot.show_yticklabels(0, 0)
    plot.save_as_pdf('plots/data_pi_' +name)


def plot_pi_ph(measured_pi, measured_ph, name, ratio, pi_err=[], ph_err=[]):
    """

    :param measured_pi: measured pulseintegral.
    :param measured_ph: measured pulseheight.
    :param name: name for output
    :param ratio: pi / ph ratio (from individual fibers, before saturation)

    """
    plot = MultiPlot(1, 2, height=r".67\linewidth")
    splot = plot.get_subplot_at(0, 0)
    splot.scatter(measured_pi / ratio, measured_ph, xerr=pi_err / ratio,
                  yerr=ph_err, markstyle='mark size=1pt')
    splot.plot([0, 6], [0, 6], mark=None, linestyle='gray')
    splot.set_xlabel(r'Multiple-LED pulseintegrals [\si{\nano\volt\second}]')
    splot.set_ylabel(r'Multiple-LED pulseheights [\si{\volt}]')
    splot.set_xlimits(0, 5.5)
    plot_fit(plot, measured_pi / ratio, measured_ph, pi_err)
    plot.set_ylimits_for_all(None, 0, 5.5)
    plot.show_xticklabels_for_all(None)
    plot.show_yticklabels(0, 0)
    plot.save_as_pdf('plots/data_piph_' +name)
