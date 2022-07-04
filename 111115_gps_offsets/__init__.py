"""HiSPARC tijdtest Package

These scripts are intended for the analysis of the tijdtest data.

The following modules are included:

:mod:`~tijdtest.analyse`
    a module to make various plots for the tijdtest data

:mod:`~tijdtest.delta`
    a module to calculate, store and retrieve the delta values

:mod:`~tijdtest.data`
    a module to download and store the tijdtest data

:mod:`~tijdtest.helper`
    a module containing some helper functions, like getting the nanosecond
    part of the ext_timestamp

:mod:`~tijdtest.testlist`
    a module which contains a list of all tests in the tijdtest
    for each test the hisparc box serial, used gps, used trigger and
    start and end date and time are known

"""
from . import analyse
from . import delta
from . import data
from . import helper
from . import testlist
from . import david

__all__ = ['analyse', 'delta', 'data', 'helper', 'testlist', 'david']
