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

from numpy import ndarray
from multiprocessing import Pool

def _check_shape_type(data,name):
    """
    """
    if isinstance(data,list):
        pass
    elif isinstance(data,ndarray):
        if len(data.shape) == 1:
            data = data.tolist()
        elif len(data.shape) == 2 and data.shape[0] == 1:
            data = data[0,:].tolist()
        elif len(data.shape) == 2 and data.shape[1] == 1:
            data = data[:,0].tolist()
        else:
            raise ValueError("If "+name+" is np.ndarray must be one dimensional or two dimensional with one redundant dimension.")
    else:
        raise TypeError(name+" must be either list or np.ndarray.")

    return data

def check_shape_type(times, job_names, job_files):
    """

    """

    times = _check_shape_type(times,"times")
    job_names = _check_shape_type(job_names,"job_names")
    job_files = _check_shape_type(job_files,"job_files")

    if not len(times) == len(job_names) == len(job_files):
        raise ValueError("times, job_names, job_files must have same length.")

    return times, job_names, job_files

def create_jobs(times = None,
                job_names = None,
                job_files=None):
    """
    """
    #
    if times is None and job_names is None and job_files is None:
        #
        os.chdir("jobs")

        #
        job_files = glob.glob("*.sh")

        # get job information
        with Pool() as p:
            _ = p.map(read_jobfile,job_files)

        # extract information
        times = [t for t,name in _]
        job_names = [name for t,name in _]

        os.chdir("..")

    # check shape
    times, job_names, job_files = check_shape_type(times,
                                                   job_names,
                                                   job_files)
    #
    with open("jobs.json","w") as f:
        json.dump({"time": times,
                   "name": job_names,
                   "file": job_files},
                   f)

    return

def read_jobfile(jobfile):
    with open(jobfile,'r') as f:

        # skip three lines
        [f.readline() for i in range(3)]

        # read in time in seconds
        time = int(f.readline()[2:].strip())

        # skip two lines
        [f.readline() for i in range(2)]

        # read job name
        job_name = f.readline()[2:].strip()

    return time,job_name

def append_jobs(times, job_names, job_files):

    # check shape
    times, job_names, job_files = check_shape_type(times,
                                                   job_names,
                                                   job_files)

    if os.path.isfile("jobs.json"):
        with open("jobs.json","r+") as f:
            old =  json.load(f)

            json.dump({"time": times+old["time"],
                       "name": job_names+old["name"],
                       "file": job_files+old["file"]},
                       f)
    else:
        with open("jobs.json","w") as f:
            json.dump({"time": times,
                       "name": job_names,
                       "file": job_files},
                       f)

    return

def create_test_jobs():
    """
    Creates ten jobs who all create another text file. Simple check that
    job files are created and passed to the done directory as well as the
    creation of the text files.
    """
    os.chdir("jobs")

    for i in range(10):

        with open('test-job-'+str(i)+'.sh','w') as f:

            f.write("#!/bin/bash\n")
            f.write("#\n")
            f.write("# time in seconds with the use of a single processor\n")
            f.write("# 10\n")
            f.write("\n")
            f.write("# job name\n")
            f.write("# test_job_"+str(i)+"\n")
            f.write("\n")
            f.write("# test program\n")
            f.write("touch test"+str(i)+".txt\n")

    os.chdir("..")

    # wait ten seconds for jobs to be done
    from time import sleep
    create_jobs()
    import sys
    sys.exit()
    sleep(30)

    # check that the files have been created
    done = [len(glob.glob('test'+str(i)+'.txt')) for i in range(10)]
    assert all(done), "Not all files have been created."

    # check for done jobs in the done folder after 10 seconds.
    os.chdir("jobs/done")
    done = [len(glob.glob('test-job-'+str(i)+'.sh')) for i in range(10)]
    assert all(done), "Not all job scripts found in the done directory."


    os.chdir("..")
    return


if __name__ == "__main__":
    #create_test_jobs()
    create_jobs()
