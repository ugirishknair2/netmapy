#!/usr/bin/env python
##
## $Id: xmlget.py,v 1.4 2012/02/06 20:05:58 weiwang Exp $
##

import getopt, json, os, re, sys, urllib2
from xml.dom.minidom import parseString


class XMLget:
    """
    A command line version of the InterMapper xmlprobe.xml -- which imports this script as a module.

    Usage:  %(cli)s  [options]  [variable=value] . . .

    Where:    [variable=value]      is a variable/value pair that gets passed to the script for
                                    building an HTTP request, e.g., host=10.20.30.40 will be used
                                    to replace occurances of "%(percent)s(host)s" in the request data in
                                    the <config-file>.

    Options:  -h | --help                  Print this help message
              -c | --config=<config-file>  Specify a configuration file.
                                           Default is "%(conf)s"
              -p | --path=<add-path>       Addition to the PYTHONPATH for this program.

    A configuration file is a text file in the JSON format, used to specify what parameters are
    used to form a URL and command for a XML RPC call to the xml_agent in a Cisco device via HTTP
    or HTTPS. A sample configuration is provided in 'xmlagent-conf-dist.json'.

    Any data in the configuration not used by XMLget is simply ignored, which means the script
    will not warn you of a typo. However, missing required configuration item will cause a
    'KeyError' to be raised.

    Example:

    %(cli)s  host=10.20.30.40

        That will probe the host with the given IP address.

    %(cli)s  -config=xmlagent-template.json  host=switch123.example.com

        The script will load the given 'xmlagent-template.json' file, which may contain all needed
        data for a specific probe, then perform the probe on device 'switch123.example.com'.
    """
    CONF = './xmlagent-conf.json'

    def output(self, msg='None'):
        try:
            fmt = self.C['result']['output']['format']
        except KeyError, err:
            fmt = '%s'
        print(fmt % msg)

    def usage(self, argv):
        sys.stderr.write((XMLget.__doc__ % {'cli': argv[0], 'percent': '%', 'conf': XMLget.CONF})+"\n")

    def __call__(self, request={}):
        """
        This makes an XMLget object callable.
        """
        res = self.C['result']
        try:
            msg = res['output']
            output = 'error'
        except:
            output = False
        try:
            request.update(self.data)
            xml = self.agent.get(request)
            if self.C['debug']: print(xml)
            code = 0
            dom = parseString(xml)

            result = []
            for node in dom.getElementsByTagName(res['tag']):
                result.extend([t.nodeValue.strip() for t in node.childNodes if t.nodeType == t.TEXT_NODE])

            if len(result) == 1 and 'map' in res:
                try:
                    rval = int(result[0])
                except ValueError, err:
                    pass
                rmap = res['map']
                for cc in rmap:
                    rr = rmap[cc]
                    if (type(rr) == list and
                        (len(rr) == 2 and rval >= rr[0] and rval <= rr[1])
                        or (len(rr) == 1 and rval >= rr[0])
                        or len(rr) == 0):
                        code = int(cc)
                        break

            if output:
                msgdata = { 'count': len(result), 'result': msg['delimiter'].join(result) }
                msgdata.update(self.C['data'])
                output = 'success'
                try:
                    msgdata['status'] = msg['status'][code+1]
                except:
                    msgdata['status'] = "Exit %d" % code
            msgdata['reason'] = 'None';
        except urllib2.URLError, err:
            msgdata['reason'] = str(err)
            code = 3
        except Exception, err:
            msgdata['reason'] = str(err)
            code = -1
        except:
            msgdata['reason'] = "Unknown"
            code = -1

        # if output: self.output(msg[output] % msgdata)
        if output: self.output(msgdata)
        if self.C['debug']:
            print "Exit = %d" % code
        return code


    def test(self, tc, argv):
        if tc == '1':
            print '\{ $result := 0, $cmd := "%s", $status := "Testing" }Test-mode=1' % ' '.join(argv)
        sys.exit(0)

    def __init__(self, argv):
        self.C = { 'result': { 'output' : { 'format':	'{reason:="%s"}' }}}

        test_mode = False
        conf = XMLget.CONF
        try:
            opts, args = getopt.gnu_getopt(argv[1:], "hc:dp:x:", ["help", "config=", "debug", "path="])
        except getopt.GetoptError, err:
            # print help information and exit:
            print str(err) # will print something like "option -a not recognized"
            self.usage(argv)
            sys.exit(-1)

        for o, a in opts:
            if o in ("-h", "--help"):
                self.usage(argv)
                sys.exit()
            elif o in ("-c", "--config"):
                conf = a
            elif o in ("-p", "--path"):
                sys.path += a.split(':')
            elif o in ("-x"):
                test_mode = a
            else:
                assert False, "unhandled option"

        self.data = {}
        for avpair in args:
            try:
                a, v = avpair.split('=')
                self.data[a] = v
            except TypeError, err:
                self.output("Error: %s (%s)" % (err, avpair))
                sys.exit(-1)

        try:
            self.C = json.load(open(conf, 'r'), 'utf-8')
            if self.C['debug']:
                print "Running in debug mode..."
        except ValueError, err:
            self.output("Error: %s" % (err))
            sys.exit(-1)
        except:
            self.output("Error loading configuration (file = %s, pwd = %s)." % (conf, os.getcwd()))
            sys.exit(-1)

        if 'path' in self.C:
            for apath in self.C['path'].split(':'):
                if os.path.isdir(apath): sys.path.append(apath)
        from cisco.HttpXmlAgent import HttpXmlAgent
        self.agent = HttpXmlAgent(self.C)

        if test_mode:
            self.test(test_mode, argv)

if __name__ == '__main__':
    sys.exit(XMLget(sys.argv)())
