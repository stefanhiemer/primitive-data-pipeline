#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

To Do read_log
 -

@author: Stefan Hiemer
"""

import os
import subprocess


if __name__ == "__main__":
    subprocess.Popen(['ssh ww8stud9.ww.uni-erlangen.de pwd'],
                     stdin = None,
                     stdout = subprocess.PIPE,
                     stderr = subprocess.PIPE,
                     shell = True)
