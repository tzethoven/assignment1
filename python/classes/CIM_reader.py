import xml.etree.ElementTree as ET

class CIM_reader:
    # eq = File path for EQ - XML Data
    # ssh = File path for SSH - XML Data
    def __init__(self, eq, ssh):
        self.eq_file = eq
        self.ssh_file = ssh
        self.obj_dict = {}

    # Calls the EQ and SSH file and parse it in a Python list (using the function parse_xml())
    # Then, the lists are passed to the merge_roots() method to creates a object dictionary
    def process_xml(self):
        eq_root = self.parse_xml(self.eq_file)
        ssh_root = self.parse_xml(self.ssh_file)
        self.merge_roots(eq_root, ssh_root)
        return self.obj_dict

    # Parse the XML into a list in Python (one list for EQ and other list for SSH)
    @staticmethod
    def parse_xml(path):
        tree = ET.parse(path)
        return tree.getroot()

    # The lists with the XML information are translate ONE objects list
    def merge_roots(self, eq, ssh):

        for el in eq:
            self.process_element(el)
        for el in ssh:
            self.process_element(el)

    # Create the object name and writhes the properties of each one.
    def process_element(self, el):
        el_id = list(el.attrib.values())[0]

        # Delete the hashtag of the ID
        if el_id[0] == "#":
            el_id = el_id[1:]

        # Extract the name of the object (Tag name)
        el_name = el.tag.split("}")[-1]

        # Check if the object was not created
        if el_id not in self.obj_dict.keys():
            self.obj_dict[el_id] = type(el_name, (), {})

        # Add the properties of the object (e.g. Cable resistance, Equipment container, etc)
        self.edit_obj(el, el_id)

    # Add the properties of the object (e.g. Cable resistance, Equipment container, etc)
    def edit_obj(self, el, el_id):
        for child in el:
            prop = child.tag.split(".")[-1]
            val = child.text

            if val is None:
                val = list(child.attrib.values())[0]
            if val[0] == "#":
                val = val[1:]
            if val in {"true", "True"}:
                val = True
            if val in {"false", "False"}:
                val = False

            try:
                setattr(self.obj_dict[el_id], prop, val)
            except:
                print("Error creating object:", el_id)

    # Auxiliary function (printing for debugging)
    def print_all_items(self, type="all", prop="all"):
        for obj_id, obj in self.obj_dict.items():
            if obj.__name__ == type or type == "all":
                print("\n" + obj.__name__ + ":\n")

                if hasattr(obj, prop):
                    print(" "*3 + obj_id, obj.__name__, getattr(obj, prop))
                if prop == "all":
                    s = str([(attr, getattr(obj, attr)) for attr in dir(obj) if attr[:2] + attr[-2:] != '____'])
                    print(" "*3 + s)

if __name__ == "__main__":
    eq="../../data/Total_MG_T1_EQ_V2.xml"
    ssh="../../data/Total_MG_T1_SSH_V2.xml"
    cr=CIM_reader(eq,ssh)
    obj=cr.process_xml()


