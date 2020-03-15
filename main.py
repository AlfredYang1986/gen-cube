# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 19:57:27 2020

@author: Alfred Yang
"""

import os
from dataCleaning import ExcelData
from cube import PhCube
from testFunctions import validate_input_data


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

validate_input_data(frame, dimensions, 0)

"""
2. gen cube
"""
cube = PhCube(frame_path=frame, dimension_path=dimensions, output_path=output)
cube.gen_cuboids()
cube.gen_cube_data()
cube.gen_final_result()
