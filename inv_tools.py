import os
import operator
import pandas as pd

# Assumptions:
# 1) inventory like RAM, SSD, and Stands are in infinite NHSupply. The purpose
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
        # {Terminal: [Hard Drive, RAM, Stand]}
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

        self.oh_dict = {}
        self.rework_in_out = {}
        self.rework_order = {}
        self.inv_retriever = {}

    # function to add inventory
    def add_inventory(self, part, qty):
        if part in self.oh_dict.keys():
            self.oh_dict[part] += qty
        else:
            self.oh_dict[part] = qty

    # function to reduce inventory
    def remove_inventory(self, part, qty):
        self.oh_dict[part] -= qty

    # removing terminal and adding its components from inventory. Need to use
    # the terminal in the rework and add parts not needed from terminal
    # back into inventory
    def mr_clean(self, part, qty):
        # removing top level part from inventory
        self.remove_inventory(part, qty)
        # looping through components in part and adding them into inventory
        for i in self.bom[part]:
            self.add_inventory(i, qty)

    # removing a terminal's components from inventory, need to take Inventory
    # of components needed to make rework happen
    def get_gainz(self, part, qty):
        # Components in "part" is what we want to remove from inventory
        # looping through components in part and adding to inventory
        for i in self.bom[part]:
            self.remove_inventory(i, qty)

    # searches for parts you are concerned with then returns an object
    # oriented version of the on hand inventory
    def inv_loader(self, path):
        # path: where file is located
        # file_name: name of file we are looking for
        # boms: dictionary that contains the parts we are looking for
        os.chdir(path)
        oh_list = pd.read_excel('On-hand inventory.xlsx')

        for index, row in oh_list.iterrows():
            # filtering for warehouses I need with qty > 0
            if row['Warehouse'] == 'NH' or row['Warehouse'] == 'NHSupply' and \
                    row['Available physical'] > 0:
                # only concnerned with parts in TERMINAL_BOMS
                if row['Item number'] in self.bom.keys():
                    # turning inventory into something more readable
                    # ex: 980027041 into RAM.8GB
                    item = row['Item number']

                    if "M61" in item:
                        item = row['Item number']
                        oh_qty = 2  # choosing 2 for now
                    else:
                        item = self.bom[item][0]
                        oh_qty = 1000  # choosing 2 for now

                    # oh_qty = row['Available physical']
                    # oh_qty = 2  # choosing 2 for now

                    # loading inventory into dictionary
                    self.add_inventory(item, oh_qty)
                else:
                    pass
            else:
                pass

    # defining function to inform program what parts need to come in/out
    # of a terminal for a rework to happen... do not really need
    def rework_comp(self, have, need):
        have = self.bom[have]
        need = self.bom[need]

        comp_in = {}
        comp_out = {}

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
    def rework_rank(self, term_need):
        # different scores, higher means more difficulty/labor required
        stand_score = 2
        ssd_score = 5
        ram_score = 10
        hw_need = self.bom[term_need]

        # want to create an algorithm that "weighs" the different terminals
        # I can reconfigure from, lower number will be less difficult to
        # rework than higher numbers
        if len(hw_need) == 3:
            for terminal in self.bom:
                if len(self.bom[terminal]) == 3 and terminal != term_need:
                    counter = 0
                    score = 0
                    # def getscore(self, terminal)
                    for components in self.bom[terminal]:
                        # Any component not in BOM is something I will need to
                        # add in and for the rework.
                        if components != hw_need[counter]:
                            if "SSD" in components:
                                score += ssd_score
                            elif "RAM" in components:
                                score += ram_score
                        counter += 1
                    self.rework_order[score] = terminal

                # Creating seperate conditions for terminals with no stand
                # BOM has only a length of 2
                elif len(self.bom[terminal]) == 2 and terminal != term_need:
                    counter = 0
                    score = stand_score
                    for components in self.bom[terminal]:
                        # Any component not in BOM is something I will need to
                        # add in and for the rework
                        if components != hw_need[counter]:
                            if "SSD" in components:
                                score += ssd_score
                            elif "RAM" in components:
                                score += ram_score
                        counter += 1
                    self.rework_order[score] = terminal
        else:
            for terminal in self.bom:
                if len(self.bom[terminal]) == 3 and terminal != term_need:
                    counter = 0
                    score = stand_score
                    for components in self.bom[terminal]:
                        # Any component not in BOM is something I will need to
                        # add in and for the rework.
                        if counter == 2:
                            pass
                        elif components != hw_need[counter]:
                            if "SSD" in components:
                                score += ssd_score
                            elif "RAM" in components:
                                score += ram_score
                        counter += 1
                    self.rework_order[score] = terminal
        # {score: terminal}

    # Inventory God =======================================================
    # Inventory god function, finds the parts you are looking for
    # and decides if a rework is needed
    def inv_god(self, model, demandqty):
        # model is the terminal called out on demand
        # demandqty is the quantity of the terminal needed
        # checking to see if demandqty of part on hand is enough to satisfy
        # demand
        if self.oh_dict[model] >= demandqty:
            print("\n No need to rework... life is good :) \n")
            self.remove_inventory(model, demandqty)

        else:  # not looking forward to this
            print("Need to rework... how could you let this happen? \n")
            # going to use the min number of drives or ram or stands
            # to see how many terminals I can actually rework
            term_bom = self.bom[model]
            maxrework = 0
            counter = 0
            # going through components in BOM first
            for i in term_bom:
                if counter == 0:
                    maxrework = self.oh_dict[i]
                elif self.oh_dict[i] < maxrework:
                    maxrework = self.oh_dict[i]

            # now looping through terminals. Going to add total terminals
            # available for rework together to see how many terminals
            # are available. Will then take min of this and maxrework
            totalterm = 0
            for i in self.terminals:
                if i != model:
                    totalterm += self.oh_dict[i]

            maxrework = min(totalterm, maxrework)

            # getting total quantity of terminals we are short
            qtyshort = demandqty - self.oh_dict[model]

            # getting min quantity we can rework
            qtyshort = min(qtyshort, maxrework)

            # sorting rework order from least to most difficult
            self.rework_rank(model)
            order = sorted(self.rework_order.items(),
                           key=operator.itemgetter(0))
            for score, terminal in order:
                ohqty = self.oh_dict[terminal]

                if qtyshort > 0:
                    print(terminal)
                    # if ohqty larger than qtyshort then take the terminal
                    # qty we are short. Else, we are taking everything in
                    # inventory we have of that part
                    if ohqty > qtyshort:
                        print("Qty Taking: ", qtyshort)
                        qtyshort -= qtyshort
                        # adding and removing components from invetory
                        self.mr_clean(terminal, qtyshort)
                        self.get_gainz(terminal, qtyshort)
                    else:
                        print("Qty Taking: ", ohqty)
                        qtyshort -= self.oh_dict[terminal]
                        # adding and removing components from invetory
                        self.mr_clean(terminal, ohqty)
                        self.get_gainz(terminal, ohqty)
