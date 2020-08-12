import inv_tools

i = inv_tools.inv_tools()


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


print("\n\n\n\nTesting Inventory Functions ==================================")

print("Printing empty oh-dict")
print(i.oh_dict)

# inventory I want everything to be
n = 10
# part I want to add/subtract inventory
componenttest = "SSD.128GB"
part = "M6150"
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

print("Testing add_inventory function\n")
print("\nAdding", str(n), part, "to inventory", sep=' ')
i.add_inventory(part, n)
print(i.oh_dict)

print("Testing remove_inventory function\n")
print("\nTaking", str(n), part, "from inventory", sep=' ')
i.remove_inventory(part, n)
print(i.oh_dict)


print("\n\nTesting MRP functions ============================================")
part = "M6150"
part2 = "M6150-01"
n = 20

partdict = {part2: [20, n]}

print("\nTesting MRP on", str(n), part, sep=' ')
i.mrp(part, n, 1)

print("\nTesting MRP2 on", str(n), part2, sep=' ')
i.mrp2(partdict, 1)


print("\n\n\n\nTesting Freight Functions ====================================")
termfreight = "M6150"
compfreight = "SSD.128GB"
print("\nTesting Standard Freight on Terminal", termfreight, sep=" ")
i.freight(termfreight, n, 'Standard', Period=1)

print("\nTesting Standard Freight on Component", compfreight, sep=" ")
i.freight(compfreight, n, 'Standard', Period=1)

print("\nTesting Premium Freight on Terminal", termfreight, sep=" ")
i.freight(termfreight, n, 'Premium', Period=1)

print("\nTesting Premium Freight on Component", compfreight, sep=" ")
i.freight(compfreight, n, 'Premium', Period=1)


print("\n\n\n\nTesting Manufacturing Functions ==============================")
part1 = "M6150"
part2 = "M6150-03"
n = 5

# testing rework function
print("\nTesting rework_rank for", part1, sep=' ')
print(i.rework_rank(part1))


print("\nTesting rework_comp, getting components that need to come in and out")
print(i.rework_comp(part, part2))

print("\nTesting Get_Gainz function by reworking",
      part1, "into", part2, sep=' ')
i.get_gainz(part1, part2, n, 1)

print("\nTesting maxreportaf", part1, sep=' ')
print(i.maxreportaf(part1))

print("\nTesting build function", n, part1, sep=' ')
i.build(part1, n, 1)


print("\n\nTesting Simulations functions ====================================")
# number of times to run the simulation
n = 5
gorilla = i.run0(n)

# simulation for regular PAR
semioptimal = i.run1(n)

# simulation for postponement/riskpooling PAR
optimal = i.run2(n)
