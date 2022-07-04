from plot_results import plot_ph, plot_pi, plot_pi_ph
from process import determine_pi_ph_ratio, get_measured_expected

# Only measured first 7 fibers individually
LED_PH = [1, 140, 170, 145, 225, 224, 222, 146] + [0] * (25 - 8)

LED_PH_ERR = [0] + [5] * 7 + [0] * (25 - 8)

LED_PI = [1, 2.17, 2.60, 2.22, 3.13, 3.33, 3.40, 2.65] + [0] * (25 - 8)

LED_PI_ERR = [0] + [0.1] * 7 + [0] * (25 - 8)

MULTI_LED = [
    ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 4590, 73.39),
    ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19), 3820, 59.60),
    ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15), 3100, 48.90),
    ((1, 2, 3, 4, 5, 6, 7, 8, 9), 1730, 26.00),
    ((1, 2, 3, 4, 5, 6), 1090, 17.16),
    ((1, 2, 3, 4), 664, 10.62),
    ((1, 2), 320, 5.05),
]

M_PH, M_PH_ERR, M_PI, M_PI_ERR, E_PH, E_PH_ERR, E_PI, E_PI_ERR = get_measured_expected(
    LED_PH, LED_PH_ERR, LED_PI, LED_PI_ERR, MULTI_LED
)
RATIO = determine_pi_ph_ratio(LED_PI, LED_PH)


if __name__ == '__main__':
    name = 'nikhef_sparse_individual'
    plot_ph(E_PH, M_PH, name, E_PH_ERR, M_PH_ERR)
    plot_pi(E_PI, M_PI, name, E_PI_ERR, M_PI_ERR)
    plot_pi_ph(M_PI, M_PH, name, RATIO, M_PI_ERR, M_PH_ERR)
