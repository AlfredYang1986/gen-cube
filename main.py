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
from dataCleaning import ExcelData
from cube import PhCube


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

cube = PhCube(frame_path=frame, dimension_path=dimensions, output_path=output)
cube.gen_cuboids()
cube.gen_cube_data()
