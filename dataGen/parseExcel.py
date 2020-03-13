# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 19:57:27 2020

@author: Alfred Yang
"""

import pandas as pd


class ExcelData(object):
    def __init__(self, path):
        self.path = path
        self.excel = pd.ExcelFile(self.path)
        self.df = None

    def excel_data_2_frames(self, path, sheet_name, arr_not_null):
        # 1. read data from excel
        df = self.excel.parse(sheet_name=sheet_name)

        # 2. clean the null in the not null column
        for index_col in arr_not_null:
            df = df[~df["PROVINCE_NAME"].isnull()]

        if self.df is None:
            self.df = df
        else:
            self.df = self.df.append(df).reset_index(drop=True)

        return df

    def query_current_frames(self):
        return self.df

    def current_data_2_frames(self):
        self.df.to_csv(path_or_buf="./data/result.csv", index=False, encoding="utf-8")
