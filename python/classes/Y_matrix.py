


class Y_matrix:

    def __init__(self, objs):
        # Initialization
        self.objs = objs
        self.buses = []
        self.conductors = {}
        self.s_base = 1000

    def build(self):
        # Create an array of ConnectivityNode groups that represent busbars
        self.buses = self.merge_conn_nodes()

        self.Y_bus = self.create_empty_matrix()
        self.add_elements()
        return self.Y_bus

    def add_elements(self):
        # Process all ACLineSegments
        self.process_AClines()

        # Process all Transformers
        self.process_transformers()

    def process_AClines(self):
        # Find all ACLineSegment ids
        line_ids = {line_id for line_id, line_obj in self.objs.items() if line_obj.__name__ == "ACLineSegment"}

        # Loop through the lines and find the ids of the ConnectivityNodes connected
        for line in line_ids:
            conn_pair = {term.ConnectivityNode for term in self.objs.values() if term.__name__ == "Terminal" and
                         term.ConductingEquipment == line and term.connected}

            # If not both terminals of the line are connected, the line is not conducting, so the line is omitted
            if len(conn_pair) < 2:
                continue

            # Loop through the buses and find the two that are connected by the line
            b = []
            for i in range(len(self.buses)):
                if conn_pair.intersection(self.buses[i]):
                    b.append(i)

            # Retrieve base voltage, impedance and susceptance of the line
            u_base = float(self.objs[self.objs[line].BaseVoltage].nominalVoltage)
            y_ser_pu = self.admittance_to_pu(1/(float(self.objs[line].r) + float(self.objs[line].x) * 1j), u_base)
            y_sh_pu = self.admittance_to_pu(float(self.objs[line].gch) + float(self.objs[line].bch) * 1j, u_base)

            # Add the impedance and susceptance of the line in the matrix according to the PI-model
            self.series_admittance(b[0], b[1], y_ser_pu)
            self.Y_bus[b[0]][b[0]] += y_sh_pu/2
            self.Y_bus[b[1]][b[1]] += y_sh_pu/2

    def process_transformers(self):
        # Find all transformers in the grid and create a dictionary with their transformer ends
        # E.g. {powertransformer1: {ptf_end1_1, ptf_end1_2}}
        ptf_ids = {}
        for ptf_id, ptf_obj in self.objs.items():
            if ptf_obj.__name__ == "PowerTransformer":
                ptf_ids[ptf_id] = {ptfe_id for ptfe_id, ptfe_obj in self.objs.items() if ptfe_obj.__name__ == "PowerTransformerEnd" and ptfe_obj.PowerTransformer == ptf_id}

        # Loop through all powertransformers and add them to the matrix
        for ptf in ptf_ids:
            windings = len(ptf_ids[ptf])        # Number of windings (connected or disconnected)
            ptf_ends = []
            connected = 0

            # Check whether the transformerends are connected or not and find out to what buses they are connected
            for ptfe in ptf_ids[ptf]:
                obj = self.objs[ptfe]
                term = self.objs[obj.Terminal]
                if term.connected:
                    bus = [i for i in range(len(self.buses)) if term.ConnectivityNode in self.buses[i]][0]
                    connected += 1
                else:
                    bus = None
                # Retrieve the properties of the transformer end
                ptf_ends.append([bus, float(obj.r), float(obj.x), float(obj.g), float(obj.b), float(self.objs[obj.BaseVoltage].nominalVoltage)])

            # Add the shunt admittance to the buses that transformerends are connected to
            # Note that this always needs to be done no matter how many windings are disconnected
            for lst in ptf_ends:

                bus, r, x, g, b, u_base = lst
                if bus is None:
                    continue
                y_sh_pu = self.admittance_to_pu(g + b*1j, u_base)
                self.Y_bus[bus][bus] += y_sh_pu

            # Situation 1: A 3 winding tf with all ends connected
            if connected == windings == 3:
                self.add_bus()
                for lst in ptf_ends:
                    bus, r, x, g, b, u_base = lst
                    self.series_admittance(bus, -1, self.admittance_to_pu(1/(r + x*1j), u_base))

            # Situation 2: A 2 winding tf with all ends connected
            if connected == windings == 2:
                z_ser = 0
                bus = []
                for lst in ptf_ends:
                    bu, r, x, g, b, u_base = lst
                    bus.append(bu)
                    if r != 0 or x != 0:
                        z_ser += (r + x*1j) / (u_base**2)
                self.series_admittance(bus[0], bus[1], self.admittance_to_pu(1 / z_ser, 1))

            # Situation 3: A 3 winding tf with only 2 connected
            if connected == 2 and windings == 3:
                self.add_bus()
                for lst in ptf_ends:
                    bus, r, x, g, b, u_base = lst
                    if bus is not None:
                        self.series_admittance(bus, -1, self.admittance_to_pu(1/(r + x*1j), u_base))
                    if bus is None:
                        self.Y_bus[-1][-1] += 1/(r + x*1j) + g + b*1j

            # Situation 4: A 2 winding tf with only 1 connected
            if connected == 1 and windings == 2:
                y_sh_pu = []
                bus = []
                for lst in ptf_ends:
                    bu, r, x, g, b, u_base = lst
                    if bu is not None and r == 0:
                        bus = bu
                    else:
                        z = r + x*1j + 1/(g + b*1j)
                        y_sh_pu = self.admittance_to_pu(1/z, u_base)
                self.Y_bus[bu][bu] += y_sh_pu

            # Situation 5: A 3 winding tf with only 1 connected
            if connected == 1 and windings == 3:
                y_sh_pu = []
                bus = []
                for lst in ptf_ends:
                    bu, r, x, g, b, u_base = lst
                    if bu is not None:
                        bus = bu
                        z_bu = r + x*1j
                    else:
                        z = r + x*1j + 1/(g + b*1j)
                        y_sh_pu.append(self.admittance_to_pu(1/z, u_base))
                    self.Y_bus[bu][bu] += 1/(1/sum(y_sh_pu) + z_bu)

            # Situation 6: No windings are connected: skip the tf
            if connected == 0:
                continue

    def merge_conn_nodes(self):
        # Find all Breakers that are closed
        break_ids = {break_id for break_id, break_obj in self.objs.items() if break_obj.__name__ == "Breaker" and
                     not break_obj.open}

        # Find all Terminals with ConnectivityNodes connected
        term_objs = {term_obj for term_obj in self.objs.values() if term_obj.__name__ == "Terminal" and
                     hasattr(term_obj, "ConnectivityNode") and term_obj.connected}

        # Find all ConnectivityNode pairs that are connected by a closed Breaker
        conn_pairs = []
        for break_id in break_ids:
            conn_pairs.append({term_obj.ConnectivityNode for term_obj in term_objs if term_obj.ConductingEquipment == break_id})
            if len(conn_pairs[-1]) < 2:
                del conn_pairs[-1]

        # Loop through all ConnectivityNode pairs, elaborate connections, Create a new list with ConnectivityNode groups
        conn_groups = []
        for pair in conn_pairs:
            remove_groups = []
            new_group = pair

            # Flag old groups to be removed later
            for group in conn_groups:
                if new_group.intersection(group):
                    remove_groups.append(group)
                    new_group = new_group.union(group)

            conn_groups.append(new_group)

            # Remove old groups
            for group in remove_groups:
                conn_groups.remove(group)

        # Find all remaining ConnectivityNode id's
        conn_groups += [{conn_id} for conn_id, conn_obj in self.objs.items() if conn_obj.__name__ == "ConnectivityNode"
                            and conn_id not in set.union(*conn_groups)]

        return conn_groups

    def admittance_to_pu(self, y, u_base):
        # Calculating per unit admittance
        y_base = self.s_base / u_base**2
        y_pu = y / y_base
        return y_pu



    def create_empty_matrix(self):
        # Create empty Y-matrix
        n = len(self.buses)
        return [[0. for x in range(n)] for y in range(n)]

    def add_bus(self):
        # Add extra bus to system by adding a zero-row and -column to the matrix
        n = len(self.Y_bus)
        for i in range(n):
            self.Y_bus[i].append(0.)
        self.Y_bus.append([0.] * (n + 1))

    def series_admittance(self, b1, b2, y):
        # Add a series admittance to the matrix
        self.Y_bus[b1][b2] -= y
        self.Y_bus[b2][b1] -= y
        self.Y_bus[b1][b1] += y
        self.Y_bus[b2][b2] += y

    def print_Y_bus(self):
        # This method prints the Y-matrix well-formated
        s = ""
        for row in self.Y_bus:
            s += "".join("{:.2}" + " "*(20 - len("{:.2}".format(e))) for e in row).format(*row) + "\n"
        return s

    def export_csv(self, file):
        # Export the calculated Y-matrix to a CSV file
        for row in self.Y_bus:
            s = "{:.4}, " * len(row)
            file.write(s.format(*row))
            file.write("\n")
