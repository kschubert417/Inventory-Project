import os
import pandas as pd


# Inventory loader ============================================================
# searches for parts you are concerned with then returns an object
# oriented version of the on hand inventory
def inv_loader(path, file_name, items):
    # path: where file is located
    # file_name: name of file we are looking for
    # items: dictionary that contains the parts we are looking for
    os.chdir(path)
    oh_list = pd.read_excel('On-hand inventory.xlsx')

    inventory = []

    for index, row in oh_list.iterrows():
        # filtering for warehouses I need with qty > 0
        if row['Warehouse'] == 'NH' or row['Warehouse'] == 'NHSupply' and \
                row['Available physical'] > 0:
            # only concnerned with parts in TERMINAL_BOMS
            if row['Item number'] in items.keys():
                item = row['Item number']
                # oh_qty = row['Available physical']
                oh_qty = 5  # choosing 5 for now

                # object oriented approach, one list for each part that exists
                # in inventory. Will create one index for each item in
                # inventory
                num = 0
                while num < oh_qty:
                    inventory.append(items[item])
                    num += 1

            else:
                pass
        else:
            pass

    return(inventory)


# Rework utility =====================================================
# Will find parts needed to put into and take out of terminal if needed
def rework_utility(term_need, term_boms):
    hw_needed = term_boms[term_need][1]


# Inventory God =======================================================
# Inventory god function, finds the parts you are looking for
# returns the parts/quantities you are looking for as well
# as the inventory that is left over
def inv_god(oh_list, model, qty=1):
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

    # rework status of 1 if rework is required, 0 if not
    if oh_dict[model] < qty:
        rework_status = 1
    else:
        rework_status = 0

    # extracting parts from inventory we need for sales orders
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

            # elif:
                # rework, etc, etc

    # removing parts from on hand list
    for i in locations:
        oh_list.pop(i)

    return({"Retrieved": found, "Inventory": oh_list})
