import json
import operator

# Assumptions:
# 1) inventory like RAM, SSD, and Stands are in infinite supply. The purpose
# of this model is to simulate how the supply chain can operate under the
# different scenarios where the ES600 is a buy, make, and hybrid model


# Creating a "class" object
class inv_tools:
    def __init__(self, name):
        self.name = name

        # All terminals
        self.terminals = ['M6150', 'M6150-01', 'M6150-02', 'M6150-03',
                          'M6150-10']

        # components that go into terminals
        self.components = ['RAM.4GB', 'RAM.8GB', 'SSD.64GB', 'SSD.128GB',
                           'Stand']

        # {Itemnumber: [Hard Drive, RAM, Stand]}
        self.bom = {'M6150': ['SSD.64GB', 'RAM.4GB', 'Stand'],
                    'M6150-01': ['SSD.128GB', 'RAM.4GB', 'Stand'],
                    'M6150-02': ['SSD.64GB', 'RAM.8GB', 'Stand'],
                    'M6150-03': ['SSD.128GB', 'RAM.8GB', 'Stand'],
                    'M6150-10': ['SSD.64GB', 'RAM.4GB'],
                    '980027040': ['RAM.4GB'],
                    '980027041': ['RAM.8GB'],
                    '980027028': ['SSD.64GB'],
                    '980027042': ['SSD.128GB'],
                    '980027063': ['Stand']}

        # adding initial inventory
        self.oh_dict = {'M6150': 0, 'M6150-01': 0, 'M6150-02': 0,
                        'M6150-03': 0, 'M6150-10': 0,
                        'SSD.64GB': 0, 'SSD.128GB': 0,
                        'RAM.4GB': 0, 'RAM.8GB': 0,
                        'Stand': 0}

        # create dictionary for cost types
        self.costs = {"Freight": {"Standard": {"Cost": 0.0, "Qty": 0.0},
                                  "Premium": {"Cost": 0.0, "Qty": 0.0}},
                      "Manufacturing": {"ReworkLabor": 0.0,
                                        "UnitsReworked": 0.0}}
        self.rework_in_out = {}
        self.rework_order = {}
        self.rework_labor = {}

    # Need to figure freight out... and net/average inventory
    def freight(self, Itemnumber, Qty, Freighttype):
        # adding part we are bringing in into inventory
        # self.add_inventory(Itemnumber, Qty)
        # if item number is terminal, need to apply freight cost for terminal
        if Itemnumber in self.terminals:
            # freight cost per terminal for different methods
            premiumfreight = 45
            standardfreight = 10
            if Freighttype == "Premium":
                print("\tPaying dat premium freight")
                self.costs["Freight"]["Premium"]["Cost"]\
                    += premiumfreight * Qty
                self.costs["Freight"]["Premium"]["Qty"] += Qty
            else:
                print("\tPaying dat standard freight")
                self.costs["Freight"]["Standard"]["Cost"]\
                    += standardfreight * Qty
                self.costs["Freight"]["Standard"]["Qty"] += Qty
        else:
            # freight cost per component for different methods
            standardfreight = 5
            premiumfreight = 25
            if Freighttype == "Premium":
                print("\tPaying dat premium freight")
                self.costs["Freight"]["Premium"]["Cost"]\
                    += premiumfreight * Qty
                self.costs["Freight"]["Premium"]["Qty"] += Qty
            else:
                print("\tPaying dat standard freight")
                self.costs["Freight"]["Standard"]["Cost"]\
                    += standardfreight * Qty
                self.costs["Freight"]["Standard"]["Qty"] += Qty

    def getinv(self, model):
        if model in self.inventory.keys():
            return self.inventory[model]
        else:
            print("Model not found in inventory")

    # function to add inventory
    def add_inventory(self, part, qty):
        if part in self.oh_dict.keys():
            self.oh_dict[part] += qty
        else:
            self.oh_dict[part] = qty

    # function to reduce inventory
    def remove_inventory(self, part, qty):
        # checking to see if we can't remove inventory
        if self.oh_dict[part] > 0:
            self.oh_dict[part] -= qty

    # function to take forecasted quantity, subtract current inventory from
    # it and add the difference to inventory
    # ex: if inventory > forecast, do not need to order more inventory
    def mrp(self, model, forecast):
        inventory = self.oh_dict[model]
        if forecast > inventory:
            qty = forecast - inventory
            self.add_inventory(model, qty)
            print("\tAdding ", str(qty), " to inventory")
            self.freight(model, qty, 'Standard')
        else:
            print("\tInventory enough to cover forecast\n\n")

    # creating function that adds all necessary parts into/out of inventory
    # from rework info
    def get_gainz(self, have, need, qty=1):  # rework
        """
        Parameters
        ----------
        have : type
            The part we have available for rework
        need : type
            The item we need to turn the part we "have" into
        qty : type
            Qty of the part we are reworking

        Returns
        -------
        type
            Description of returned object.
        """
        self.rework_comp(have, need)
        rework = self.rework_in_out
        # removing from inventory needed to perform rework
        for i in rework["In"]:
            component = rework["In"][i]
            onhand = self.oh_dict[component]
            if qty > onhand:
                orderqty = qty - onhand
                self.freight(component, orderqty, "Premium")
                self.add_inventory(component, orderqty)
            print("\t\ttaking from inventory: ", component)
            self.remove_inventory(component, qty)
        # adding parts we need to take out of terminal into Inventory
        for i in rework["Out"]:
            component = rework["Out"][i]
            print("\t\tadding into inventory: ", component)
            self.add_inventory(component, qty)
        # removing terminal we used for the rework from inventory
        self.remove_inventory(have, qty)

    # defining function to inform program what parts need to come in/out
    # of a terminal for a rework to happen... do not really need
    def rework_comp(self, have, need):  # rework
        have = self.bom[have]
        need = self.bom[need]

        comp_in = {}
        comp_out = {}

        # checking length of the BOM for terminal to see if stand is needed
        if len(have) > len(need):
            comp_out["Stand"] = "Stand"
        elif len(have) < len(need):
            comp_in["Stand"] = "Stand"
        else:
            pass

        # find components needed to take out of terminal
        counter = 1
        for component in need:
            if component not in have:
                if counter == 1:
                    comp_in['HD'] = component
                elif counter == 2:
                    comp_in['RAM'] = component
            counter += 1

        # find components needed to take out of terminal
        counter = 1
        for component in have:
            if component not in need:
                if counter == 1:
                    comp_out['HD'] = component
                if counter == 2:
                    comp_out['RAM'] = component
            counter += 1

        self.rework_in_out = {"In": comp_in, "Out": comp_out}
        # {In: {HD: SSD#, RAM: RAM#, Stand: Stand},
        # Out: {HD: SSD#, RAM: RAM#, Stand: Stand}}

    # Rework utility =====================================================
    # Will find parts needed to put into and take out of terminal if needed
    # returns the score needed to rework each terminal we have into the
    # terminal we need
    def rework_rank(self, term_need):  # rework
        # different scores, higher means more difficulty/labor required
        stand_score, ssd_score, ram_score = 2, 5, 10

        # going to add cost of labor in as well
        stand_labor, ssd_labor, ram_labor = 10, 5, 20

        hw_need = self.bom[term_need]

        # want to create an algorithm that "weighs" the different terminals
        # I can reconfigure from, lower number will be less difficult to
        # rework than higher numbers
        if len(hw_need) == 3:
            for terminal in self.bom:
                if len(self.bom[terminal]) == 3 and terminal != term_need:
                    counter = 0
                    score = 0
                    labor = 0
                    # def getscore(self, terminal)
                    for components in self.bom[terminal]:
                        # Any component not in BOM is something I will need to
                        # add in and for the rework.
                        if components != hw_need[counter]:
                            if "SSD" in components:
                                score += ssd_score
                                labor += ssd_labor
                            elif "RAM" in components:
                                score += ram_score
                                labor += ram_labor
                        counter += 1
                    self.rework_order[score] = terminal
                    self.rework_labor[terminal] = labor

                # Creating seperate conditions for terminals with no stand
                # BOM has only a length of 2
                elif len(self.bom[terminal]) == 2 and terminal != term_need:
                    counter = 0
                    score = stand_score
                    labor = stand_labor
                    for components in self.bom[terminal]:
                        # Any component not in BOM is something I will need to
                        # add in and for the rework
                        if components != hw_need[counter]:
                            if "SSD" in components:
                                score += ssd_score
                                labor += ssd_labor
                            elif "RAM" in components:
                                score += ram_score
                                labor += ram_labor
                        counter += 1
                    self.rework_order[score] = terminal
                    self.rework_labor[terminal] = labor
        else:
            for terminal in self.bom:
                if len(self.bom[terminal]) == 3 and terminal != term_need:
                    counter = 0
                    score = stand_score
                    labor = stand_labor
                    for components in self.bom[terminal]:
                        # Any component not in BOM is something I will need to
                        # add in and for the rework.
                        if counter == 2:
                            pass
                        elif components != hw_need[counter]:
                            if "SSD" in components:
                                score += ssd_score
                                labor += ssd_labor
                            elif "RAM" in components:
                                score += ram_score
                                labor += ram_labor
                        counter += 1
                    self.rework_order[score] = terminal
                    self.rework_labor[terminal] = labor
        # self.rework_order = {score: terminal}
        # self.rework_labor = {terminal: labor}

    # Inventory God =======================================================
    # Inventory god function, finds the parts you are looking for
    # and decides if a rework is needed
    def inv_god(self, model, demandqty):
        print("\tDemand for", str(demandqty), model, '\n')
        # model is the terminal called out on demand
        # demandqty is the quantity of the terminal needed
        # checking to see if demandqty of part on hand is enough to satisfy
        # demand
        if self.oh_dict[model] >= demandqty:
            self.remove_inventory(model, demandqty)

        else:
            # when demand is higher than inventory, add function in to
            # keep track of terminals I need to expedite in
            print("\tNeed to rework... how could you let this happen?")

            # getting total quantity of terminals we are short
            qtyshort = demandqty - self.oh_dict[model]
            qty = qtyshort
            # expediting freight here
            self.freight(model, qtyshort, "Premium")

            # removing what is left of this part from inventory
            self.remove_inventory(model, self.oh_dict[model])

            # sorting rework order from least to most difficult
            self.rework_rank(model)
            order = sorted(self.rework_order.items(),
                           key=operator.itemgetter(0))

            print("\tQty left:", str(qtyshort), "\n")
            for score, terminal in order:
                ohqty = self.oh_dict[terminal]
                if ohqty > 0:
                    if qtyshort > 0:
                        print("\t\tReworking:", terminal, "into", model)
                        # if ohqty larger than qtyshort then take the terminal
                        # qty we are short. Else, we are taking everything in
                        # inventory we have of that part
                        if ohqty > qtyshort:
                            print("\t\tQty Taking: ", qtyshort)
                            # adding and removing components from invetory
                            self.get_gainz(terminal, model, qtyshort)

                            # adding associated rework costs to dictionary
                            self.costs["Manufacturing"]["UnitsReworked"]\
                                += qtyshort
                            self.costs["Manufacturing"]["ReworkLabor"]\
                                += qtyshort * self.rework_labor[terminal]

                            # decrementing total quantity short
                            qtyshort -= qtyshort
                            print("\t\tDemand Qty left:", str(qtyshort), "\n")
                        else:
                            print("\t\tQty Taking: ", ohqty)
                            # adding and removing components from invetory
                            self.get_gainz(terminal, model, ohqty)

                            # adding associated rework costs to dictionary
                            self.costs["Manufacturing"]["UnitsReworked"]\
                                += ohqty
                            self.costs["Manufacturing"]["ReworkLabor"]\
                                += ohqty * self.rework_labor[terminal]

                            # decrementing total quantity short
                            qtyshort -= ohqty
                            print("\t\tDemand Qty left:", str(qtyshort), "\n")
                else:
                    pass
            # adding inventory ERP system would have said to expedite here
            self.add_inventory(model, qty)


