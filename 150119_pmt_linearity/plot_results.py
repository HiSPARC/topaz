from numpy import linspace

from artist import MultiPlot

from fit_curve import fit_curve, fit_function


def plot_fit(plot, expected, measured, measured_err=[]):
    """

    :param plot: an artist.Plot object.
    :param expected: expected values from sum individual measurements.
    :param measured: measured values.

    """
    popt, perr = fit_curve(measured, expected, p0=(1.0, 1.1, 1.0), err=measured_err)
    print(popt, perr)
    outputs = linspace(0.01, max(measured) + 0.2, 500)
    # Plot fit line
    splot = plot.get_subplot_at(0, 0)
    splot.plot(outputs, fit_function(outputs, *popt), mark=None)
    # Plot residuals
    splot = plot.get_subplot_at(1, 0)
    splot.scatter(measured, expected - fit_function(measured, *popt), markstyle='mark size=1pt')
    splot.draw_horizontal_line(0, linestyle='gray')
    splot.set_axis_options('height={2.5cm}')


#     splot.set_xlimits(-15e-2, 15e-2)


def plot_ph(expected, measured, name, expected_err=[], measured_err=[]):
    """

    :param expected: expected pulseheight from sum individual measurements.
    :param measured: measured pulseheight.
    :param name: name for output

    """
    plot = MultiPlot(2, 1, height=r".67\linewidth")
    splot = plot.get_subplot_at(0, 0)
    splot.scatter(measured, expected, xerr=measured_err, yerr=expected_err, markstyle='mark size=1pt')
    splot.plot([0, 6], [0, 6], mark=None, linestyle='gray')
    plot_fit(plot, expected, measured, measured_err)

    splot.set_ylabel(r'Sum individual LED pulseheights [\si{\volt}]')
    splot.set_ylimits(0, 5.5)
    splot.set_axis_equal()

    splot = plot.get_subplot_at(1, 0)
    splot.set_xlabel(r'Multiple-LED pulseheight [\si{\volt}]')

    plot.set_xlimits_for_all(None, 0, 5.5)
    plot.show_xticklabels(1, 0)
    plot.show_yticklabels_for_all(None)

    plot.save_as_pdf('plots/data_ph_' + name)


def plot_pi(expected, measured, name, expected_err=[], measured_err=[]):
    """

    :param expected: expected pulseintegral from sum individual measurements.
    :param measured: measured pulseintegral.
    :param name: name for output

    """
    plot = MultiPlot(2, 1, height=r".67\linewidth")
    splot = plot.get_subplot_at(0, 0)
    splot.scatter(measured, expected, xerr=measured_err, yerr=expected_err, markstyle='mark size=1pt')
    splot.plot([0, 120], [0, 120], mark=None, linestyle='gray')
    plot_fit(plot, expected, measured, measured_err)

    splot.set_ylabel(r'Sum individual LED pulseintegrals [\si{\nano\volt\second}]')
    splot.set_ylimits(0, 60)
    splot.set_axis_equal()

    splot = plot.get_subplot_at(1, 0)
    splot.set_xlabel(r'Multiple-LED pulseintegrals [\si{\nano\volt\second}]')

    plot.set_xlimits_for_all(None, 0, 60)
    plot.show_xticklabels(1, 0)
    plot.show_yticklabels_for_all(None)
    plot.save_as_pdf('plots/data_pi_' + name)


def plot_pi_ph(measured_pi, measured_ph, name, ratio, pi_err=[], ph_err=[]):
    """

    :param measured_pi: measured pulseintegral.
    :param measured_ph: measured pulseheight.
    :param name: name for output
    :param ratio: pi / ph ratio (from individual fibers, before saturation)

    """
    plot = MultiPlot(2, 1, height=r".67\linewidth")

    splot = plot.get_subplot_at(0, 0)
    splot.scatter(measured_ph, measured_pi / ratio, xerr=ph_err, yerr=pi_err / ratio, markstyle='mark size=1pt')
    splot.plot([0, 6], [0, 6], mark=None, linestyle='gray')

    plot_fit(plot, measured_pi / ratio, measured_ph, pi_err)

    splot.set_ylabel(r'Multiple-LED pulseintegrals [\si{\nano\volt\second}]')
    splot.set_ylimits(0, 5.5)

    splot = plot.get_subplot_at(1, 0)
    splot.set_xlabel(r'Multiple-LED pulseheights [\si{\volt}]')

    plot.set_xlimits_for_all(None, 0, 5.5)
    plot.show_yticklabels_for_all(None)
    plot.show_xticklabels(1, 0)
    plot.save_as_pdf('plots/data_piph_' + name)
