from datetime import datetime as dt
from re import sub


class Tijdtest():
    def __init__(self, HGT, start, end):
        self.hisparc = HGT[0]
        self.gps = HGT[1]
        self.trigger = HGT[2]
        self.group = "/".join(HGT)
        self.start = dt(*start)
        self.end = dt(*end)
        self.time = (self.start, self.end)


def get_tests(hisparc=None, gps=None, trigger=None, group=None, subset='ALL',
              complement=True, part=None, unique=True):
    """ Search available tests and return those that match request

    In this program is a list of all available tests from the tijdtest
    project. Tests can be retrieved based on their parameters.

    The HiSPARC box number, the GPS used and the trigger of the swapped box.

    Some special cases exist; the reference used the external trigger (e),
    or the GPS position of the reference was set incorrectly (b).
    These are indicated by a suffix behind PMT2 or EXT.

    """

    #All tests, sorted by hisparc, gps, trigger, date.
    tests = (
        (('012','501', 'PMT2'),   (2011,11,29, 13,41), (2011,11,30, 13,58)),
        (('018','501', 'PMT2'),   (2011,11,18, 15,46), (2011,11,21,  7,25)),
        (('018','test','PMT1t1'), (2012, 5, 9, 15,15), (2012, 5,10, 11,13)),
        (('040','501', 'PMT2'),   (2011,11,30, 14,12), (2011,12, 1, 15,30)),
        (('040','test','PMT2'),   (2011,12, 1, 15,45), (2011,12, 2, 11,38)),
        (('050','501', 'PMT2'),   (2011,11,23, 15, 0), (2011,11,24, 13,18)),
        (('050','501', 'EXT' ),   (2011,11,23, 14,28), (2011,11,23, 14,58)),
        (('050','test','PMT1t1'), (2012, 5,10, 12, 0), (2012, 5,11, 15,03)),
        (('050','test','PMT1t'),  (2012, 5,11, 15,10), (2012, 5,12, 22,45)),
        (('053','501', 'PMT2'),   (2012, 1, 9, 11,14), (2012, 1,10,  9,28)),
        (('053','501', 'PMT2e'),  (2012, 1,12, 14,03), (2012, 1,13, 14,20)),
        (('053','501', 'PMT2b'),  (2011,12,20, 15,33), (2011,12,21, 20, 0)),
        (('053','501', 'EXT' ),   (2012, 1,11, 11,34), (2012, 1,12, 14, 0)),
        (('053','501', 'EXTe'),   (2012, 1,10,  9,32), (2012, 1,11, 11,32)),
        (('053','test','PMT2'),   (2012, 1,13, 14,30), (2012, 1,15, 17,48)),
        (('053','test','PMT2e'),  (2012, 1,18, 13,26), (2012, 1,19,  9,26)),
        (('053','test','EXT'),    (2012, 1,15, 17,58), (2012, 1,17, 11,07)),
        (('053','test','EXTe'),   (2012, 1,17, 11,10), (2012, 1,18, 13,23)),
        (('065','501', 'PMT2'),   (2011,11,24, 13,24), (2011,11,25, 11,48)),
        (('074','501', 'PMT2'),   (2011,11,16, 14,44), (2011,11,17, 15, 6)),
        (('074','501', 'EXT' ),   (2011,11,22,  9,30), (2011,11,23,  9,38)),
        (('074','100m','PMT2'),   (2011,11,17, 15, 9), (2011,11,18, 14,49)),
        (('083','501', 'PMT2'),   (2011,11,15, 15,52), (2011,11,16, 14,25)),
        (('083','501', 'PMT2b'),  (2011,12, 9, 11,58), (2011,12,13,  9,11)),
        (('083','501', 'PMT1b'),  (2011,12, 8, 11,15), (2011,12, 9, 11,56)),
        (('083','501', 'EXTb'),   (2011,12,13,  9,14), (2011,12,19, 13,52)),
        (('083','test','EXT'),    (2011,12, 4, 22, 0), (2011,12, 8, 11, 9)),
        (('083','test','PMT2'),   (2011,12, 2, 15,49), (2011,12, 4, 21,54)),
        (('122','501', 'PMT2'),   (2011,11,28, 15,15), (2011,11,29, 13,27)),
        (('156','501', 'PMT2'),   (2011,11,21,  7,27), (2011,11,22,  9,14)),
        (('176','501', 'PMT2'),   (2011,11,25, 12, 3), (2011,11,26, 14,47)),
        (('176','501', 'PMT1'),   (2011,11,26, 14,54), (2011,11,27, 14,22)),
        (('176','501', 'EXT' ),   (2011,11,27, 14,26), (2011,11,28, 14,56)))

