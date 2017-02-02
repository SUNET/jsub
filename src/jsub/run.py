"""
jsub-run [-h] [-v] [--spool <spool>] [-u|--user <user>] [-g|--group <group>] [-c|--channel <channel>]+ -- cmdline

After some inital setup, jsub-run optionally drops privileges and sets starts to
process messages in the spool maildir. Each time a message is received the ENV
element in the json object is used to generate an environment for the cmdline
which is executed once. Each message is removed after processing.
"""

import os, pwd, grp
import sys
import mailbox
import logging
import getopt
import subprocess
import shlex

__author__ = 'leifj'

from . import __version__

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
    user = None
    group = None
    channels = []
    spool = "/var/spool/jsub"

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
        elif o in ('--spool'):
            spool = a
 
    log_args = {'level': loglevel}
    if logfile is not None:
        log_args['filename'] = logfile
    logging.basicConfig(**log_args)

    if not channels:
        channels = ['inbox']

    if user and group:
        drop_privileges(user,group)

    i = inotify.adapters.InotifyTree(spool,mask=inotify.constants.IN_MOVE)
    md = mailbox.Maildir(self.spool, factory=json.loads)

    def _process_messages():
        for key,message in mb.iteritems():
            env = dict()
            for k,v in msg['ENV'].items():
                n = "JSUB_%s" % pipes.quote(k).upper()
                env[n] = pipes.quote(v)
            p = subprocess.Popen(shlex.split(args), env=env, stdout=PIPE, stderr=PIPE)
            p.communicate()
            p.wait()
        mb.remove(key)

    _process_messages()

    try:
       for event in i.event_gen():
          if event is not None:
             (header, type_names, watch_path, filename) = event
             if 'new' in filename:
                _process_messages()
                     
    except Exception as ex:
       logging.error(ex)
    finally:
       i.remove_watch(spool)
    
if __name__ == '__main__':
    main()
