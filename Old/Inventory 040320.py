# creating BOM structure for different M6150
# {Terminal: [Hard Drive, RAM]}
TERMINAL_BOMS = {'M6150': ['64GBHD', '4GBRAM'],
                 'M6150-01': ['128GBHD', '4GBRAM'],
                 'M6150-02': ['64GBHD', '8GBRAM'],
                 'M6150-03': ['128GBHD', '8GBRAM']}

# for each terminal, the order of how we should rework from
# least to most complicated
REWORK_ORDER = {'M6150': ['M6150-01', 'M6150-02', 'M6150-03'],
                'M6150-01': ['M6150', 'M6150-02', 'M6150-03'],
                'M6150-02': ['M6150-03', 'M6150', 'M6150-01'],
                'M6150-03': ['M6150-02', 'M6150', 'M6150-01']}

# need to create something to assist with reworking
# returns what parts need to come out


def rework_comp(term_have, term_need):
    comp_in = {}
    comp_out = {}
    counter = 1
    # find components needed to put into terminal
    for component in need:
        if component not in have:
            if counter == 1:
                comp_in['HD'] = component
            if counter == 2:
                comp_in['RAM'] = component
        counter += 1

    counter = 1
    # find components needed to take out of terminal
    for component in have:
        if component not in need:
            if counter == 1:
                comp_out['HD'] = component
            if counter == 2:
                comp_out['RAM'] = component
        counter += 1

    rework = {'In': comp_in, 'Out': comp_out}
    return(rework)


have = TERMINAL_BOMS['M6150']
need = TERMINAL_BOMS['M6150-01']

print(rework_comp(have, need))


# Inventory
# {Terminal: QTY OH}
ONHAND_INVENTORY = {'M6150': 10, 'M6150-01': 50,
                    'M6150-02': 100, 'M6150-03': 100,
                    '64GBHD': 1000, '128GBHD': 1000,
                    '4GBRAM': 1000, '8GBRAM': 1000}

# Creating information for terminals
# {Terminal: [MIN Demand, MAX Demand, MIN FC, MAX FC, Lead Time]}
TERMINAL_DEMAND = {'M6150': [20, 100, 30, 200, 10],
                   'M6150-01': [10, 20, 30, 200, 10],
                   'M6150-02': [10, 20, 30, 200, 10],
                   'M6150-03': [5, 10, 30, 200, 10]}


[
    {'name': 'config1',
        'onHand': 1000,
        'composition': ['comp', ['hd', 'ram']]
]
for c in builder:
    c['onHand']

# Counters
# spot to count when reworks happen and stuff


# running model
# all numbers in weeks
i = 0
while i < 10:
    item = "M6150"

    # adding weekly forecast to inventory
    # using min for now
    forecast = TERMINAL_DEMAND[item][2]
    beg_inventory = ONHAND_INVENTORY[item]
    ONHAND_INVENTORY[item] = beg_inventory + forecast

    # getting min demand value for now
    demand = TERMINAL_DEMAND[item][1]

    if ONHAND_INVENTORY[item] < demand:
        print('rework')
        reworkqty = demand - ONHAND_INVENTORY[item]


        for j in REWORK_ORDER[item]:
            print(ONHAND_INVENTORY[j])

    else:
        end_inventory = ONHAND_INVENTORY[item] - demand
        ONHAND_INVENTORY[item] = end_inventory

    print(f"""Beginning Inventory: {beg_inventory}
              Forecast: {forecast}
              Demand: {demand}
              Ending Inventory: {end_inventory} \n""")

    i += 1