#            (('050','501', 'PMT2s'), (2011,11,23, 10,58),(2011,11,23, 13,40)),
#            (('050','501', 'PMT2s'), (2011,11,23, 13,41),(2011,11,23, 14,26)),

    test_all = [Tijdtest(*test) for test in tests]

    #Select a subset
    if subset in ('ALL'):
        test_list = test_all
    elif subset in ('PMT'):
        test_list = [test
                     for test in test_all
                     if test.trigger in ('PMT2', 'PMT1') and
                        test.gps in ('501')]
    elif subset in ('EXT'):
        test_list = [test
                     for test in test_all
                     if test.trigger in ('EXT', 'EXTe', 'PMT2e')]
    elif subset in ('GPS'):
        test_list = [test
                     for test in test_all
                     if test.gps in ('test')]
    elif subset in ('Bad'):
        test_list = [test
                     for test in test_all
                     if test.trigger in ('PMT2b', 'PMT1b', 'EXTb') or
                        test.gps in ('100m')]
    else:
        test_list = test_all

    if complement == False and subset in ('EXT', 'GPS', 'Bad'):
        pass
    elif subset in ('EXT'):
        test_list = [test
                     for test in test_all
                     for ptest in test_list
                     if test.group == sub('EXT$', 'PMT2', ptest.group) or
                        test.group == ptest.group.replace('EXTe', 'EXT') or
                        test.group == ptest.group.replace('PMT2e', 'PMT2') or
                        test.group == ptest.group]
    elif subset in ('GPS'):
        test_list = [test
                     for test in test_all
                     for ptest in test_list
                     if test.group == ptest.group.replace('test', '501') or
                        test.group == ptest.group]
    elif subset in ('Bad'):
        test_list = [test
                     for test in test_all
                     for ptest in test_list
                     if test.group == ptest.group.replace('100m', '501') or
                        test.group == ptest.group.replace('EXTb', 'EXT') or
                        test.group == ptest.group.replace('PMT2b', 'PMT2') or
                        test.group == ptest.group.replace('PMT1b', 'PMT1') or
                        test.group == ptest.group]

    if hisparc:
        test_list = [test for test in test_list if test.hisparc in hisparc]
    if gps:
        test_list = [test for test in test_list if test.gps in gps]
    if trigger:
        test_list = [test for test in test_list if test.trigger in trigger]
    if group:
        test_list = [test for test in test_list if test.group in group]

    #Get a part of the class
    if part in (None,): pass
    elif part in ('hisparc'): test_list = [test.hisparc for test in test_list]
    elif part in ('trigger'): test_list = [test.trigger for test in test_list]
    elif part in ('gps'): test_list = [test.gps for test in test_list]
    elif part in ('group'): test_list = [test.group for test in test_list]
    elif part in ('time'): test_list = [test.time for test in test_list]
    elif part in ('start'): test_list = [test.start for test in test_list]
    elif part in ('end'): test_list = [test.end for test in test_list]

    if unique:
        test_list = sorted(set(test_list))

    return test_list

if __name__ in ('__main__'):
    print ("Number of tests: %s (unique: %s)" %
           (len(get_tests(subset='ALL', unique=False)),
            len(get_tests(subset='ALL', unique=True))))
    print ("Number of boxes: %s" %
           len(get_tests(part='hisparc', unique=True)))
    print ('HII:074:  %s' % ", ".join(get_tests(hisparc='074', part='group')))
    print ('GPS:test: %s' % ", ".join(get_tests(gps='test', part='group')))
    print ('TRG:EXT:  %s' % ", ".join(get_tests(trigger='EXT', part='group')))
    print ('HII:053, TRG:EXT: %s' %
           ", ".join(get_tests(hisparc='053', trigger='EXT', part='group')))
    print ('GRP:018/501/PMT2: %s' %
           ", ".join(get_tests(group='018/501/PMT2', part='group')))
    print ("Boxes tested with multiple GPSs: %s" %
           ", ".join(get_tests(subset='GPS', part='hisparc')))
    print ("Boxes tested with bad GPS coordinates: %s" %
           ", ".join(get_tests(subset='Bad', part='hisparc')))
    print ("Groups which used external trigger: %s" %
           ", ".join(get_tests(subset='EXT', part='group', complement=False)))
    print ("Groups of previous, with the PMT triggered complement: %s" %
           ", ".join(get_tests(subset='EXT', part='group', complement=True)))
