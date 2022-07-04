""" Process LED results for further analysis

Convert pulseheights from mV to V.

"""


from numpy import mean, sqrt


def get_measured_expected(led_ph, led_ph_err, led_pi, led_pi_err, multi_led):
    """

    :param led_ph: individual fiber measurements of pulseheight
    :param led_ph_err: error on measurement of individual pulseheights
    :param led_pi: individual fiber measurements of pulseintegral
    :param led_ph_err: error on measurement of individual pulseintegral
    :param multi_led: tuple of fibers numbers, measured pulseheight
                      and pulseintegral

    """
    measured_ph = []
    measured_ph_err = []
    measured_pi = []
    measured_pi_err = []
    expected_ph = []
    expected_ph_err = []
    expected_pi = []
    expected_pi_err = []
    for fibers, ph, pi in multi_led:
        # Convert pulseheights to V
        measured_ph.append(ph / 1e3)
        measured_ph_err.append(2 * sqrt(ph) / 1e3)  # 5% error?
        measured_pi.append(pi)
        measured_pi_err.append(0.05 * pi)  # 5% error?
        expected_ph.append(sum(led_ph[fiber] for fiber in fibers) / 1e3)
        expected_ph_err.append(sqrt(sum(led_ph_err[fiber] ** 2 for fiber in fibers)) / 1e3)
        expected_pi.append(sum(led_pi[fiber] for fiber in fibers))
        expected_pi_err.append(sqrt(sum(led_pi_err[fiber] ** 2 for fiber in fibers)))

    #     print expected_ph_err
    #     print expected_ph
    return (
        measured_ph,
        measured_ph_err,
        measured_pi,
        measured_pi_err,
        expected_ph,
        expected_ph_err,
        expected_pi,
        expected_pi_err,
    )


def determine_pi_ph_ratio(led_pi, led_ph):
    """Calculate ratio between pulseintegral and pulseheight

    :param led_ph: individual fiber measurements of pulseheight
    :param led_pi: individual fiber measurements of pulseintegral

    """
    ratio = mean([pi / (ph / 1e3) for ph, pi in zip(led_ph[1:], led_pi[1:]) if not (pi == 0.0 or ph == 0.0)])
    return ratio
