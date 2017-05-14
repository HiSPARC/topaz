"""Energy versus detector distance for 50% efficiency

Show which energy can be efficienctly detected by two detectors separated by
distance d.

"""
from numpy import array, exp, interp, linspace, logspace, median
from scipy.stats import binned_statistic

from artist import Plot

from sapphire.simulations.ldf import EllipsLdf, KascadeLdf, NkgLdf


def P_0(ldf, r, N):
    """Probability that a detector sees no particles for given density"""

    if isinstance(ldf, EllipsLdf):
        return exp(-0.5 * ldf.calculate_ldf_value(r, 0, N))
    else:
        return exp(-0.5 * ldf.calculate_ldf_value(r, N))


def P_2(ldf, r=10, N=10**4.07):
    """Probability that two detectors have at least one particle"""

    return (1 - P_0(ldf, r, N)) ** 2


def energy_to_size(E, a, b=1.):
    """Relation between shower size and energy

    size = 10 ** (energy ** b - a)

    :param E: log10 of the energy in eV.

    """
    return 10 ** (E ** b - a)


def plot_E_d_P(ldf):
    energies = linspace(13, 21, 100)
    sizes = energy_to_size(energies, 13.3, 1.07)
    core_distances = logspace(-1, 4.5, 100)

    probabilities = []
    for size in sizes:
        prob_temp = []
        for distance in core_distances:
            prob_temp.append(P_2(ldf, distance, size))
        probabilities.append(prob_temp)
    probabilities = array(probabilities)

    plot = Plot('semilogx')

    low = []
    mid = []
    high = []
    for p in probabilities:
        # Using `1 -` to ensure x (i.e. p) is increasing.
        low.append(interp(1 - 0.10, 1 - p, core_distances))
        mid.append(interp(1 - 0.50, 1 - p, core_distances))
        high.append(interp(1 - 0.90, 1 - p, core_distances))
    plot.plot(low, energies, linestyle='densely dotted', mark=None)
    plot.plot(mid, energies, linestyle='densely dashed', mark=None)
    plot.plot(high, energies, mark=None)
    plot.set_ylimits(13, 20)
    plot.set_xlimits(1., 1e4)

    plot.set_xlabel(r'Core distance [\si{\meter}]')
    plot.set_ylabel(r'Energy [log10(E/\si{\eV})]')
    plot.save_as_pdf('efficiency_distance_energy_' + ldf.__class__.__name__)


if __name__ == "__main__":
    for ldf in [NkgLdf(), KascadeLdf(), EllipsLdf()]:
        plot_E_d_P(ldf)
