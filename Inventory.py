import os
import socket as soc
import inv_tools as it

compname = soc.gethostname()
# print("Computer Name: " + compname)

if compname == 'DESKTOP-3U5BV0O':
    # setting up desired directories (Home Desktop)
    cpu = 'Karl'
else:
    # setting up desired directories (Work Computer)
    cpu = 'SchubertK'

fle_path = os.path.join('C:\\', 'Users', cpu,
                        'Onedrive - PAR Technology Corporation',
                        'Demand Planning', 'AX Reports')

# creating BOM structure for different M6150
# {Terminal: [Hard Drive, RAM, Stand]}
TERMINAL_BOMS = {'M6150': ['SSD.64GB', 'RAM.4GB', 'Stand'],
                 'M6150-01': ['SSD.128GB', 'RAM.4GB', 'Stand'],
                 'M6150-02': ['SSD.64GB', 'RAM.8GB', 'Stand'],
                 'M6150-03': ['SSD.128GB', 'RAM.8GB', 'Stand'],
                 'M6150-10': ['SSD.64GB', 'RAM.4GB'],
                 # need to add 4GB of ram and stand part numbers
                 '980027041': ['RAM.8GB'],
                 '980027042': ['SSD.128GB'],
                 '980027028': ['SSD.64GB']}

oh_list = 'On-hand inventory.xlsx'

f = it.inv_tools("Instance")

f.inv_loader(fle_path, TERMINAL_BOMS)
# print(f.oh_list)

f.rework_utility("M6150-10", TERMINAL_BOMS)
print(f.rework_rank)

# call function from another function?
f.inv_god(f.oh_list, "M6150", 3, TERMINAL_BOMS)
print(f.inv_retriever)
