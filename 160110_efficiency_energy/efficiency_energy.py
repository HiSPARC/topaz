"""Energy versus detector distance for 50% efficiency

Show which energy can be efficienctly detected by two detectors separated by
distance d.

"""
from numpy import arange, array, exp

from artist import Plot

from sapphire.simulations.ldf import NkgLdf, KascadeLdf


def P_0(ldf, r, N):
    return exp(-0.5 * ldf.calculate_ldf_value(r, N))


def P_2(ldf, r=10, N=10**4.07):
    return (1 - P_0(ldf, r, N)) ** 2


def energy_to_size(E, a, b=1.):
    """Relation between shower size and energy

    size = 10 ** (energy ** b - a)

    :param E: log10 of the energy in eV.

    """
    return 10 ** (E ** b - a)


def plot_E_d_P(ldf):
    energies = arange(13, 20.00001, .01)
    sizes = energy_to_size(energies, 13.3, 1.07)
    size_centers = (sizes[1:] + sizes[:-1]) / 2
    log_distances = arange(0, 4.0001, .01)
    core_distances = (10 ** log_distances) / 2.
    distance_centers = (core_distances[1:] + core_distances[:-1]) / 2

    probabilities = []
    for size in size_centers:
        prob_temp = []
        for distance in distance_centers:
            prob_temp.append(P_2(ldf, distance, size))
        probabilities.append(prob_temp)
    probabilities = array(probabilities)

    plot = Plot()
    plot.histogram2d(probabilities.T, log_distances, energies, bitmap=True)
    plot.set_xlabel(r'Distance [log10(d/\si{\meter})]')
    plot.set_ylabel(r'Energy [log10(E/\si{\eV})]')
    plot.save_as_pdf('efficiency_distance_energy_' + ldf.__class__.__name__)


if __name__ == "__main__":
    for ldf in [NkgLdf(), KascadeLdf()]:
        plot_E_d_P(ldf)
