#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

To Do read_log
 -

@author: Stefan Hiemer
"""

import threading
import smtpd
import asyncore
import smtplib

server = smtpd.SMTPServer(('localhost', 1025), None)

loop_thread = threading.Thread(target=asyncore.loop, name="Asyncore Loop")
# If you want to make the thread a daemon
# loop_thread.daemon = True
loop_thread.start()

# port should match your SMTP server
client = smtplib.SMTP('localhost', port=1025)

fromaddr = 'user@smtpd-test.com'
toaddrs = 'stefan.hiemer@fau.de'
msg = 'Hello'

client.sendmail(fromaddr, toaddrs, msg)
client.quit()
