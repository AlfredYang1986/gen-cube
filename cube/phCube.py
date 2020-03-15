# coding=utf-8
"""
Created on Fri Mar 13 19:57:27 2020

@author: Alfred Yang
"""

import pandas as pd
import itertools
from functions import cartesian
import uuid
import os
from phDimension import PhDimension


class PhCube(object):
    def __init__(self, frame_path, dimension_path, output_path):
        self.data = pd.read_csv(frame_path)
        self.dms = PhDimension(dimension_path)
        # self.all_hierarchies = self.dms.gen_all_hierarchies()
        self.cuboids = []
        self.job_id = str(uuid.uuid4())
        os.mkdir(output_path + self.job_id)
        self.output = output_path + self.job_id + "/"

    def gen_cuboids(self):
        if len(self.cuboids) > 0:
            self.cuboids = []

        for ld in range(len(self.dms.get_dimensions()) + 1):
            # 1. for all dimensions in these example is 3-D cuboid or base cuboid
            # 1.1 for n-dimension should have 2^n cuboids (or panels)
            #     in this place I am using the combination (排列组合)
            for cuboid in itertools.combinations(self.dms.get_dimensions(), ld):
                # 1.2 construct bitmap dimension indexing
                #     also can be save the last when you want to build indexing of the cuboids
                self.cuboids.append(cuboid)

        return self.cuboids

    # 2. for all cuboid, build lattices base on the dimension's concept hierarchies
    def gen_cube_data(self):
        for cuboid in self.cuboids:
            self.gen_cuboids_data(cuboid)

    def gen_cuboids_data(self, cuboid):
        # 2.1 create metadata for the cuboid
        #    2.1.1 the name of the cuboid for now only
        def gen_cuboid_name():
            dimensions_names = []
            for dimension in cuboid:
                dimensions_names.append(dimension["name"])
            # print dimensions_names
            dimension_count = len(cuboid)
            return "apex" \
                if dimension_count == 0 \
                else "base" if dimension_count == len(self.dms.get_dimensions()) \
                else str(dimension_count) + "-D-" + "-".join(dimensions_names)

        # 3. construction for the lattices of the cuboid
        #   3.1 construction all the combination in the dimension concept hierarchies
        #       for 1-D dimension, the lattice number of the cuboid is calculated by the number of the concept hierarchy
        #       for 2-D dimension cuboid, which has n and m concept hierarchy for each dimension especially,
        #       the number of the lattices is m * n
        #       in summary, n-dimension with n levels of hierarchies would have n^n lattice.
        #       in this example, we use cartesian to implement
        def gen_cur_hierarchies():
            result = []
            for har in cuboid:
                result.append(har["hierarchy"])
            return result

        # 3.2 for apex lattice, replace dimension with * character
        #     star node
        def gen_apex_lattice():
            all_hierarchies = self.dms.get_all_hierarchies()
            # for col in all_hierarchies:
            self.data.loc[:, "apex"] = "alfred"
            apex = self.data.groupby(["apex"])["SALES_QTY", "SALES_VALUE"].sum()
            # 3.3 fill dimension columns
            for hier in all_hierarchies:
                apex[hier] = "*"
            # 3.4 fill cube metadata
            apex["dimension.name"] = "apex"
            apex["dimension.value"] = "*"
            apex = apex.reset_index(drop=True)
            apex.to_csv(self.output + cuboid_name + ".csv")

        def gen_base_lattice():
            self.data.to_csv(self.output + cuboid_name + ".csv")

        # 4. for calculation lattice in  n-dimension cuboids,
        #    group by the higher level hierarchy in such dimension
        def gen_dimension_lattice():
            for cartesian_hierarchies in cartesian(hierarchies):
                group_hierarchy = []
                for tmp_hierarchy in cartesian_hierarchies:
                    for tmp_dimension in cuboid:
                        try:
                            for index in range(tmp_dimension["hierarchy"].index(tmp_hierarchy) + 1):
                                group_hierarchy.append(tmp_dimension["hierarchy"][index])
                        except ValueError, e:
                            print "not in the array"
                data_lattice = self.data.groupby(group_hierarchy)["SALES_QTY", "SALES_VALUE"].sum().reset_index()
                # 4.1 fill the other
                fill_hierarchies = []
                for dm in self.dms.get_dimensions():
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
                data_lattice.to_csv(self.output + cuboid_name + "-"
                                    + "-".join(cartesian_hierarchies) + ".csv")

        cuboid_name = gen_cuboid_name()
        hierarchies = gen_cur_hierarchies()

        if len(hierarchies) == 0:
            gen_apex_lattice()
        elif len(hierarchies) == len(self.dms.get_dimensions()):
            gen_base_lattice()
        else:
            gen_dimension_lattice()
