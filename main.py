import pandas as pd

from dataGen import ExcelData

path = "./data/data.xlsx"
# path = "./data/data1.xlsx"
data = ExcelData(path)
data.excel_data_2_frames(path, sheet_name="10", arr_not_null=["PROVINCE_NAME"])
data.excel_data_2_frames(path, sheet_name="11", arr_not_null=["PROVINCE_NAME"])
data.excel_data_2_frames(path, sheet_name="12", arr_not_null=["PROVINCE_NAME"])
data.current_data_2_frames()
