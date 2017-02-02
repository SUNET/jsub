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
import subprocess
import shlex

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

    if not os.path.exists(spool):
        os.mkdir(spool)
        gid = grp.getgrnam(group).gr_gid
        uid = pwd.getpwnam(user).pw_uid
        os.chown(spool, uid, gid)
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
