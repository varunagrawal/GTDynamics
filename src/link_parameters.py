#!/usr/bin/env python
import numpy as np
from math import pi

class LinkParameters_PUMA():
    """
    Denavit-Hartenberg parameters and
    input values for PUMA manipulator
    """
    def __init__(self):
        #Puma Kinematic Parameters and Inputs
        #joint offsets       0...n+1 (first element ignored)
        self.dh_d = np.array([0, 1, 0.2435, -0.0934, 0.4331, 0, 0.2000, 0])        
        #joint angles        0...n+1 (first element ignored) 
        self.dh_t = np.array([0, 1, 2, 3, 4, 5, 6, 90/5.])*( 5)*pi/180.
        #link common normals 0...n+1 (last  element ignored)
        self.dh_a = np.array([0, 0, 0.4318, 0.0203, 0, 0, 0, 0])           
        #link twist angles   0...n+1 (last  element ignored)
        self.dh_f = np.array([0, -90, 0, -90, 90, -90, 90, 0])*pi/180.  
        #{R/P/G/B/N} = {Revolute/Prismatic/Gripper/Base/None} joint type
        self.dh_j = np.array(['B', 'R', 'R', 'R', 'R', 'R', 'R', 'G'])      

        #joint velocities    0...n+1 (first element ignored)
        self.dh_td = np.array([0, 1, 2, 3, 4, 5, 6, 0])*(-5)*pi/180.
        #joint accelerations 0...n+1 (first element ignored)
        self.dh_tdd = np.array([0, 1, 2, 3, 4, 5, 6, 0])*(10)*pi/180.

        #Puma Dynamics Parameters
        #link masses (first and last element are ignored)
        self.dh_m = np.array([0, 0, 17.40, 4.80, 0.82, 0.34, 0.09, 0])
        #ith center-of-mass location in frame i 0...n+1 (first and last elements ignored)
        self.dh_com = np.array([[0, 0, 0.068, 0, 0, 0, 0, 0],         
                        [0, 0, 0.006, -0.070, 0, 0, 0, 0], 
                        [0, 0, -0.016, 0.014, -0.019, 0, 0.032, 0]])
        #ith principal inertias i 0...n+1 (first and last elements ignored)
        self.dh_pI = np.array([[0, 0, 0.130, 0.066, 0.0018, 0.00030, 0.00015, 0],              
                        [0, 0, 0.524, 0.0125, 0.00180, 0.00030, 0.00015, 0],
                        [0, 0.35, 0.539, 0.086, 0.00130, 0.00040, 0.00004, 0]])
        # torque applied on each joints (frist and last elements ignored)
        self.dh_tq = np.array([0, 0.626950752326773,	-34.8262338725151,	1.02920598714973,
                            -0.0122426673731905,	0.166693973271978,	7.20736555357164e-05, 0])

class LinkParameters_RR():
    """
    Denavit-Hartenberg parameters and
    input values for RR link manipulator
    """
    def __init__(self):
        #RR manipulator Kinematic Parameters and Inputs
        #joint offsets       0...n+1 (first element ignored)
        self.dh_d = np.array([0, 0, 0, 0])          
        #joint angles        0...n+1 (first element ignored) 
        self.dh_t = np.array([0, 0, 0, 0])
        #link common normals 0...n+1 (last  element ignored)
        self.dh_a = np.array([0, 2, 2, 0])         
        #link twist angles   0...n+1 (last  element ignored)
        self.dh_f = np.array([0, 0, 0, 0])
        #{R/P/G/B/N} = {Revolute/Prismatic/Gripper/Base/None} joint type
        self.dh_j = np.array(['B', 'R', 'R', 'G'])      

        #joint velocities    0...n+1 (first element ignored)
        self.dh_td = np.array([0, 1, 1, 0])
        #joint accelerations 0...n+1 (first element ignored)
        self.dh_tdd = np.array([0, 0, 0, 0])

        #Puma Dynamics Parameters
        #link masses (first and last element are ignored)
        self.dh_m = np.array([0, 1, 1, 1, 1, 1, 1, 0])
        #ith center-of-mass location in frame i 0...n+1 (first and last elements ignored)
        self.dh_com = np.array([[0, 1, 1, 0],         
                        [0, 0, 0, 0], 
                        [0, 0, 0, 0]])
        #ith principal inertias i 0...n+1 (first and last elements ignored)
        self.dh_pI = np.array([[0, 0, 0, 0],              
                        [0, 1/6., 1/6., 0],
                        [0, 1/6., 1/6., 0]])
        # torque applied on each joints (frist and last elements ignored)
        self.dh_tq = np.array([0, 0, 0, 0])
