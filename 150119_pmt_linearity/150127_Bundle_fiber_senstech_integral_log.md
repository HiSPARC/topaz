# PMT linearity bundle cap log


Setup
-----

Test on 2015/1/27

Sens Tech PMT with SN 30449.

PMT voltage 893 V.

Bundle of many fibers in custom drilled cap.

Now performed with a different scope that can measure the pulse integral.

Oscilloscope LeCroy 434:
Acquire     Average 100
Measure     Ch1 Pk-Pk
Measure     Ch1 Area
Trigger     Ch4


Check combination of LED and Bundle fibers
------------------------------------------

    LED + Bundle Fiber    Pulseheight [mV]  Integral [nVs]
    #01                   150               1.68
    #02                   220               2.44
    #03                   156               1.80
    #04                   225               2.43
    #05                   230               2.56
    #06                   230               2.57
    #07                   182               2.18
    #08                   299               3.32
    #09                   163               1.82
    #10                   202               2.46
    #11                   220               2.46
    #12                   250               3.00
    #13                   202               2.36
    #14                   244               2.87
    #15                   240               2.56
    #16                   190               2.22
    #17                   240               2.79
    #18                   159               1.84
    #19                   196               2.20
    #20                   180               2.05
    #21                   182               2.00
    #22                   160               1.83
    #23                   210               2.47
    #24                   202               2.70


Multiple fibers combined
------------------------

Connected multiple fibers simultaneously to add signals.

LED fibers are connected to the Bundle fiber of the same number.

    Fibers                                                          Pulseheight [mV]    Integral [nVs]
    23 24                                                           325                 4.45
    22 23 24                                                        550                 6.55
    21 22 23 24                                                     730                 8.61
    20 21 22 23 24                                                  860                 10.60
    19 20 21 22 23 24                                               1000                12.21
    18 19 20 21 22 23 24                                            1120                15.20
    17 18 19 20 21 22 23 24                                         1267                17.66
    16 17 18 19 20 21 22 23 24                                      1339                19.12
    15 16 17 18 19 20 21 22 23 24                                   1453                21.00
    14 15 16 17 18 19 20 21 22 23 24                                1545                23.00
    13 14 15 16 17 18 19 20 21 22 23 24                             1605                24.33
    12 13 14 15 16 17 18 19 20 21 22 23 24                          1712                26.55
    11 12 13 14 15 16 17 18 19 20 21 22 23 24                       1776                28.04
    10 11 12 13 14 15 16 17 18 19 20 21 22 23 24                    1844                29.46
    9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24                  1877                30.66
    8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24                1960                32.23
    7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24              1983                33.15
    6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24            2036                34.30
    4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24        2097                36.25
    2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24    2150                38.15
    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24  2170                38.57
    
