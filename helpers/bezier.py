###############################################################################
##                                                                           ##
## This file contains object definitions for geometric parametrization and   ##
## meshing for ducts.                                                        ##
##                                                                           ##
## Original Author: Alexandre Capitao Patrao, 2022-03-17,                    ##
## capitao@chalmers.se                                                       ##
## Modified by: Erik Hasselwander, 2026-01-20                                ##
## erik.hasselwander@chalmers.se                                             ##
###############################################################################

import numpy as np
from scipy.special import binom
from pathlib import Path
import subprocess
import os
import sys

import matplotlib.pyplot as plt

def bezierCurve(bezierPoints, numPoints=100, selfIntersectFlag=False):
    tVal = np.linspace(0, 1, num=numPoints)
    pAnalytic = np.zeros((len(tVal), len(bezierPoints[0])))
    order = len(bezierPoints) - 1
    for k in range(len(bezierPoints[0])):
        for j in range(len(tVal)):
            for i in range(order + 1):
                t = tVal[j]
                pAnalytic[j][k] = (
                    pAnalytic[j][k]
                    + binom(order, i)
                    * (1 - t) ** (order - i)
                    * t**i
                    * bezierPoints[i][k]
                )

    if selfIntersectFlag:
        foundIntersection, intersection = checkIfCurveSelfIntersects(pAnalytic)
        if foundIntersection:
            print("\t\tBezier curve self-intersects!")
        return pAnalytic
    else:
        return pAnalytic


def checkIfCurveSelfIntersects(curve):
    np.seterr(divide="ignore")

    foundIntersection = False
    intersection = None
    for i in range(len(curve) - 1):  # loop through all curve segments, pick segment 1
        # pick segment 1
        p1 = curve[i, :]
        p2 = curve[i + 1, :]

        for j in range(
            len(curve) - 1
        ):  # loop through all curve segments, pick segment 2
            if i != j:
                # pick segment 2
                p3 = curve[j, :]
                p4 = curve[j + 1, :]

                # check if intersect
                # https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
                r = p2 - p1
                s = p4 - p3
                p = p1
                q = p3
                t = np.cross((q - p), s) / np.cross(r, s)
                u = np.cross((q - p), r) / np.cross(r, s)

                if t > 0 and t < 1 and u > 0 and u < 1:
                    intersection = p + t * r
                    foundIntersection = True
                    print("\t\tCurve self-intersects!")
                    break

            if abs(i - j) == 1:
                # neighbour segment, wont intersect except at ends of curves, so do nothing
                pass
            else:
                # same segment as segment 1
                pass

        # break outer loop in case inner loops finds self-intersection
        if foundIntersection:
            break

    return foundIntersection, intersection
