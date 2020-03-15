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
            df = df[~df[index_col].isnull()]

        # 3. fill the QUARTER
        df.loc[:, "QUARTER"] = df.loc[:, "MONTH"].apply(lambda x: int((x - 1) / 3) + 1)

        # 4. fill the MKT data with company name
        df.loc[:, "MKT"] = df.loc[:, "COMPANY"].apply(lambda x: x)

        # 6. for every measure should not have null or NaN
        df = df.fillna(0.0)
        # df.loc[:, "SALES_QTY"] = df.loc[:, "SALES_QTY"].apply(lambda x: 0.0 if x.isnull() else x)
        # df.loc[:, "SALES_VALUE"] = df.loc[:, "SALES_VALUE"].apply(lambda x: 0.0 if x.isnull() else x)

        # 7. fill a column with COUNTRY, which represents the highest level of geo dimension
        df.loc[:, "COUNTRY_NAME"] = "CHINA"

        # 5. prune the data with only which need
        df = df[["YEAR", "QUARTER", "MONTH",
                 "COUNTRY_NAME", "PROVINCE_NAME", "CITY_NAME",
                 "COMPANY", "MKT", "MOLE_NAME", "PRODUCT_NAME",
                 "SALES_QTY", "SALES_VALUE"]]

        if self.df is None:
            self.df = df
        else:
            self.df = self.df.append(df).reset_index(drop=True)

        return df

    def query_current_frames(self):
        return self.df

    def current_data_2_frames(self, output_path):
        self.df.to_csv(path_or_buf=output_path, index=False, encoding="utf-8")
