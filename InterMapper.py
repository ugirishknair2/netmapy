#!/bin/env python
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


import json
import psycopg2


class InterMapper:
    """
    An object class for intigration with InterMapper.

    Tests:

    >>> im = InterMapper('./intermapper-test.json')
    >>> if im.CONF['host'] == 'localhost':
    ...     print "Yes!"
    ... else:
    ...     print json.dumps(im.CONF, sort_keys=True, indent=4)
    Yes!

    >>> from pprint import pprint
    >>> im = InterMapper()
    >>> def print_row(r, rs): pprint(r)
    >>> im.connect().run("select map_id, name, path from map where name = 'Test'", (), print_row)
    (7, 'Test', '/Test')
    []
    >>> im.connect().run("select map_id, name, path from map where name = %s", ('Test',), print_row)
    (7, 'Test', '/Test')
    []
    >>> im.map2path('Test')
    '/Test'
    >>> xn = im.notifier('notify: EM')
    >>> xn[0][2]
    'notify: EM'
    >>> xno = Notifier(xn[0])
    >>> xno.message()
    [u'event', u'name', u'probegroup', u'memberprobe', u'address', u'status', u'condition', u'prevcondition', u'probe', u'sysuptime', u'syscontact', u'syslocation', u'comment', u'lastdown', u'time', u'document', u'version', u'downcount', u'critcount', u'alrmcount', u'warncount', u'ackmessage', u'sendcount', u'maxsendcount', u'deviceimid', u'mapid']
    >>> xr = im.rule(xn[0])
    >>> xr[0][0] == xn[0][0] and xr[0][3] == xn[0][1]
    True
    """

    def __init__(self, cf='./intermapper-conf.json'):
        self.CONF = { 'host': 'localhost', 'database': { 'name': 'intermapper', 'port': 8183, 'user': 'dba', 'password': 'dbapw' } }
        try:
            self.CONF.update(json.load(open(cf, 'r'), 'utf-8'))
        except:
            raise Exception("Error loading configuration: %s"%(cf))
        self.cur = {}

    def connect(self):
        db = self.CONF['database']
        self.db = psycopg2.connect(host=self.CONF['host'], database=db['name'], user=db['user'], password=db['password'], port=db['port'])
        self.cur = self.db.cursor()
        return self

    def run(self, sql, data=(), afn=lambda r, rs: rs.append(r)):
        self.cur.execute(sql, data)
        rows = []
        while True:
            row = self.cur.fetchone()
            if not row: break
            afn(row, rows)
        return rows

    def map2path(self, name):
        row = self.run("select path from map where name = %s", (name,))
        return row[0][0] if len(row) == 1 else None

    def notifier(self, name):
        return self.run("select * from notifier where name = %s", (name,))

    def rule(self, anotifier, mapid=None, devid=None):
        sql = "SELECT * FROM notifierrule WHERE server_id=%d AND notifier_id=%d" % anotifier[0:2]
        if mapid != None: sql += " AND map_id=%d" % mapid
        if devid != None: sql != " AND device_id=%d" % devid
        return self.run(sql)


class Notifier:
    def __init__(self, data):
        self.server_id = data[0]
        self.notifier_id = data[1]
	self.name = data[2]
	self.enabled = data[3]
	self.create_time = data[5]
	self.delete_time = data[6]

        #       Parsing the XML data to get message, etc.
        from xml.dom.minidom import parseString
	dom = parseString(data[4])
        for xn in dom.getElementsByTagName('d'):
            if xn.getAttribute('name') == 'message':
                for xnc in xn.childNodes:
                    if xnc.nodeType == xn.TEXT_NODE:
                        self.notifier_msg = xnc.data.lower().replace('${', '').replace('}', '').split("|")
                        return

    def message(self):
        return self.notifier_msg


if __name__ == '__main__':
    import doctest
    doctest.testmod()
