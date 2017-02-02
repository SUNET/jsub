"""
jsub-run [-h] [-v] [--spool <spool>] [-u|--user <user>] [-g|--group <group>] [-c|--channel <channel>]+ -- cmdline

After some inital setup, jsub drops privileges and connects to Redis and
subscribes to all the channels listed on the cmdline (defaults to 'inbox')
Each incoming message is parsed as json (failures are logged) and written
to an maildir folder with the same name as the channel.
"""

import os, pwd, grp
import sys
import mailbox
import logging
import getopt
import redis
import json

__author__ = 'leifj'
__version__ = '0.0.1'

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
                                   ['help', 'version', 'spool=', 'channel=', 
                                    'loglevel=', 'logfile=', 'user=', 'group='])
    except getopt.error, msg:
        print msg
        print __doc__
        sys.exit(2)

    loglevel = logging.WARN
    logfile = None
    user = 'nobody'
    group = 'nogroup'
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
        elif o in ('-u','--user'):
            user = a
        elif o in ('-g','--group'):
            group = a
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