class simulation:
    def __init__(self, np):
        # fp = file path
        # Demand information
        # {Terminal: [Forecast, Demand]}
        self.demand = {'M6150': [300, 10],
                       'M6150-01': [100, 10],
                       'M6150-02': [100, 10],
                       'M6150-03': [10, 300],
                       'M6150-10': [100, 10]}

        # self.f = inv_tools()

        self.np = np

    def run(self, np):
        # np = number of periods I want to run simulation
        p = 1

        # need to tell simulation I will need to call inv_tools
        f = inv_tools("Something")

        while p <= np:
            print("\nPeriod:", str(p), "=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=\n\n\n")

            # running MRP function to see what needs to be added to inventory
            # first
            print("Running MRP =========================================== \n")
            for item in self.demand:
                print(f.oh_dict)
                forecast = self.demand[item][0]

                print("\n", item, "\n\tForecast:", str(forecast),
                      "\n\tInventory:", str(f.oh_dict[item]), "\n")
                f.mrp(item, forecast)

            print("\n\n\n\nModeling Demand =============================== \n")
            for item in self.demand:
                print(f.oh_dict)
                forecast = self.demand[item][0]
                demand = self.demand[item][1]
                inventory = f.oh_dict[item]

                print(item, "\n\tForecast:", str(forecast),
                      "\n\tInventory:", str(inventory))

                # now time for the real demand for the part
                f.inv_god(item, demand)

            p += 1

        print(f.oh_dict)
        print(json.dumps(f.costs))
