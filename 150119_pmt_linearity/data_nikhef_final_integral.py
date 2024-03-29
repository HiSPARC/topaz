from plot_results import plot_ph, plot_pi, plot_pi_ph
from process import determine_pi_ph_ratio, get_measured_expected

LED_PH = [
    1,
    155,
    193,
    155,
    219,
    233,
    239,
    169,
    322,
    160,
    230,
    240,
    285,
    208,
    222,
    262,
    174,
    319,
    168,
    210,
    216,
    162,
    130,
    213,
    166,
]

LED_PH_ERR = [0] + [5] * 24

LED_PI = [
    1,
    2.43,
    3.15,
    2.48,
    3.18,
    3.60,
    3.70,
    2.72,
    5.09,
    2.49,
    3.66,
    3.57,
    4.51,
    3.15,
    3.49,
    3.81,
    2.64,
    4.93,
    2.72,
    3.13,
    3.27,
    2.55,
    2.07,
    3.40,
    2.93,
]

LED_PI_ERR = [0] + [0.1] * 24

MULTI_LED = [
    ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 5050, 86.50),
    ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22), 4723, 73.61),
    ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20), 4396, 68.58),
    ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18), 3950, 61.43),
    ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16), 3560, 55.46),
    ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14), 3150, 49.00),
    ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), 2686, 42.50),
    ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 2140, 34.34),
    ((1, 2, 3, 4, 5, 6, 7, 8), 1746, 28.13),
    ((1, 2, 3, 4, 5, 6), 1224, 20.36),
    ((1, 2, 3, 4), 716, 11.43),
    ((1, 2), 318, 5.00),
]

M_PH, M_PH_ERR, M_PI, M_PI_ERR, E_PH, E_PH_ERR, E_PI, E_PI_ERR = get_measured_expected(
    LED_PH, LED_PH_ERR, LED_PI, LED_PI_ERR, MULTI_LED
)
RATIO = determine_pi_ph_ratio(LED_PI, LED_PH)


if __name__ == '__main__':
    name = 'nikhef_final'
    plot_ph(E_PH, M_PH, name, E_PH_ERR, M_PH_ERR)
    plot_pi(E_PI, M_PI, name, E_PI_ERR, M_PI_ERR)
    plot_pi_ph(M_PI, M_PH, name, RATIO, M_PI_ERR, M_PH_ERR)
