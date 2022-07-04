from numpy import append, arange, cumsum, exp, histogram, inf, interp, searchsorted, where
from scipy.integrate import quad
from scipy.misc import factorial

from artist import Plot

from kascade_density import KascadeDensity

MIN = 0
MAX = 300
STEP = 0.01
SMALL_STEP = STEP  # / 10.
LAMBDA = arange(MIN, MAX, SMALL_STEP)

KD = KascadeDensity()
KD_probability, KD_bins = histogram(KD.src_k, bins=arange(MIN, MAX, STEP),
                                    density=True)
# To prevent bad index when using searchsorted add some zeros
KD_probability = append(KD_probability, [0., 0.])


def poisson(lamb, k):
    """Poisson probability for detecting k particles given density lamb

    P(k|lamb)

    :param lamb: the actual expected number of particles
    :param k: the detected number of particles

    """
    return lamb ** k * exp(-lamb) / factorial(k)


def p_lambda(lamb):
    """The probability to encounter a particle density

    P(lamb)
    Based on KASCADE data.

    :param lamb: the actual expected number of particles

    """
    idx = searchsorted(KD_bins, lamb)
    return where(idx >= len(KD_probability) - 1, 0., KD_probability[idx])


def integrand(lamb, k):
    """Probabilities to be integrated over

    P(k|lamb) P(lamb)

    :param lamb: the actual expected number of particles
    :param k: the detected number of particles

    """
    return poisson(lamb, k) * p_lambda(lamb)


def normalization(k):
    """Normalization factor

    :param k: the detected number of particles

    """
    return quad(integrand, 0, inf, args=(k))[0]


def density_probability(lamb, k):
    """Probability for density lamb was responsible for detection of k particles

    P(lamb|k)

    :param lamb: the actual expected number of particles
    :param k: the detected number of particles

    """
    return poisson(lamb, k) * p_lambda(lamb) / normalization(k)


def mean_density_for_n(k):
    """Calculate expected mean density given a detected number of particles

    :param k: the detected number of particles

    """
    return sum(LAMBDA * density_probability(LAMBDA, k)) * SMALL_STEP


def most_probable_density_for_n(k):
    """Calculate most probable density given a detected number of particles

    :param k: the detected number of particles

    """
    return LAMBDA[density_probability(LAMBDA, k).argmax()]


def median_density_for_n(k):
    """Calculate median density given a detected number of particles

    :param k: the detected number of particles

    """
    cumulative_prob = cumsum(density_probability(LAMBDA, k) * SMALL_STEP)
    return LAMBDA[searchsorted(cumulative_prob, 0.5)]


def percentile_low_density_for_n(k):
    """Calculate lower percentile density given a detected number of particles

    :param k: the detected number of particles

    """
    cumulative_prob = cumsum(density_probability(LAMBDA, k) * SMALL_STEP)
    return interp(0.25, cumulative_prob, LAMBDA)


def percentile_high_density_for_n(k):
    """Calculate upper percentile density given a detected number of particles

    :param k: the detected number of particles

    """
    cumulative_prob = cumsum(density_probability(LAMBDA, k) * SMALL_STEP)
    return interp(0.75, cumulative_prob, LAMBDA)


def plot_contributions():
    colors = ['red', 'blue', 'green', 'purple', 'gray', 'brown', 'cyan',
              'magenta', 'orange', 'teal']
    lamb = arange(MIN, MAX, 0.1)
    plot = Plot('semilogy')

    for j, k in enumerate(list(range(1, 8)) + [15] + [20]):
        ks = [k]  # arange(k - 0.5, k + 0.5, 0.2)
        p = sum(density_probability(lamb, ki) for ki in ks) / len(ks)
        plot.plot(lamb, p, linestyle=colors[j % len(colors)], mark=None)
    plot.set_ylimits(min=0.01)
    plot.set_xlimits(0, 20)
    plot.set_xlabel('Expected actual number of particles')
    plot.set_ylabel('Probability')
    plot.save_as_pdf('plots/poisson_distributions')


def plot_ranges():
    k = arange(26)
    p_low = [percentile_low_density_for_n(ki) for ki in k]
    p_median = [median_density_for_n(ki) for ki in k]
    p_mean = [mean_density_for_n(ki) for ki in k]
#     p_mpv = [most_probable_density_for_n(ki) for ki in k]
    p_high = [percentile_high_density_for_n(ki) for ki in k]
    plot = Plot(height=r'\defaultwidth')
    plot.plot([0, 1.5 * max(k)], [0, 1.5 * max(k)], mark=None, linestyle='dashed')
    plot.scatter(k, p_median)
#     plot.plot(k, p_mean, mark=None, linestyle='green')
#     plot.plot(k, p_mpv, mark=None, linestyle='red')
    plot.shade_region(k, p_low, p_high)
    plot.set_xlimits(min(k) - 0.05 * max(k), 1.05 * max(k))
    plot.set_ylimits(min(k) - 0.05 * max(k), 1.05 * max(k))
    plot.set_axis_equal()
    plot.set_xlabel('Detected number of particles')
    plot.set_ylabel('Expected actual number of particles')
    plot.save_as_pdf('plots/poisson_ranges')


def make_plots():
    plot_contributions()
    plot_ranges()


if __name__ == "__main__":
    make_plots()
