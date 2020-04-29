import os
import operator
import pandas as pd


# Creating a "class" object
class inv_tools:
    def __init__(self, name):
        self.name = name
        # {Terminal: [Hard Drive, RAM, Stand]}
        self.bom = {'M6150': ['SSD.64GB', 'RAM.4GB', 'Stand'],
                    'M6150-01': ['SSD.128GB', 'RAM.4GB', 'Stand'],
                    'M6150-02': ['SSD.64GB', 'RAM.8GB', 'Stand'],
                    'M6150-03': ['SSD.128GB', 'RAM.8GB', 'Stand'],
                    'M6150-10': ['SSD.64GB', 'RAM.4GB'],
                    # need to add 4GB of ram and stand part numbers
                    '980027041': ['RAM.8GB'],
                    '980027042': ['SSD.128GB'],
                    '980027028': ['SSD.64GB']}

        self.oh_dict = {}
        self.rework_rank = {}
        self.inv_retriever = {}

    def add_inventory(self, part, qty):
        if part in self.oh_dict.keys():
            self.oh_dict[part] += qty
        else:
            self.oh_dict[part] = qty

    def remove_inventory(self, part, qty):
        self.oh_dict[part] -= qty

    # searches for parts you are concerned with then returns an object
    # oriented version of the on hand inventory
    def inv_loader(self, path):
        # path: where file is located
        # file_name: name of file we are looking for
        # boms: dictionary that contains the parts we are looking for
        os.chdir(path)
        oh_list = pd.read_excel('On-hand inventory.xlsx')

        # inventory = {}

        for index, row in oh_list.iterrows():
            # filtering for warehouses I need with qty > 0
            if row['Warehouse'] == 'NH' or row['Warehouse'] == 'NHSupply' and \
                    row['Available physical'] > 0:
                # only concnerned with parts in TERMINAL_BOMS
                if row['Item number'] in self.bom.keys():
                    item = row['Item number']
                    # oh_qty = row['Available physical']
                    oh_qty = 2  # choosing 2 for now

                    # loading inventory into dictionary
                    self.add_inventory(item, oh_qty)
                else:
                    pass
            else:
                pass

        # self.oh_list = inventory

    # Rework utility =====================================================
    # Will find parts needed to put into and take out of terminal if needed
    def rework_utility(self, term_need):
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
                    self.rework_rank[score] = terminal

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
                    self.rework_rank[score] = terminal
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
                    self.rework_rank[score] = terminal
        # {rank: {Terminal: "M6150", SSD:}}

    # Inventory God =======================================================
    # Inventory god function, finds the parts you are looking for
    # and decides if a rework is needed
    def inv_god(self, model, qty):
        # checking to see if qty of part on hand is enough to satisfy demand
        if self.oh_dict[model] >= qty:
            print("\n No need to rework \n")
            self.remove_inventory(model, qty)
        else:
            # this will get hairy
            print("Need to rework \n")
            # getting rework priority
            # sorting rework order from least to most difficult
            rework_order = sorted(self.rework_rank.items(),
                                  key=operator.itemgetter(0))
            for score, terminal in rework_order:
                print(terminal, " | ", "Score: ", score)
