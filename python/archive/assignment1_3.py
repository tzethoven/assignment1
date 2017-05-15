from CIM_reader import CIM_reader
from SQL_db import SQL_db
from Y_builder import Y_builder


EQ_FILE = "../data/Total_MG_T1_EQ_V2.xml"
SSH_FILE = "../data/Total_MG_T1_SSH_V2.xml"

# if __name__ is "__main__":

cr = CIM_reader(EQ_FILE, SSH_FILE)
dict = cr.process_xml()
# cr.print_all_items(type="EnergyConsumer", prop="name")


# ps_db = SQL_db(dict)
# ps_db.generate_db()




# y_builder = Y_builder(dict)
# print(y_builder.find_admittance("_f33cc626-2c46-46b6-8536-88f30ab532cb", "_b67c8340-cb6e-11e1-bcee-406c8f32ef58"))

