#!/usr/bin/env python

import os
import sys
import time
import commands
from lib.common_lib import mysql
from lib.common_lib import mylogger


class Writer:
    def __init__(self, filename):
        self.filename = filename
    def write(self, msg):
        f = file(self.filename, 'a')
        f.write(msg)
        f.close()


class shellinabox(object):
    def run_command(self,cmd):
        rc, out = commands.getstatusoutput(cmd)
        if ( rc != 0 ):
            return False
        else:
            return True

    def pre_action(self):
        if os.path.isfile(filename):
            time_now = time.strftime("%Y%m%d%H%I.%S",time.localtime())
            cmd = 'mv ' + filename + ' ' + filename + '.' + time_now
            if ( self.run_command(cmd) == False ):
                logger.debug('failure: mv %s to %s.%s' %(filename,filename,time_now))
                sys.exit(1)
        else:
            logger.debug('failure: The file "%s" is not exist! No file will be baked.' %filename)

    def add_head(self):
        stdout_pre = sys.stdout
        sys.stdout = Writer(filename)
        print '# Should shellinaboxd start automatically'
        print 'SHELLINABOX_DAEMON_START=1\n'
        print '# TCP port that shellinboxd\'s webserver listens on'
        print 'SHELLINABOX_PORT=4200\n'
        print '# Parameters that are managed by the system and usually should not need'
        print '# changing:'
        print '# SHELLINABOX_DATADIR=/var/lib/shellinabox'
        print '# SHELLINABOX_USER=shellinabox'
        print '# SHELLINABOX_GROUP=shellinabox\n'
        print '# Any optional arguments (e.g. extra service definitions)'
        print '# We disable beeps, as there have been reports of the VLC plugin crashing'
        print '# Firefox on Linux/x86_64.'
        sys.stdout = stdout_pre

    def add_rest(self,rows):
        text = ''
        for row in rows:
            line1 = ' -s /ipmi/console/%s:nobody:nogroup:/:\\"ipmitool -I lanplus -U %s -H %s -P %s sol activate\\"' %(row[0].replace('.','/'),row[1],row[0],row[2])
            line2 = ' -s /ipmi/deactivate/%s:nobody:nogroup:/:\\"ipmitool -I lanplus -U %s -H %s -P %s sol deactivate\\"' %(row[0].replace('.','/'),row[1],row[0],row[2])
            line3 = ' -s /ipmi/shell/%s:nobody:nogroup:/:\\"ipmitool -I lanplus -U %s -H %s -P %s shell\\"' %(row[0].replace('.','/'),row[1],row[0],row[2])
            line = line1 + line2 + line3
            text += line
        Writer(filename).write('SHELLINABOX_ARGS="--no-beep --localhost-only --disable-ssl')
        Writer(filename).write(text)
        Writer(filename).write('"\n')

    def run(self):
        bmc_cmd = 'select bmc_ip,userid,password from server_info where sol = 1;'
        rc,rows = mysql('xxxx','xxxxxx','server_info').get_response(bmc_cmd)
        if rc:
            self.pre_action()
            self.add_head()
            self.add_rest(rows)
            

if __name__ == '__main__':
    filename = '/etc/default/shellinabox'
    logger = mylogger("/opt/log/shellinabox_mc.log").initlog()
    shellinabox().run()

