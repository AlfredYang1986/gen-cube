
import os
import sys
import json
import pandas as pd


def validate_input_data(frame_path, dimension_path, run_test):
    if run_test and os.path.isfile(frame_path):
        data = pd.read_csv(frame_path)
        with open(dimension_path, "r") as f:
            dm = json.loads(f.read())

        for dimension in dm["dimensions"]:
            for hierarchy in dimension["hierarchy"]:
                if len(data[data[hierarchy].isnull()]) > 0:
                    sys.stderr.write("Every dimensions should have no null or NaN")
                    exit(-1)

        for measure in dm["measures"]:
            if len(data[data[measure].isnull()]) > 0:
                sys.stderr.write("Every measure should have no null or NaN")
                exit(-1)
