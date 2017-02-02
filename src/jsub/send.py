"""
jsub-send [-h] [-v] [-c|--channel <channel>]+ < json

After some inital setup, jsub-send connects to Redis and sends the json 
provided on stdin to the channel(s) listed
"""

import os, pwd, grp
import sys
import mailbox
import logging
import getopt
import redis
import json

from . import __version__

__author__ = 'leifj'

logging.basicConfig(level=logging.DEBUG)

def main():
    """
    jsub main entrypoint
    """

    opts = None
    args = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], 
                                   'hvu:g:c:S', 
                                   ['help', 'version', 'spool=', 'loglevel=', 'logfile='])
    except getopt.error, msg:
        print msg
        print __doc__
        sys.exit(2)

    loglevel = logging.WARN
    logfile = None
    channels = []

    for o, a in opts:
        if o in ('-h', '--help'):
            print __doc__
            sys.exit(0)
        elif o in '--version':
            print "jsub version %s" % __version__
            sys.exit(0)
        elif o in '--loglevel':
            loglevel = getattr(logging, a.upper(), None)
            if not isinstance(loglevel, int):
                raise ValueError('Invalid log level: %s' % a)
        elif o in '--logfile':
            logfile = a
        elif o in ('-c','--channel'):
            channels += a
 
    log_args = {'level': loglevel}
    if logfile is not None:
        log_args['filename'] = logfile
    logging.basicConfig(**log_args)

    if not channels:
        channels = ['inbox']

    msg = json.load(sys.stdin)
    valid_json_data = json.dumps(msg)
    r = redis.Redis()
    pubsub = redis.pubsub() 
    for c in channels:
        pubsub.publish(c,valid_json_data)

if __name__ == '__main__':
    main()
