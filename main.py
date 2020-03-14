# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 19:57:27 2020

@author: Alfred Yang
"""
import itertools
import json
import os
import sys

import pandas as pd
import numpy as np
from dataGen import ExcelData
from utils import cartesian


"""
Parameters
    ----------
    path : string, path of the data excel
    frame: string, path of frame after data cleaning
    dimensions: string, path of define file of dimensions and measures
"""
path = "./data/data.xlsx"
frame = "./data/frames/origin.csv"
dimensions = "./data/define/example.json"

"""
0. test the data clean functions
"""
test = 1
# if test:
#     path_test = "./data/data1.xlsx"
#     data = ExcelData(path_test)
#     tmp = data.excel_data_2_frames(
#         path_test, sheet_name="10", arr_not_null=["PROVINCE_NAME"])
#     print tmp

"""
1. data cleaning and data integration
"""
if not os.path.isfile(frame):
    data = ExcelData(path)
    data.excel_data_2_frames(path,
                             sheet_name="10",
                             arr_not_null=["PROVINCE_NAME", "MOLE_NAME", "PRODUCT_NAME"])
    data.excel_data_2_frames(path,
                             sheet_name="11",
                             arr_not_null=["PROVINCE_NAME", "MOLE_NAME", "PRODUCT_NAME"])
    data.excel_data_2_frames(path,
                             sheet_name="12",
                             arr_not_null=["PROVINCE_NAME", "MOLE_NAME", "PRODUCT_NAME"])
    data.current_data_2_frames(output_path=frame)


"""
1.5. test if the finally data frame is good enough to construct data cube
"""
if test and os.path.isfile(frame):
    data = pd.read_csv(frame)

    # 1. every dimension should have no null or nan
    with open(dimensions, "r") as f:
        dm = json.loads(f.read())

    for dimension in dm["dimensions"]:
        for hierarchy in dimension["hierarchy"]:
            if len(data[data[hierarchy].isnull()]) > 0:
                sys.stderr.write("Every dimensions should have no null or NaN")
                exit(-1)

    for measure in dm["measures"]:
        if len(data[data[measure].isnull()]) > 0:
            print measure
            sys.stderr.write("Every measure should have no null or NaN")
            exit(-1)

"""
2. construction of data dimension 
"""
with open(dimensions, "r") as f:
    dm = json.loads(f.read())

dms = dm["dimensions"]

# 1. for all dimensions in these example is 3-D cuboid or base cuboid
print len(dms)
print 2 ** len(dms)
# 1.1 for n-dimension should have 2^n cuboids (or panels)
#     in this place I am using the combination (排列组合)
cuboids = []
for ld in range(len(dms) + 1):
    for cuboid in itertools.combinations(dms, ld):
        # 1.2 construct bitmap dimension indexing
        #     also can be save the last when you want to build indexing of the cuboids
        cuboids.append(cuboid)

print cuboids

# 2. for all cuboid, build lattices base on the dimension's concept hierarchies
for cuboid in cuboids:
    print cuboid
    # 2.1 create metadata for the cuboid
    #    2.1.1 the name of the cuboid for now only
    dimensions_names = []
    for dimension in cuboid:
        dimensions_names.append(dimension["name"])
    print dimensions_names
    dimension_count = len(cuboid)
    cuboid_name = "apex" \
        if dimension_count == 0 \
        else "base" if dimension_count == len(dms) \
        else str(dimension_count) + "-D-" + "-".join(dimensions_names)
    print cuboid_name

    # 3. construction for the lattices of the cuboid
    #   3.1 construction all the combination in the dimension concept hierarchies
    #       for 1-D dimension, the lattice number of the cuboid is calculated by the number of the concept hierarchy
    #       for 2-D dimension cuboid, which has n and m concept hierarchy for each dimension especially,
    #       the number of the lattices is m * n
    #       in summary, n-dimension with n levels of hierarchies would have n^n lattice.
    #       in this example, we use cartesian to implement
    hierarchies = []
    for har in cuboid:
        hierarchies.append(har["hierarchy"])

    print hierarchies

    if len(hierarchies) == 0:
        print "apex"

    else:
        for cartesian_hierarchies in cartesian(hierarchies):
            print cartesian_hierarchies
