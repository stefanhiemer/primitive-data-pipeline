#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

To Do read_log
 -

@author: Stefan Hiemer
"""

import os
import glob
import sys
from subprocess import Popen, PIPE, run
from re import sub
import datetime
from time import sleep, gmtime, strftime

def check_ticket():
    """
    Check how many tickets are there
    if more than one, delete all except newest
    if one: read expiration time and become active 20 minutes before
    order new ticket, delete old, set new activation time
    """

    # get machine/host name
    machine = Popen(['hostname'], stdout = PIPE)

    # convert from byte to string
    machine = machine.stdout.readline().strip().decode("utf-8")

    while 1:
        # count how many tickets are currently used (counter starts at two
        # because two lines are inserted by default and technically I just count
        # lines)
        p = Popen(["klist","-l"],stdout=PIPE)
        tickets = int(Popen(["wc","-l"],
                            stdin=p.stdout,
                            stdout=PIPE).stdout.readline())
        if tickets != 3:
            print("Remove tickets. Time: ",strftime("%c"))
            p = Popen(["klist","-l"],stdout=PIPE)

            # get rid of first three lines which contain the header names, an
            # empty line and the longest living ticket. We want to delete the
            # shorter living tickets.
            for i in range(3):
                p.stdout.readline()

            # delete remaining short living tickets
            for line in p.stdout:
                # convert from byte to string
                cache = line.strip().decode("utf-8")
                # get rid of multiple whitespaces
                cache = sub(' +', ' ', cache).split(" ")

                Popen(["kdestroy -c "+ cache[1]], shell=True)

        else:
            # get remaining time on the existing ticket
            p = Popen(["klist","-A"],stdout=PIPE)
            for i in range(4):
                p.stdout.readline()

            # convert from byte to string
            ticket_time_info = p.stdout.readline().strip().decode("utf-8")\
                               .split("  ")[1]
            print(ticket_time_info)
            ticket_date, ticket_time = ticket_time_info.split(" ")
            ticket_date = ticket_date.split("/")
            ticket_time = ticket_time.split(":") # hour minute second

            # convert string to integer
            ticket_date = list(map(int, ticket_date))
            if ticket_date[2] < 2000:
                ticket_date[2] += 2000
            ticket_time = list(map(int, ticket_time))

            # get current time
            now = datetime.datetime.now()

            # convert to datetime
            if now.year == ticket_date[2] and \
               now.month == ticket_date[1]:

               ticket = datetime.datetime(year = ticket_date[2],
                                          month = ticket_date[1],
                                          day = ticket_date[0],
                                          hour = ticket_time[0],
                                          minute = ticket_time[1],
                                          second = ticket_time[2])

            elif now.year == ticket_date[2] and \
                 now.month == ticket_date[0]:

               ticket = datetime.datetime(year = ticket_date[2],
                                          month = ticket_date[0],
                                          day = ticket_date[1],
                                          hour = ticket_time[0],
                                          minute = ticket_time[1],
                                          second = ticket_time[2])
            else:
                raise ValueError(ticket_date,now.year)

            # calculate remaining time of ticket (is always smaller than one day)
            remaining_time = ticket - now

            # currently remaining time (which is currently a datetime object)
            # to seconds
            remaining_time = remaining_time.seconds - 3600

            if remaining_time > 0:
                # wait
                request_time = now+datetime.timedelta(seconds = remaining_time)
                print("Wait from",strftime("%a, %d %b %Y %H:%M:%S",
                      now.timetuple()), "to", strftime("%a, %d %b %Y %H:%M:%S",
                      request_time.timetuple()))

                sleep(remaining_time)

            # write file requesting the management script to ssh to this machine
            # to create a new ticket
            with open(machine+"-ssh-request.txt", 'w') as sshfile:
                sshfile.write(machine)

            print("Request filed: ", strftime("%c"))

            # wait until new ticket was issued
            while 1:
                print("Waiting for request fulfillment:", strftime("%c"))
                if os.path.isfile(machine+"-ssh-request.txt"):
                    sleep(30)
                else:
                    break

    return

if __name__ == "__main__":

    check_ticket()
