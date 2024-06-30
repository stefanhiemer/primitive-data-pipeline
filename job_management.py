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
from time import sleep
from shutil import rmtree
from time import sleep, strftime
from subprocess import Popen, PIPE

import smtplib
from email.message import EmailMessage

def supervise_machines(file):
    while 1:
        # read mining machines list
        mining_machines = []
        # check if every machine has written the status file
        for machine in mining_machines:
            if os.path.is_file(machine):
                rmtree(machine)
            else:
                # send email to me indicating that some machine died
                msg = EmailMessage()

                # me == the sender's email address
                # you == the recipient's email address
                msg['Subject'] = machine + " died in the process and needs restart"
                msg['From'] = "job-pipeline@fau.de"
                msg['To'] = "Stefan.Hiemer@fau.de"

                # Send the message via our own SMTP server.
                s = smtplib.SMTP('localhost')
                s.send_message(msg)
                s.quit()

                # remove machine from the mining machines list
                mining_machines.remove(machine)


    return

def handle_job_queries(job_queries,jobs,work_in_prog,time_stamp):

    if len(job_queries) != 0:
        print("Query detected.")
        for file in job_queries:

            # read information of the job query
            try:
                with open(file,'r') as f:
                    query = json.load(f)
            except err:

                print(file)
                with open("file","r") as f:
                    for line in f:
                        print(line)
                print(err)
                import sys
                sys.exit()

            # make time estimate
            abs_time_limit = query["timelimit"] * query["nproc"]

            # find job below time limit
            job = None
            for i,time in enumerate(jobs["time"]):
                if time < abs_time_limit:
                    # create new job dictionary
                    job = {}
                    for key in jobs.keys():
                        job = dict(job,**{key: jobs[key][i]})
                    break

            #
            if job is not None:
                # remove query
                os.remove(file)

                # remove job from list
                [jobs[key].pop(i) for key in jobs.keys()]
                with open("jobs.json","w") as f:
                    json.dump(jobs,f)

                # update time stamp
                time_stamp = os.stat("jobs.json").st_mtime

                # write out job details for the work horse
                with open(file.rsplit("_",1)[0]+"_job.json",'w') as f:
                    json.dump(job, f)

                # write job to work in progress
                [work_in_prog[key].append(job[key]) for key in job.keys()]

                with open("jobs-in-progress.json","w") as f:
                    json.dump(work_in_prog,f)

    return jobs, work_in_prog, time_stamp

def supervise_jobs():
    """
    Script that distributes jobs to machines.
    """

    # read initial jobs if exist. Otherwise create dictionary with no jobs,
    # create a json file and wait for new jobs.
    if not os.path.isfile("jobs.json"):
        jobs = {"name": [],"time": []}
        with open("jobs.json","w") as f:
                json.dump(jobs,f)
    else:
        with open("jobs.json","r") as f:
            jobs = json.load(f)

    # construct dictionary for work in progress jobs
    work_in_prog = {}
    if not os.path.isfile("jobs-in-progress.json"):
        for key in jobs.keys():
            work_in_prog = dict(work_in_prog,**{key: []})
    else:
        with open("jobs-in-progress.json","r") as f:
            work_in_prog = json.load(f)

    # check timetamps of the job json file in order to recognize when new jobs
    # have been submitted.
    time_stamp = os.stat("jobs.json").st_mtime

    while 1:

        # check if jobs have changed
        if time_stamp != os.stat("jobs.json").st_mtime:

            # load new jobs
            with open("jobs.json","r") as f:
                jobs = json.load(f)

            time_stamp = os.stat("jobs.json").st_mtime

        # check for reports
        for file in glob.glob("*_report.json"):
            print("Job report detected: ",strftime("%c"))
            # get report data
            with open(file,'r') as f:
                job = json.load(f)

            # bundle job reports
            if os.path.isfile("job_reports.json"):
                print("Append new report to file:",
                      strftime("%c"))
                with open("job_reports.json","r") as f:
                    # load old reports
                    reports = json.load(f)

                # append new report
                [reports[key].append(job[key]) for key in reports.keys()]

                # write new json file.
                with open("job_reports.json","w") as f:

                    # save reports
                    json.dump(reports,f)
            else:
                print("Create new reports dictionary and file: ",
                      strftime("%c"))
                with open("job_reports.json","w") as f:
                    # create new reports dictionary
                    reports = {}
                    for key in job.keys():
                        reports[key] = [job[key]]

                    # save reports
                    json.dump(reports,f)

            # remove job from work in progress
            index = work_in_prog["name"].index(job["name"])
            [work_in_prog[key].pop(index) for key in work_in_prog.keys()]

            # move report file to the done directory
            os.remove(file)

        # if no jobs there wait fifteen seconds
        if len(jobs["name"]) == 0:
            print("No jobs in queque: ",strftime("%c"))
            sleep(15)
            continue

        # answer job queries. Take jobs submitted to a machine out of the jobs
        # dictionary and move it to the work in prog dictionary. Update the
        # time stamp of the job json file.
        jobs,work_in_prog,time_stamp = handle_job_queries(
                                               glob.glob("*_jobquery.json"),
                                               jobs,
                                               work_in_prog,
                                               time_stamp)



        print(str(len(jobs["name"]))+" jobs remaining.")
        print(str(len(work_in_prog["name"]))+" jobs in progress: ",
              strftime("%c"))
        sleep(1)

    return

if __name__ == "__main__":
    supervise_jobs()
