from __future__ import division

from process import get_measured_expected, determine_pi_ph_ratio
from plot_results import plot_ph, plot_pi, plot_pi_ph


led_direct_ph = [1, 225, 300, 225, 320, 250, 350, 375, 370, 340, 325,
                 300, 350, 325, 350, 350, 350, 325, 350, 350, 350,
                 330, 310, 350, 350]

led8_on_b = [1, 310, 272, 328, 332, 336, 276, 192, 352, 268, 240,
             340, 336, 268, 320, 344, 260, 312, 248, 264, 276,
             268, 160, 208, 200]

LED_PH = [1, 160, 192, 152, 240, 232, 232, 148, 352, 192, 200,
          248, 280, 222, 274, 302, 224, 308, 200, 214, 212,
          172, 136, 190, 168]

# Pulse integral not measured
LED_PI = [0] * 25

MULTI_LED = [((1, 8), 508, 0.),
             ((2, 8), 516, 0.),
             ((1, 2, 8), 688, 0.),
             ((2, 3, 8), 684, 0.),
             ((1, 2, 3, 8), 856, 0.),
             ((3, 4, 8), 752, 0.),
             ((1, 2, 3, 4, 8), 1130, 0.),
             ((1, 2, 3, 4, 5, 8), 1360, 0.),
             ((2, 3, 4, 5, 8), 1220, 0.),
             ((1, 3, 4, 5, 8), 1170, 0.),
             ((1, 2, 3, 4, 5, 8), 1360, 0.),
             ((1, 2, 3, 4, 5, 6, 8), 1620, 0.),
             ((1, 2, 3, 4, 5, 6, 7, 8), 1780, 0.),
             ((1, 2, 3, 4, 5, 6, 7, 8, 9), 1960, 0.),
             ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 2180, 0.),
             ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), 2420, 0.),
             ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), 2720, 0.),
             ((2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), 2560, 0.),
             ((3, 4, 5, 6, 7, 8, 9, 10, 11, 12), 2340, 0.),
             ((4, 5, 6, 7, 8, 9, 10, 11, 12), 2160, 0.),
             ((5, 6, 7, 8, 9, 10, 11, 12), 1940, 0.),
             ((6, 7, 8, 9, 10, 11, 12), 1700, 0.),
             ((6, 8, 9, 10, 11, 12), 1540, 0.),
             ((7, 8, 9, 10, 11, 12), 1460, 0.),
             ((8, 9, 10, 11, 12), 1320, 0.),
             ((9, 10, 11, 12), 936, 0.),
             ((10, 11, 12), 736, 0.),
             ((11, 12), 544, 0.),
             ((1, 12), 448, 0.),
             ((1, 11, 12), 704, 0.),
             ((1, 2, 11, 12), 888, 0.),
             ((1, 2, 3, 11, 12), 1060, 0.),
             ((1, 2, 3, 10, 11, 12), 1260, 0.),
             ((1, 2, 3, 5, 10, 11, 12), 1500, 0.),
             ((1, 2, 3, 5, 9, 10, 11, 12), 1700, 0.),
             ((1, 2, 3, 5, 6, 9, 10, 11, 12), 1940, 0.),
             ((1, 2, 3, 4, 5, 6, 9, 10, 11, 12), 2240, 0.),
             ((1, 2, 3, 4, 5, 9, 10, 11, 12), 1980, 0.),
             ((1, 2, 3, 4, 5, 10, 11, 12), 1780, 0.),
             ((1, 2, 3, 4, 5, 6, 9, 10, 11, 12), 2240, 0.),
             ((1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12), 2360, 0.),
             ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), 2760, 0.),
             ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13), 2840, 0.),
             ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14), 3120, 0.),
             ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15), 3400, 0.),
             ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16), 3600, 0.),
             ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17), 3880, 0.),
             ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18), 4080, 0.),
             ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19), 4280, 0.),
             ((10, 11, 12, 13, 14, 15, 16, 17, 18, 19), 2400, 0.),
             ((11, 12, 13, 14, 15, 16, 17, 18, 19), 2180, 0.),
             ((12, 13, 14, 15, 16, 17, 18, 19), 1960, 0.),
             ((13, 14, 15, 16, 17, 18, 19), 1660, 0.),
             ((14, 15, 16, 17, 18, 19), 1440, 0.),
             ((15, 16, 17, 18, 19), 1160, 0.),
             ((16, 17, 18, 19), 888, 0.),
             ((17, 18, 19), 680, 0.),
             ((18, 19), 408, 0.),
             ((20, 21, 22, 23, 24), 832, 0.),
             ((10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 3220, 0.),
             ((9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 3380, 0.),
             ((8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 3760, 0.),
             ((7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 3880, 0.),
             ((6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 4120, 0.),
             ((5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 4360, 0.),
             ((4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 4600, 0.),
             ((3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 4720, 0.),
             ((2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 4920, 0.),
             ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 5080, 0.),
             ((1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 4880, 0.),
             ((1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 4920, 0.),
             ((1, 2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 4720, 0.),
             ((1, 2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23), 4600, 0.)]

M_PI, M_PH, E_PI, E_PH = get_measured_expected(LED_PH, LED_PI, MULTI_LED)
RATIO = determine_pi_ph_ratio(LED_PI, LED_PH)


if __name__ == '__main__':
    eff_8b = [l8_on_b / led_direct_ph[8] for l8_on_b in led8_on_b]
    eff_lb = [lb / l for lb, l in zip(led_ph, led_direct_ph)]
    eff_lb_8b = [elb / e8b for elb, e8b in zip(eff_lb, eff_8b)]

    name = 'nikhef'
    plot_ph(E_PH, M_PH, name)
