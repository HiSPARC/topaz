from artist import Plot


def plot_ph(expected, measured, name, expected_err=[], measured_err=[]):
    """

    :param expected: expected pulseheight from sum individual measurements.
    :param measured: measured pulseheight.
    :param name: name for output

    """
    graph = Plot(height=r".67\linewidth")
    graph.scatter(expected, measured, xerr=expected_err, yerr=measured_err,
                  markstyle='mark size=1.5pt')
    graph.plot([0, 6], [0, 6], mark=None)
    graph.set_xlabel(r'Sum individual LED pulseheights [\si{\volt}]')
    graph.set_ylabel(r'Multiple-LED pulseheight [\si{\volt}]')
    graph.set_xlimits(0, 6)
    graph.set_ylimits(0, 6)
    graph.save_as_pdf('result_ph_' +name)


def plot_pi(expected, measured, name, expected_err=[], measured_err=[]):
    """

    :param expected: expected pulseintegral from sum individual measurements.
    :param measured: measured pulseintegral.
    :param name: name for output

    """
    graph = Plot(height=r".67\linewidth")
    graph.scatter(expected, measured, xerr=expected_err, yerr=measured_err,
                  markstyle='mark size=1.5pt')
    graph.plot([0, 120], [0, 120], mark=None)
    graph.set_xlabel(r'Sum individual LED pulseintegrals [\si{\nano\volt\second}]')
    graph.set_ylabel(r'Multiple-LED pulseintegrals [\si{\nano\volt\second}]')
    graph.set_xlimits(0, 120)
    graph.set_ylimits(0, 120)
    graph.save_as_pdf('result_pi_' +name)


def plot_pi_ph(measured_pi, measured_ph, name, ratio, pi_err=[], ph_err=[]):
    """

    :param measured_pi: measured pulseintegral.
    :param measured_ph: measured pulseheight.
    :param name: name for output
    :param ratio: pi / ph ratio (from individual fibers, before saturation)

    """
    graph = Plot(height=r".67\linewidth")
    graph.scatter(measured_pi, measured_ph, xerr=pi_err, yerr=ph_err,
                  markstyle='mark size=1.5pt')
    graph.plot([0, 6 * ratio], [0, 6], mark=None)
    graph.set_xlabel(r'Multiple-LED pulseintegrals [\si{\nano\volt\second}]')
    graph.set_ylabel(r'Multiple-LED pulseheights [\si{\volt}]')
    graph.set_xlimits(0, 6 * ratio)
    graph.set_ylimits(0, 6)
    graph.save_as_pdf('result_piph_' +name)
