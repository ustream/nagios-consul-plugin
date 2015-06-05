#!/usr/bin/python
"""Usage: 
    check-consul-health.py node NODE DC
        [--addr=ADDR]
        [--CheckID=CheckID | --ServiceName=ServiceName]
        [--verbose]

Arguments:
    NODE  the consul node_name
    DC    the consul datacenter

Options:
    -h --help                  show this
    -v --verbose               verbose output
    --addr=ADDR                consul address [default: http://localhost:8500]
    --CheckID=CheckID          CheckID matcher
    --ServiceName=ServiceName  ServiceName matcher
"""

from docopt import docopt
import requests, json, traceback, exceptions

def dump(it):
    if arguments['--verbose']: print it

def buildNodeUrl():
    url = "%(--addr)s/v1/health/node/%(NODE)s?dc=%(DC)s" % arguments
    dump("Url: " + url)
    return url

def getJsonFromUrl(url):
    r = requests.get(url)
    dump("Response: " + r.text)
    dump("Status code: " + str(r.status_code))
    r.raise_for_status()
    return r.json()

def printCheck(check):
    print "> %(Node)s:%(ServiceName)s:%(Name)s:%(CheckID)s:%(Status)s" % check

def processFailing(checks):
    filters = map(lambda field: \
        lambda x: arguments['--' + field] is None or x[field] == arguments['--'+field],
        ['CheckID', 'ServiceName']
    )

    filtered = filter(lambda x: all(f(x) for f in filters), checks)
    passing  = filter(lambda x: x['Status'] == 'passing', filtered)
    warning  = filter(lambda x: x['Status'] == 'warning', filtered)
    critical = filter(lambda x: x['Status'] == 'critical', filtered)

    if len(checks) == 0:
        print "There is no matching node"
        return 3

    if len(filtered) == 0:
        print "There is no matching checks"
        return 3

    checkOutput = lambda x: x["Name"] + ":" + x["Output"]

    if len(critical):
        print "|".join(map(checkOutput, critical))
        for check in critical:
            printCheck(check)
    if len(warning):
        print "|".join(map(checkOutput, warning))
        for check in warning:
            printCheck(check)
    if len(passing):
        print "Passing: %d" % (len(passing))
        for check in passing:
            printCheck(check)

    return 2 if len(critical) else 1 if len(warning) else 0

if __name__ == '__main__':
    try:
        arguments = docopt(__doc__)
        dump("Arguments: " + str(arguments))
        if arguments['node']:
            url = buildNodeUrl()
            json = getJsonFromUrl(url)
            exit(processFailing(json))
    except exceptions.SystemExit: raise
    except:
        traceback.print_exc()
        exit(3)
