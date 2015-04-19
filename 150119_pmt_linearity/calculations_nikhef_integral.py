from process import get_measured_expected, determine_pi_ph_ratio
from plot_results import plot_ph, plot_pi, plot_pi_ph


if __name__ == '__main__':

    # Only measured first 7 fibers individually
    led_ph = [1, 140, 170, 145, 225, 224, 222, 146] + [0] * (25 - 8)

    led_pi = [1, 2.17, 2.60, 2.22, 3.13, 3.33, 3.40, 2.65] + [0] * (25 - 8)

    multi_led = [((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 4590, 73.39),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19), 3820, 59.60),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15), 3100, 48.90),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9), 1730, 26.00),
                 ((1, 2, 3, 4, 5, 6), 1090, 17.16),
                 ((1, 2, 3, 4), 664, 10.62),
                 ((1, 2), 320, 5.05)]

    m_pi, m_ph, e_pi, e_ph = get_measured_expected(led_ph, led_pi, multi_led)
    ratio = determine_pi_ph_ratio(led_pi, led_ph)
    name = 'nikhef_sparse_individual'
    plot_ph(e_ph, m_ph, name)
    plot_pi(e_pi, m_pi, name)
    plot_pi_ph(m_pi, m_ph, name, ratio)
