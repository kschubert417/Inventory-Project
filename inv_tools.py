import os
import operator
import pandas as pd


# Creating a "class" object
class inv_tools:
    def __init__(self, name):
        self.name = name
        self.bom = {}  # need to throw bom in here?
        self.oh_list = []
        self.rework_rank = {}
        self.inv_retriever = {}

    # searches for parts you are concerned with then returns an object
    # oriented version of the on hand inventory
    def inv_loader(self, path, boms):
        # path: where file is located
        # file_name: name of file we are looking for
        # boms: dictionary that contains the parts we are looking for
        os.chdir(path)
        oh_list = pd.read_excel('On-hand inventory.xlsx')

        inventory = []

        for index, row in oh_list.iterrows():
            # filtering for warehouses I need with qty > 0
            if row['Warehouse'] == 'NH' or row['Warehouse'] == 'NHSupply' and \
                    row['Available physical'] > 0:
                # only concnerned with parts in TERMINAL_BOMS
                if row['Item number'] in boms.keys():
                    item = row['Item number']
                    # oh_qty = row['Available physical']
                    oh_qty = 2  # choosing 5 for now

                    # object oriented approach, one list for each part that
                    # exists in inventory. Will create one index for each item
                    # in inventory
                    num = 0
                    while num < oh_qty:
                        inventory.append([item, boms[item]])
                        num += 1
                else:
                    pass
            else:
                pass

        self.oh_list = inventory

    # Rework utility =====================================================
    # Will find parts needed to put into and take out of terminal if needed
    def rework_utility(self, term_need, term_boms):
        # different scores, higher means more difficulty/labor required
        stand_score = 2
        ssd_score = 5
        ram_score = 10
        rework_scores = {}
        hw_need = term_boms[term_need]

        # want to create an algorithm that "weighs" the different terminals
        # I can reconfigure from, lower number will be less difficult to
        # rework than higher numbers
        if len(hw_need) == 3:
            for terminal in term_boms:
                if len(term_boms[terminal]) == 3 and terminal != term_need:
                    counter = 0
                    score = 0
                    for components in term_boms[terminal]:
                        # Any component not in BOM is something I will need to
                        # add in and for the rework.
                        if components != hw_need[counter]:
                            if "SSD" in components:
                                score += ssd_score
                            elif "RAM" in components:
                                score += ram_score
                        counter += 1
                    rework_scores[score] = terminal

                # Creating seperate conditions for terminals with no stand
                # BOM has only a length of 2
                elif len(term_boms[terminal]) == 2 and terminal != term_need:
                    counter = 0
                    score = stand_score
                    for components in term_boms[terminal]:
                        # Any component not in BOM is something I will need to
                        # add in and for the rework
                        if components != hw_need[counter]:
                            if "SSD" in components:
                                score += ssd_score
                            elif "RAM" in components:
                                score += ram_score
                        counter += 1
                    rework_scores[score] = terminal
        else:
            for terminal in term_boms:
                if len(term_boms[terminal]) == 3 and terminal != term_need:
                    counter = 0
                    score = stand_score
                    for components in term_boms[terminal]:
                        # Any component not in BOM is something I will need to
                        # add in and for the rework.
                        if counter == 2:
                            pass
                        elif components != hw_need[counter]:
                            print(counter)
                            if "SSD" in components:
                                score += ssd_score
                            elif "RAM" in components:
                                score += ram_score
                        counter += 1
                    rework_scores[score] = terminal

        self.rework_rank = rework_scores

    # Inventory God =======================================================
    # Inventory god function, finds the parts you are looking for
    # returns the parts/quantities you are looking for as well
    # as the inventory that is left over
    # according to Tyler this is very limited
    def inv_god(self, oh_list, model, qty, term_boms):
        # oh_list is the object oriented inventory we have on hand
        # model is the model number we are looking for
        # qty is the quantity of the terminal we need
        inv_counter = 0
        found = []
        locations = []

        # Summarizing the inventory we have on hand, will use this to determine
        # whether a rework is needed or not
        oh_dict = {}
        for i in oh_list:
            if i[0] in oh_dict.keys():
                oh_dict[i[0]] += 1
            else:
                oh_dict[i[0]] = 1

        # checking to see if qty of part on hand is enough to satisfy demand
        if oh_dict[model] >= qty:
            print("No need to rework \n")

            # extracting parts from inventory we need for sales orders
            # i in this case is a counter
            while inv_counter < qty:
                for i, item in enumerate(oh_list):
                    if item[0] == model and inv_counter < qty:
                        # adding item to stuff we are taking
                        found.append(item)
                        # finding indexes where we are taking inventory from
                        locations.append(i)
                        inv_counter += 1
                        # updating oh_dict with terminal we took
                        oh_dict[item[0]] -= 1
        else:
            # this will get hairy
            print("Need to rework \n")
            # getting rework priority... need to get BOMS in here, add as
            # argument to this function?
            # using default order dictionary comes in
            rework_order = self.rework_rank
            # sorting rework order from least to most difficult
            rework_order = sorted(rework_order.items(),
                                  key=operator.itemgetter(0))
            print(rework_order)
            for score, terminal in rework_order:
                print(terminal, " | ", "Score: ", score)

        # print(oh_dict)
        # removing parts from on hand list
        for i in locations:
            oh_list.pop(i)

        # return({"Retrieved": found, "Inventory": oh_list})
        self.inv_retriever = {"Retrieved": found, "Inventory": oh_list}
