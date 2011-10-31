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


import getopt
from InterMapper import InterMapper
from pprint import pprint
import sys

debug = False
def_conf = './intermapper-conf.json'


def usage():
    """
    Usage:  %s  [options]  sql-command  parameters . . .

    Where:    sql-command       is a PostgreSQL command to be passed to psycopg2.execute.
              parameters        is an optional list of parameters for the command above.

    Options:  -h | --help                  Print this help message
              -c | --config=<config-file>  Specify a configuration file.
                                           Default is "%s"
              -d | --debug                 Debug mode.

    A configuration file is a text file in the JSON format, used to be specify what parameters
    each notifier object uses.
    """
    sys.stderr.write(usage.__doc__ % (sys.argv[0], def_conf)+"\n")


try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hc:d", ["help", "config=", "debug"])
except getopt.GetoptError, err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(1)
if len(args) < 1:
    usage()
    sys.exit(2)

conf = def_conf
for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-c", "--config"):
        conf = a
    elif o in ("-d", "--debug"):
        debug = True
    else:
        assert False, "unhandled option"

im = InterMapper(conf).connect()
im.run(args[0], args[1:], lambda r, rs: pprint(r))

exit(0)
