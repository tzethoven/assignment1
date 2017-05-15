from CIM_reader import CIM_reader
from SQL_db import SQL_db
from Y_matrix import Y_matrix


EQ_FILE = "../data/Total_MG_T1_EQ_V2.xml"
SSH_FILE = "../data/Total_MG_T1_SSH_V2.xml"

# EQ_FILE = "../data/MicroGridTestConfiguration_T1_BE_EQ_V2.xml"
# SSH_FILE = "../data/MicroGridTestConfiguration_T1_BE_SSH_V2.xml"


# if __name__ is "__main__":

cr = CIM_reader(EQ_FILE, SSH_FILE)
ps_objs = cr.process_xml()


# ps_db = SQL_db(ps_objs)
# ps_db.generate_db()



y = Y_matrix(ps_objs)
y.build()

