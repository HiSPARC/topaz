# 150522 Check dead time and trace window overlap

Station 99 - HiSPARC II # 160

Using pulse generator set to send two pulses per interval with a chosen
delay between the two pulses.

i.e. `----^_^----^_^----^_^`

where `----` is the interval time (1 second), `^` is a pulse, and `_` is
the short delay between the pulses.

The pulse generator was connected to PMT input #2.

Trigger is set to 'one high'.

Time window is also change from the normal values to reduce the
`post-coincidence time`, allowing a second trigger to have the
`coincidence time` (part of the time window) in its
`pre-coincidence time`.

The Time window consists of three parts:

- `pre-coincidence time`
- `coincidence time` - here the trigger conditions are to be met, the
    start of this part will be when the a trigger might occur, normally
    when a signal crosses the low threshold. 
- `post-coincidence time`


## Test log

    Time (GPS)      Time window [µs]    Pulse delay [µs]
    11:10 - 11:15   2. : 1. : 0.        1.6
    11:24 - 11:26   1. : 1. : 1.        1.6
    11:27 - 11:29   1. : 1. : 1.        2.2
    11:32 - 11:34   .5 : 1. : 0.        1.6
