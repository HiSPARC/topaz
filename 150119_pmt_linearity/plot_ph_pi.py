from plot_results import plot_pi_ph

from artist import Plot

from . import data_nikhef_final_integral, data_nikhef_integral, data_nikhef_senstech_integral, data_senstech_integral


def plot_pi_ph(plot, test, mark='o'):
    """

    :param measured_pi: measured pulseintegral.
    :param measured_ph: measured pulseheight.

    """
    plot.scatter(test.M_PI, test.M_PH, xerr=test.M_PI_ERR, yerr=test.M_PH_ERR, mark=mark, markstyle='mark size=1.5pt')


def compared_nikhef_senstech():
    plot = Plot(height=r".67\linewidth")
    plot_pi_ph(plot, data_nikhef_final_integral, 'square')
    plot_pi_ph(plot, data_nikhef_integral, 'x')
    plot_pi_ph(plot, data_nikhef_senstech_integral, 'triangle')
    plot_pi_ph(plot, data_senstech_integral, 'o')
    plot.plot([0, 7 * data_nikhef_final_integral.RATIO], [0, 7], mark=None, linestyle='gray')
    plot.plot([0, 7 * data_nikhef_integral.RATIO], [0, 7], mark=None, linestyle='gray')
    plot.plot([0, 7 * data_nikhef_senstech_integral.RATIO], [0, 7], mark=None, linestyle='gray')
    plot.set_xlabel(r'Multiple-LED pulseintegrals [\si{\nano\volt\second}]')
    plot.set_ylabel(r'Multiple-LED pulseheights [\si{\volt}]')
    plot.set_xlimits(0, 7 * data_nikhef_final_integral.RATIO)
    plot.set_ylimits(0, 7)
    plot.save_as_pdf('plots/ph_pi_compared_nikhef_senstech')


if __name__ == "__main__":
    compared_nikhef_senstech()
