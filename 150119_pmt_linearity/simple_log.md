# PMT linearity simple cap log


Test on 2015/1/19

PMT new chip with extra Ohm.

PMT voltage 789 V

Normal cap with fiber #8 resulted in signal 372 mV.

Cap with 5 fibers through connector.

    Fibers      Signal
    8           60 mV
    78          160 mV
    7           98 mV
    78          160 mV
    78 alt      180 mV
    678         224 mV
    5678        264 mV
    45678       320 mV
    4567        262 mV
    456         170 mV
    45          102 mV
    4           64 mV
    45          110 mV
    5           46 mV
    56          90 mV


Tree list:

    Fibers      Signal
    4       64 mV
                 102 mV
    5       46 mV      170 mV
                  90 mV      262 mV
    6       .. mV      224 mV      320 mV
                  .. mV      264 mV
    7       98 mV
                 160 mV
    8       60 mV
