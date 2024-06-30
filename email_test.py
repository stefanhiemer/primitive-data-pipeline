#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

To Do read_log
 -

@author: Stefan Hiemer
"""

import asyncio
from email.message import EmailMessage

import aiosmtplib

message = EmailMessage()
message["From"] = "root@localhost"
message["To"] = "somebody@example.com"
message["Subject"] = "Hello World!"
message.set_content("Sent via aiosmtplib")

loop = asyncio.get_event_loop()
loop.run_until_complete(aiosmtplib.send(message, hostname="127.0.0.1", port=25))
