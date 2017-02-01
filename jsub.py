"""
jsub [-h] [-v] [--spool <spool>] [-u|--user <user>] [-g|--group <group>] [-c|--channel <channel>]+

After some inital setup, jsub drops privileges and connects to Redis and
subscribes to all the channels listed on the cmdline (defaults to 'inbox')
Each incoming message is parsed as json (failures are logged) and written
to an maildir folder with the same name as the channel.
"""

import os, pwd, grp
import sys
import redis
import threading
import mailbox
import logging
import getopt

__author__ = 'leifj'
__version__ = '0.0.1'

logging.basicConfig(level=logging.DEBUG)

def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    if os.getuid() != 0:
        # We're not root so, like, whatever dude
        return

    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    # Remove group privileges
    os.setgroups([])

    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)

    # Ensure a very conservative umask
    old_umask = os.umask(077)


class Listener(threading.Thread):
    def __init__(self, r, spool, channels):
        threading.Thread.__init__(self)
        self.redis = r
        self.spool = spool
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)
    
    def dlvr(self, item):
        md = mailbox.Maildir(self.spool,factory=json.loads)
        channel = md.add_folder(item['channel'])
        channel.add(json.loads(item['data']))
        channel.flush()
    
    def run(self):
        for item in self.pubsub.listen():
            try:
                self.dlvr(item)
            except Exception as ex:
                logging.error(ex)

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

    r = redis.Redis()
    client = Listener(r, spool, channels)
    client.start()

if __name__ == '__main__':
    main()
