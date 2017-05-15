from PyCIM import cimread
import xml.etree.ElementTree as ET
import time


EQ_FILE = "../data/Total_MG_T1_EQ_V2.xml"
SSH_FILE = "../data/Total_MG_T1_SSH_V2.xml"

class CIM_reader:



    def __init__(self, eq, ssh):
        self.eq_file = eq
        self.ssh_file = ssh

    def read_cim(self):
        self.eq = cimread(self.eq_file)

        tree = ET.parse(self.ssh_file)
        self.ssh_root = tree.getroot()



        return self.eq, self.ssh_root

    '''
    def merge_dictionaries(self, dict1, dict2):
        for id2, obj2 in dict2:
    
            for id1, obj1 in dict1:
                if id1==id2:
                    dict1[id1]
    '''


    def merge_dicts(self, eq, ssh):

        for element in ssh:
            ssh_id = str(element.attrib.values()).split("'", 2)[1]

            if ssh_id[0] == "#":
                ssh_id = ssh_id[1:]

                for child in element:
                    prop = str(child.tag).split('.')[-1]

                    val = child.text
                    if val in {"true", "True"}:
                        val=True
                    if val in {"false", "False"}:
                        val=False

                    try:
                        setattr(eq[ssh_id], prop, val)
                    except:
                        print(ssh_id)



        return eq





    @staticmethod
    def mergeObjectProperties(self, objectToMergeFrom, objectToMergeTo):
        """
        Used to copy properties from one object to another if there isn't a naming conflict;
        """
        for property in objectToMergeFrom.__dict__:
            # Check to make sure it can't be called... ie a method.
            # Also make sure the objectobject ToMergeTo doesn't have a property of the same name.
            if not callable(objectToMergeFrom.__dict__[property]) and not hasattr(objectToMergeTo, property):
                setattr(objectToMergeTo, property, getattr(objectToMergeFrom, property))

        return objectToMergeTo



    def print_all_items(self):
        for obj_id, obj in self.eq:
            print(obj_id, vars(obj))




    def get_eq(self):
        return self.eq

    def get_ssh(self):
        return self.ssh




    def get_obj(self, obj_name):

        result_set = {}

        for id, obj in self.eq.items():
            if obj.__class__.__name__ == obj_name:
                result_set.update({id: obj})

        return result_set



if __name__ == "__main__":
    cr = CIM_reader(EQ_FILE, SSH_FILE)
    eq, ssh = cr.read_cim()
    time.sleep(0.5)


    dict = cr.merge_dicts(eq, ssh)

    print(dict["_ddc148fc-3abd-459d-aec1-396283e0def6"].open)

    for key, value in dict.items():
        print(key, value)

    '''
    breakers_eq = cr.get_obj("Breaker")


    br_eq = breakers_eq["_38dfcc80-600f-44e2-8f71-fb595b4f00ac"]

    br_ssh = ssh["#_38dfcc80-600f-44e2-8f71-fb595b4f00ac"]

    br = cr.mergeObjectProperties(br_eq, br_ssh)

    print(br_ssh.__class__.__name__)



    for id, term in terminals.items():

        print(id + ": " + term.name)
   





for id, obj in eq.items():
    print("ID: {}        Component name: {}".format(id, obj.name))


for id, obj in ssh.items():
    print("ID: {}        Component name: {}".format(id, obj.name))

'''