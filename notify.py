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


##
## notify.py (weiwang 2011-09-30)
##
##      A Python script to send a text message via a Notifier object.


import getopt
import json
import os
import re
import sys
import time

def_conf = './notify-conf.json'


def usage():
    """
    Usage:  %s  [options]  "recipient"  "message"

    Where:    "recipients" is a name that identifys one (or more) recipient(s) for the
                           "notifier" configured. The content of this name depends on
                           the notifier object to be used.

              "message"    is a message to be sent. Multiple messages are accepted. If
                           multiple message are specified, they will be joined into one
                           separated by a single space.

    Options:  -h | --help                  Print this help message
              -c | --config=<config-file>  Specify a configuration file.
                                           Default is "%s"
              -d | --debug                 Debug mode.
              -p | --path=<add-path>       Addition to the PYTHONPATH for Notifier modules.

    A configuration file is a text file in the JSON format, used to be specify what parameters
    each notifier object uses.
    """
    sys.stderr.write(usage.__doc__ % (sys.argv[0], def_conf)+"\n")


try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hc:dp:", ["help", "config=", "debug", "path="])
except getopt.GetoptError, err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(1)
if len(args) < 1:
    usage()
    sys.exit(2)

debug = False
conf = def_conf
for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-c", "--config"):
        conf = a
    elif o in ("-d", "--debug"):
        debug = True
    elif o in ("-p", "--path"):
        sys.path += a.split(':')
    else:
        assert False, "unhandled option"

try:
    CONF = { 'notifier': [ 'Notifier' ], 'path': './notifier' }
    CONF.update(json.load(open(conf, 'r'), 'utf-8'))
except ValueError, err:
    print "Error: %s" % (err)
    sys.exit(1)
except:
    print "notify: Error loading configuration."
    sys.exit(1)

for apath in CONF['path'].split(':'):
    if os.path.isdir(apath): sys.path.append(apath)
from Notifier import Notifier

recp = args[0]
msg = " ".join(args[1:])
for klass in set(re.split('[\s,]+', CONF['notifier'])):
    try:
        notifier = Notifier.new(klass, CONF[klass])
        resp = notifier.notify(recp, msg)
        if debug:
            print("%s('%s', '%s') = %s\n" % (klass, recp, msg, resp))
    except Exception as ex:     #       Call all exceptions so that every configured notifier is visited.
        err = "%s %s = %s -- message = %s" % (time.strftime("%Y-%m-%dT%H:%M:%S"), ex.__class__.__name__, str(ex), msg)
        try:
            flog = Notifier.new("Logfile", CONF['errorlog'])
            flog.notify(recp, err)
        except Exception as ex:
            sys.stderr.write("%s\n" % (err))
sys.exit(0)
