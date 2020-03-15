
import json


class PhDimension(object):
    """
    2. construction of data dimension
    """
    def __init__(self, dimension_path):
        with open(dimension_path, "r") as f:
            dm = json.loads(f.read())
        self.dms = dm["dimensions"]
        self.all_hierarchies = []
        self.all_hierarchies = self.get_all_hierarchies()

    def get_dimensions(self):
        return self.dms

    def gen_all_hierarchies(self):
        tmp = []
        for dm in self.dms.get_dimensions():
            for her in dm["hierarchy"]:
                tmp.append(her)

        self.all_hierarchies = tmp
        return tmp

    def get_all_hierarchies(self):
        return self.all_hierarchies

