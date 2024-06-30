#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

To Do read_log
 -

@author: Stefan Hiemer
"""

import os
import glob

from time import sleep, gmtime, strftime
from subprocess import Popen, PIPE 

# get machine name
machine = Popen(['hostname'], stdout = PIPE)
machine = machine.stdout.readline().strip().decode("utf-8")

def check_ssh(waiting_time=60):

    while 1:
        print("Checking for Tickets.")
        # check wether any ssh requests are there
        requests = glob.glob("*ssh-request.txt")
        
        # avoid sshing to the machine performing the ticket management.
        if machine+"-ssh-request.txt" in requests:
            requests.remove(machine+"-ssh-request.txt")

        if len(requests) == 0:
            print("No tickets triggered. Time: " + \
                  strftime("%a, %d %b %Y %H:%M:%S", gmtime()))
        else:
            
            for request in requests:
                
                # read adress used for ssh
                try: 
                    with open(request,'r') as file:
                        adress = file.readline()
                # the request has already been fulfilled by another ticket 
                # manager
                except FileNotFoundError:
                    continue
                # ssh to machine in order to trigger a new ticket
                Popen(['ssh ' + adress + ' pwd'],
                      stdin = None,
                      stdout = PIPE,
                      stderr = PIPE,
                      shell = True)
                print("Ticket triggerd at "+adress + ". Time: " + \
                      strftime("%a, %d %b %Y %H:%M:%S", gmtime()))

                #remove request in order to avoid to read the same request twice
                try:
                    os.remove(os.path.join(os.getcwd(),request))
                # this is the case where another manager has already removed 
                # the ssh request.
                except FileNotFoundError:
                    pass
                    
        sleep(waiting_time)
    return


if __name__ == "__main__":
    check_ssh()
