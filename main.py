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
output = "./data/frames/"

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

data = pd.read_csv(frame)

if test and os.path.isfile(frame):
    # data = pd.read_csv(frame)
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
# print dms
# 1.1 for n-dimension should have 2^n cuboids (or panels)
#     in this place I am using the combination (排列组合)
cuboids = []
for ld in range(len(dms) + 1):
    for cuboid in itertools.combinations(dms, ld):
        # 1.2 construct bitmap dimension indexing
        #     also can be save the last when you want to build indexing of the cuboids
        cuboids.append(cuboid)
# print cuboids

# 2. for all cuboid, build lattices base on the dimension's concept hierarchies
for cuboid in cuboids:
    # print cuboid
    # 2.1 create metadata for the cuboid
    #    2.1.1 the name of the cuboid for now only
    dimensions_names = []
    for dimension in cuboid:
        dimensions_names.append(dimension["name"])
    # print dimensions_names
    dimension_count = len(cuboid)
    cuboid_name = "apex" \
        if dimension_count == 0 \
        else "base" if dimension_count == len(dms) \
        else str(dimension_count) + "-D-" + "-".join(dimensions_names)
    # print cuboid_name

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

    if len(hierarchies) == 0:
        # print "apex"
        # 3.2 for apex lattice, replace dimension with * character
        #     star node
        all_hierarchies = []
        for dm in dms:
            for her in dm["hierarchy"]:
                all_hierarchies.append(her)
        for col in all_hierarchies:
            data.loc[:, "apex"] = "alfred"
            apex = data.groupby(["apex"])["SALES_QTY", "SALES_VALUE"].sum()
            # 3.3 fill dimension columns
            for hier in all_hierarchies:
                apex[hier] = "*"
            # 3.4 fill cube metadata
            apex["dimension.name"] = "apex"
            apex["dimension.value"] = "*"
            apex.to_csv(output + cuboid_name + ".csv")
    elif len(hierarchies) == len(dms):
        # print "base"
        data.to_csv(output + cuboid_name + ".csv")
    else:
        for cartesian_hierarchies in cartesian(hierarchies):
            # print "alfred"
            # print cartesian_hierarchies
            # 4. for calculation lattice in  n-dimension cuboids,
            #    group by the higher level hierarchy in such dimension
            group_hierarchy = []
            for tmp_hierarchy in cartesian_hierarchies:
                for tmp_dimension in cuboid:
                    try:
                        for index in range(tmp_dimension["hierarchy"].index(tmp_hierarchy) + 1):
                            group_hierarchy.append(tmp_dimension["hierarchy"][index])
                    except ValueError, e:
                        # do nothing
                        print "not in the array"

            # print group_hierarchy
            data_lattice = data.groupby(group_hierarchy)["SALES_QTY", "SALES_VALUE"].sum().reset_index()
            # print data_lattice.reset_index()

            # 4.1 fill the other
            fill_hierarchies = []
            for dm in dms:
                for her in dm["hierarchy"]:
                    if her not in group_hierarchy:
                        fill_hierarchies.append(her)
            # print fill_hierarchies

            for fill_hier in fill_hierarchies:
                data_lattice[fill_hier] = "*"

            # 4.4 fill cube metadata
            data_lattice["dimension.name"] = cuboid_name
            data_lattice["dimension.value"] = ""

            for condi in cartesian_hierarchies:
                data_lattice.loc[:, "dimension.value"] = \
                    data_lattice.loc[:, "dimension.value"].apply(lambda x: str(x)) + "," + \
                    data_lattice.loc[:, condi.encode("utf8")].apply(lambda x: condi.encode("utf8") + ":" + str(x))

            data_lattice.to_csv(output + cuboid_name + "-".join(cartesian_hierarchies) + ".csv")

