# PMT linearity simple cap log


Test on 2015/1/19

PMT new chip with extra Ohm.

PMT voltage 789 V

Normal cap with fiber #8 resulted in signal 372 mV.

Cap with 5 fibers through connector.

    Fibers      Signal [mV]
    8           60
    78          160
    7           98
    78          160
    78 alt      180
    678         224
    5678        264
    45678       320
    4567        262
    456         170
    45          102
    4           64
    45          110
    5           46
    56          90


Tree list:

    Fibers   Signal [mV]
    4        64
                  102
    5        46         170
                   90         262
    6       [45]        224         320
                 [143]        264
    7        98        [203]
                  160
    8        60

Values in brackets are derived from surrounding values..
