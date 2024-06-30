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
import json
import subprocess
import time
from multiprocessing import cpu_count



# get computer name
process = subprocess.run(['lshw', '-json'], check=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         universal_newlines=True)
lshw_information = json.loads(process.stdout)
machine_name = lshw_information['id']

def start_job(nproc=None,timelimit=900):
    """
    nproc: int, number of processors
    timelimit: int, number of seconds which the job may maximally last.
    timelimit: int, number of seconds which the job may maximally last.
    """

    retraction_times = [1,2,5,10,15,20,25,30,40,50,60]

    if nproc is None:
        nproc = cpu_count()

    # ask for job
    with open(machine_name+"_jobquery.json",'w') as f:
        json.dump({"nproc": nproc, "timelimit": timelimit},f)

    # wait for job. if no job available with 60 sec retract query
    job_found=False
    print("Waiting for job.")
    for i in range(11):

        if os.path.isfile(machine_name+"_job.json"):
            job_found=True
            print("Job received.")
            break
        else:
            time.sleep(retraction_times[i])

    if not job_found:
        print("No job available.")
        os.remove(machine_name+"_jobquery.json")
        return

    # load job information
    with open(machine_name+"_job.json",'r') as f:
        job = json.load(f)

    # remove job file
    os.remove(machine_name+"_job.json")

    # move in job directory
    os.chdir('jobs')

    # start job
    wall_time = time.time()
    try:
        subprocess.check_output(["bash",job["file"]],
                                stderr=subprocess.STDOUT,
                                universal_newlines=True)
        job["message"] = "success"
    except subprocess.CalledProcessError as err:
        job["message"] = err

    job["wall time"] = time.time() - wall_time
    job["machine"] = machine_name

    # move jobfile in the folder of done jobs
    subprocess.run(["mv",job["file"],"done/"])

    # move out of job directory
    os.chdir('..')

    # write job summary
    with open(machine_name+"_report.json","w") as f:
        json.dump(job,f)

    return

def get_idle_times():
    """
    Get list how long each user has not done anything by use of who -u.
    """
    # get information about logged in users from the command who.
    # returns one big string
    user_infos = subprocess.run(["who","-u"],stdout=subprocess.PIPE)\
                 .stdout.decode("utf8")

    # split string into list of lists. Each list is a user plus its infos.
    user_infos = [user.split() for user in user_infos.split("\n")][:-1]

    # conversion to set eliminates users which are logged in multiple times
    user_names = set([user[0] for user in user_infos])

    # convert set back to list as the unsortedness is unwanted
    user_names = list(user_names)

    # get minimum idle time for each user or the question mark.
    idle_times = []
    for user_name in user_names:
        idle = [info[4] for info in user_infos if info[0] is user_name]

        # The question mark indicates a user logged in locally. For the moment
        # pretend that every user logged in locally is also permanent active.
        if "?" in idle:
            idle_times.append(0)

        # indicates activity within the last minute
        elif "." in idle:
            idle_times.append(0)

        # append minimum idle time
        else:
            # split time in hours and minutes
            idle = [time.split(":")for time in idle]
            # convert to seconds
            idle = [int(time[0])*3600 + int(time[1]) * 60 for time in idle]
            # find minimum time
            idle_times.append(min(idle))

    return idle_times

def get_nusers():

    return int(subprocess.run(["users | wc -l"],
                          stdout=subprocess.PIPE,shell=True)\
           .stdout.decode("utf8"))

def run_client(block_lift=86400,
               sleep_time=150,
               life_time=None):
    """
    block_lift: int, number of seconds which the block may maximally last.
    sleep_time: int, number of seconds which the computer waits.
    """

    # gives the user thirty seconds to get out of the tmux session and leave the
    # computer
    time.sleep(10)

    # initialize variables needed for deciding different cases
    timer_running = False
    prev_job = False
    block_time = 0

    # set off life timer
    if life_time is not None:
        start_time = time.time()
    else:
        start_time = None

    while 1:

        # check how many users are logged in
        n_users = get_nusers()

        # get computational load over last minute and over last five minutes
        load = os.getloadavg()[:2]

        # check if computer is blocked
        blocked = os.path.isfile(machine_name)

        # check if timer for blocking is running
        if timer_running:
            # lift blockade after 24 hours and switch off timer
            if time.time() - block_time > block_lift:
                blocked = False
                os.remove(machine_name)
                timer_running = False

        if blocked and not timer_running:
            timer_running = True
            block_time = time.time()

        # if no users logged in and no noticeable load, run jobs-
        # Also run if the client has previously run a job and no user is
        # present as in this case the entire load stems from the client
        # running a job.
        if n_users == 0 and load < (0.05, 0.05) or n_users == 0 and prev_job:

            # reset job flag
            prev_job = False

            # run jobs as long as no user connects or the lifetime is exceeded
            while 1:
                print("No users detected. Start job:",time.strftime("%c"))
                start_job()

                if get_nusers() != 0:
                    break
                elif life_time is not None:
                    if life_time < (time.time()-start_time):
                        break

        # no users logged in, but load detected. This means that either updates
        # are running or someone uses tmux to do stuff.
        elif n_users == 0 and load > (0.05, 0.05):

            # check wether it's noise
            if load[0] < 0.3:
                print("Computer unoccupied, but load detected. Check for noise: ",
                      time.strftime("%c"))
                time.sleep(60)
                if os.getloadavg()[0] < 0.3:
                    print("Load deemed to be noise. Start job: ",time.strftime("%c"))
                    start_job()
                    prev_job = True
                else:
                    print("Load deemed not to be noise. Wait 15 min: ",
                           time.strftime("%c"))
                    # check processor usage

                    # submit job with reduced number of processors

                    # wait
                    time.sleep(sleep_time)

        elif n_users != 0 or blocked:
            # has someone idle time if he has submitted a job?
            # if yes. get idle times
            # check processor usage

            # start job with reduced processor count

            #
            if os.getloadavg()[:2] < (0.05, 0.05):
                print("Computer occupied. No load detected.")
                print("Waiting to find out wether user is sleeping: ",
                       time.strftime("%c"))

                # wait
                time.sleep(sleep_time)

                if os.getloadavg()[:2] < (0.05, 0.05):
                    print("User sleeps. Start job:",time.strftime("%c"))
                    start_job()
                    # sleep for five seconds to not taint the load average
                    # for the next 5 minutes
                    prev_job = True
                    time.sleep(5)
            else:
                # wait
                print("User does not sleep. Wait:" ,time.strftime("%c"))
                time.sleep(sleep_time)
        else:
            print("Unforseen Case.")
            import sys
            sys.exit()


        print("Cycle finished: ",time.strftime("%c"))
        if life_time is not None:
            if life_time < (time.time()-start_time):
                print("Life time of client exceeded. Intended breakout of loop: ",
                       time.strftime("%c"))
                break
    return



if __name__ == "__main__":

    run_client()
