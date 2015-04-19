from artist import Plot


def plot_ph(expected, measured, name):
    """

    :param expected: expected pulseheight from sum individual measurements.
    :param measured: measured pulseheight.
    :param name: name for output

    """
    graph = Plot(height=r".67\linewidth")
    graph.scatter(expected, measured)
    graph.plot([0, 6000], [0, 6000], mark=None)
    graph.set_xlabel('Sum individual LED pulseheights [mV]')
    graph.set_ylabel('Multiple-LED pulseheight [mV]')
    graph.set_xlimits(0, 6000)
    graph.set_ylimits(0, 6000)
    graph.save_as_pdf(name + '_ph')


def plot_pi(expected, measured, name):
    """

    :param expected: expected pulseintegral from sum individual measurements.
    :param measured: measured pulseintegral.
    :param name: name for output

    """
    graph = Plot(height=r".67\linewidth")
    graph.scatter(expected, measured)
    graph.plot([0, 120], [0, 120], mark=None)
    graph.set_xlabel('Sum individual LED pulseintegrals [nVs]')
    graph.set_ylabel('Multiple-LED pulseintegrals [nVs]')
    graph.set_xlimits(0, 120)
    graph.set_ylimits(0, 120)
    graph.save_as_pdf(name + '_pi')


def plot_pi_ph(measured_pi, measured_ph, name, ratio):
    """

    :param measured_pi: measured pulseintegral.
    :param measured_ph: measured pulseheight.
    :param name: name for output
    :param ratio: pi / ph ratio (from individual fibers, before saturation)

    """
    graph = Plot(height=r".67\linewidth")
    graph.scatter(measured_pi, measured_ph)
    graph.plot([0, 6000 * ratio], [0, 6000], mark=None)
    graph.set_xlabel('Multiple-LED pulseintegrals [nVs]')
    graph.set_ylabel('Multiple-LED pulseheights [mV]')
    graph.set_xlimits(0, 6000 * ratio)
    graph.set_ylimits(0, 6000)
    graph.save_as_pdf(name + '_pi_ph')
