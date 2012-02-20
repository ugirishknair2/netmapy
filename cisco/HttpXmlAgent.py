#!/usr/bin/env python
# -*- coding: utf-8 -*-
## $Id: HttpXmlAgent.py,v 1.2 2011/12/28 20:19:52 weiwang Exp $
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

import sys, time, urllib, urllib2


class HttpXmlAgent:
    """
    An object accessing xml_agent on a Cisco device via HTTP, based on a script from Matt Galazka:

    #!/bin/bash
    if [ -z $3 ]; then
        echo "./check-xlate.sh [Admin IP] [Context] [PAT IP]
        "
        exit
    fi

    XLATECOUNT=`curl --basic -u admin:<PW> \
        -d "xml_cmd=<request_raw context-name=\"$2\">show xlate global $3 %7c count</request_raw>" \
        http://$1/bin/xml_agent 2>/dev/null | egrep "^[0-9 ]+$" | awk '{ print $1 }'`

    echo "$XLATECOUNT"

    Test:

    >>> import json
    >>> 
    """

    def get(self, dat):
        """
        Post request and return response.
        """
        cdata = self.rupdate(self.C['data'], dat)
        creq = urllib.urlencode(self.request(cdata))
        url = self.url(cdata)
        if self.C['debug']:
            print("URL = %s" % url)
            print("Request = %s" % creq)

        #       Build request, with basic authentication only:
        post = urllib2.Request(url, creq)
        if 'user' in self.C and 'password' in self.C:
            import base64
            post.add_header('Authorization',
                            'Basic %s' % base64.encodestring('%s:%s' % (self.C['user'], self.C['password']))[:-1])
        
        try:
            response = urllib2.urlopen(post)
            return response.read()
        except urllib2.HTTPError, err:
            pass
        if self.C['debug']: print err
        return ''

    def format(self, fmt, data):
        """
        Recursive format.
        """
        for x in range(self.C['recursion']):
            url = fmt % data
            if url == fmt: break
            fmt = url
        return url

    def request(self, dat):
        creq = self.C['request']
        req = {}
        for var in creq:
            req[var] = self.format(creq[var], dat)
        return req

    def rupdate(self, dat, obj):
        for x in obj:
            if x in dat:
                if type(dat[x]) == dict and type(obj[x]) == dict:
                    dat[x] = self.rupdate(dat[x], obj[x])
                    continue
            dat[x] = obj[x]
        return dat

    def url(self, req):
        return self.format(self.C['url-format'], req)

    def __init__(self, cnf):
        """
        Details of the configuration (conf) are found in xmlagent-conf-dist.json.
        """
        self.C = {
            "url-format": "https://%(host)s/$(agent)s",
            'request':
                {
                "xml_cmd": "<request_raw context-name=\"%(context)s\">%(command)s</request_raw>",
                },
            "data":
                {
                "agent": "bin/xml_agent",
                "command": "show xlate global %(vip)s | count",
                },
            "result":
                {
		"tag":	"xml_show_result",
                },
            'debug': False,
            'recursion': 8,
            }
        self.C.update(cnf)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
