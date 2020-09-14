import inv_tools

i = inv_tools.inv_tools()
s = inv_tools.simulation(1)


# setting up period stats to make some functions work better
i.periodstats(1)


print("\nPrinting general data and info =====================================")
print("\nPrinting Terminals:")
print(i.terminals)

print("\nPrinting Components:")
print(i.components)

print("\nPrinting Values:")
print(i.values)

print("\nPrinting Boms:")
print(i.bom)

print("\nPrinting Demand Info:")
print(i.demandinfo)


print("\n\n\n\nTesting Inventory Functions ==================================")

print("Printing empty oh-dict")
print(i.oh_dict)

# inventory I want everything to be
n = 10
# part I want to add/subtract inventory
componenttest = "SSD.128GB"
part = i.terminals[0]
part2 = "M6150-01"

print("\nPopulating inventory for every part to " + str(n))

for terminal in i.terminals:
    if terminal in i.oh_dict.keys():
        pass
    else:
        i.oh_dict[terminal] = n

for component in i.components:
    if component in i.oh_dict.keys():
        pass
    else:
        i.oh_dict[component] = n

print("Printing oh-dict")
print(i.oh_dict)

print("\nTesting add_inventory function")
print("Adding", str(n), part, "to inventory", sep=' ')
i.add_inventory(part, n)
print(i.oh_dict)

print("\nTesting remove_inventory function")
print("Taking", str(n), part, "from inventory", sep=' ')
i.remove_inventory(part, n)
print(i.oh_dict)


print("\n\n\n\nTesting MRP functions ========================================")
n = 20
if len(i.terminals) == 1:
    part = i.terminals[0]

    partdict = {part2: [20, n]}

    print("\nTesting MRP on", str(n), part, sep=' ')
    i.mrp(part, n, 1)
else:
    part = i.terminals[0]
    part2 = i.terminals[1]

    partdict = {part2: [20, n]}

    print("\nTesting MRP on", str(n), part, sep=' ')
    i.mrp(part, n, 1)

    print("\nTesting MRP2 on", str(n), part2, sep=' ')
    i.mrp2(partdict, 1)


print("\n\n\n\nTesting Freight Functions ====================================")
part1 = i.terminals[0]
part2 = i.components[0]
n = 20
print("\nTesting Standard Freight on Terminal", part1, sep=" ")
i.freight(part1, n, 'Standard', Period=1)

print("\nTesting Standard Freight on Component", part2, sep=" ")
i.freight(part2, n, 'Standard', Period=1)

print("\nTesting Premium Freight on Terminal", part1, sep=" ")
i.freight(part1, n, 'Premium', Period=1)

print("\nTesting Premium Freight on Component", part2, sep=" ")
i.freight(part2, n, 'Premium', Period=1)


print("\n\n\n\nTesting Manufacturing Functions ==============================")
n = 5

# Some times I need to test scenarios where only 1 terminal exists, adjusting
# code to reflect that
if len(i.terminals) == 1:
    print("Only 1 terminal to work with")
    part1 = i.terminals[0]

    print("\nTesting maxreportaf", part1, sep=' ')
    print(i.maxreportaf(part1))

    print("\nTesting build function", n, part1, sep=' ')
    i.build(part1, n, 1)
else:
    print("Working with more than 1 terminal")
    part1 = i.terminals[0]
    part2 = i.terminals[1]

    print("\nTesting maxreportaf", part1, sep=' ')
    print(i.maxreportaf(part1))

    print("\nTesting build function", n, part1, sep=' ')
    i.build(part1, n, 1)

    # testing rework function
    print("\nTesting rework_rank for", part1, sep=' ')
    print(i.rework_rank(part1))

    print("\nTesting rework_comp, getting components that need to come in and out")
    print(i.rework_comp(part1, part2))

    print("\nTesting Get_Gainz function by reworking",
          part1, "into", part2, sep=' ')
    i.get_gainz(part1, part2, n, 1)


print("\n\nTesting Simulations functions ====================================")
# number of times to run the simulation
n = 5
# print("\nSimulation for PAR if it was run by Gorillas")
s.run0(n)

# print("\nsimulation for regular PAR")
# s.run1(n)

# print("\nsimulation for postponement/riskpooling PAR")
# s.run2(n)
