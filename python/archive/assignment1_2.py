import xml.etree.ElementTree as ET
import time
import cmath

EQ_FILE = "../data/Total_MG_T1_EQ_V2.xml"
SSH_FILE = "../data/Total_MG_T1_SSH_V2.xml"


class CIM_reader:

    def __init__(self, eq, ssh):
        self.eq_file = eq
        self.ssh_file = ssh
        self.obj_dict = {}

    def parse_xml(self):
        tree = ET.parse(self.eq_file)
        eq_root = tree.getroot()

        tree = ET.parse(self.ssh_file)
        ssh_root = tree.getroot()

        self.xml = self.merge_roots(eq_root, ssh_root)

        return eq_root, ssh_root


    def merge_roots(self, eq, ssh):

        for element in eq:
            eq_id = list(element.attrib.values())[0]

            if eq_id[0] == "#":
                eq_id = eq_id[1:]

            eq_name = element.tag.split("}")[-1]

            self.obj_dict[eq_id] = type(eq_name, (), {})

            for child in element:

                eq_prop = child.tag.split(".")[-1]
                eq_val = child.text

                if eq_val == None:
                    eq_val = list(child.attrib.values())[0]
                    if eq_val[0] == "#":
                        eq_val = eq_val[1:]

                if eq_val in {"true", "True"}:
                    eq_val = True
                if eq_val in {"false", "False"}:
                    eq_val = False

                try:
                    setattr(self.obj_dict[eq_id], eq_prop, eq_val)
                except:
                    pass
                    #print(eq_id)

        for element in ssh:
            ssh_id = list(element.attrib.values())[0]

            if ssh_id[0] == "#":
                ssh_id = ssh_id[1:]

            for child in element:

                ssh_prop = child.tag.split(".")[-1]
                ssh_val = child.text

                try:
                    setattr(self.obj_dict[ssh_id], ssh_prop, ssh_val)
                except:
                    pass
                    #print(ssh_id)

        return self.obj_dict

    def print_all_items(self, type="all", prop="all"):
        for obj_id, obj in self.obj_dict.items():
            if obj.__name__ == type or type == "all":
                print("\n" + obj.__name__ + ":\n")

                if hasattr(obj, prop):
                    print(" "*3 + obj_id, obj.__name__, getattr(obj, prop))
                if prop == "all":
                    print(" "*3 + str([(attr, getattr(obj, attr)) for attr in dir(obj) if attr[:2] + attr[-2:] != '____']))





if __name__ == "__main__":
    cr = CIM_reader(EQ_FILE, SSH_FILE)
    eq, ssh = cr.parse_xml()

    dict = cr.merge_roots(eq, ssh)
    print(len(dict))
    cr.print_all_items(type="ACLineSegment", prop="all")

