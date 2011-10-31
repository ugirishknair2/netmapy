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


from abc import ABCMeta, abstractmethod
import re


class AlertError(Exception):
    pass


class Notifier:
    """
    A class for objects used to notify an object in external systems.

    This is intended to be a base class for other notifier object classes: such as HTTP post.

    Tests:

    >>> try:
    ...     xn = Notifier()
    ...     xn.notify("Test message")
    ... except TypeError as ex:
    ...     print ex.args[0]
    ... else:
    ...     print("No exception?")
    Can't instantiate abstract class Notifier with abstract methods notify
    >>> class TestNotifier(Notifier):
    ...     def notify(self, recp, msg):
    ...         pass
    >>> xn = TestNotifier({'delimiter': '\|'})
    >>> xn.split('aaa|bbb|||fff ggg')
    ['aaa', 'bbb', '', '', 'fff ggg']
    """
    __metaclass__ = ABCMeta

    @classmethod
    def new(cls, klass, conf):
        """
        Function to create am object of class (klass) with (conf) as configuration.
        """
        mod = __import__(klass)
        return getattr(mod, klass)(conf)

    @abstractmethod
    def notify(self, recp, msg):
        pass

    def split(self, msg):
        return re.split(self.C['delimiter'], msg)

    def __init__(self, cnf):
        self.C = {'delimiter': ','}
        self.C.update(cnf)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
