# -*- coding: utf-8 -*-
################################################################################
#The following code is used to make a focus map for the foils. The first of
#which is calc_coords. This calculates a list of points that the
#SEM stage will move to. It's important to make sure the stage won't
#move the samples too close to either the chamber edges or the
#detectors. 

#The next one is the FocusMap function. This function is
#the one that actually moves the stage and finds the appropriate WD at
#each point calculated in calc_coords. It then calculates the sample
#height using the WD and adds this value as a z-coordinate in the
#previous list. Lastly, the function creates a csv file in the
#present working directory that contains all the points the SEM will
#move to. This csv file is writable and its values can be changed
#should the user wish to change numbers.

#Lastly, the main important function is the TakeImgs function. This 
#one reads the csv file created (or a custom csv file made by the
#user) and creates a Python-list from it. Because it becomes readable,
#the function then has the SEM move the stage to those locations and 
#calls other pre-written but slightly modified functions to collect
#images.

#See documentation for more details.



from __future__ import print_function
print('Start')
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'remote'))
import time
import sem
import struct
from sem_v3_lib import *
import numpy as np
#from scipy import misc
import csv
import ast


#Connect to the SEM SharkSEM interface.
m = sem.Sem()
conn = m.Connect('localhost', 8300)
print("Connection Established.")

#WD_0 = m.GetWD()
#print("Working Distance=",WD_0)

stg = m.StgGetPosition()
print("Z Stage Position =",stg[2])
