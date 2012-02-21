#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## This program is licensed under the GPL v3.0, which is found at the URL below:
##	http://opensource.org/licenses/gpl-3.0.html
##
## Copyright (c) 2011 Regents of the University of Michigan.
## All rights reserved.
##
## Redistribution and use in source and binary forms are permitted
## provided that this notice is preserved and that due credit is given
## to the University of Michigan at Ann Arbor. The name of the University
## may not be used to endorse or promote products derived from this
## software without specific prior written permission. This software
## is provided ``as is'' without express or implied warranty.


from Notifier import Notifier
import logging
import time


class Logfile(Notifier):
    """
    A class for objects used to notify an object external to InterMapper.

    The intention of this module is to log messages from InterMapper, for investigative
    purposes.

    Tests:

    >>> from Logfile import Logfile
    >>> import os
    >>> try:
    ...     cnf = { 'filename': '/tmp/Logfile-test.log', 'mode': 'w' }
    ...     xn = Logfile(cnf)
    ...     xn.notify("weiwang", "Test 1")
    ...     xn.notify("weiwang", "Test 2")
    ...     xn.close()
    ...     f = open(cnf['filename'], 'r')
    ...     txt = f.read()
    ...     print(txt)
    ...     f.close()
    ... except TypeError as ex:
    ...     print ex.args[0]
    ... except AttributeError as ex:
    ...     print ex.args[0]
    Test 1
    Test 2
    <BLANKLINE>
    """

    def close(self):
        self.file.close()

    def notify(self, recp, msg, opt={}):
        fname = time.strftime(self.C['filename'])
        if fname != self.name:
            self.logger = logging.getLogger(fname)
            try:
                self.logger.removeHandler(self.file)
                self.file = logging.FileHandler(fname, self.C['mode'])
                self.logger.addHandler(self.file)
                self.name = fname
                self.logger.setLevel(logging.DEBUG)
                self.logger.info(msg)
            except IOError as (errno, errmsg):
                return "I/O error({0}): {1}".format(errno, errmsg)
            except:
                return False

    def __init__(self, cnf):
        Notifier.__init__(self, { 'filename': '%Y-%m-%d.log', 'mode': 'a' })
        self.C.update(cnf)
        self.file = self.name = None

if __name__ == '__main__':
    import doctest
    doctest.testmod()
