import os
import socket as soc
import inv_tools as it

compname = soc.gethostname()
# print("Computer Name: " + compname)

if compname == 'DESKTOP-3U5BV0O':
    # setting up desired directories (Home Desktop) =========================
    source = os.path.join('C:\\', 'Users', 'Karl',
                          'Onedrive - PAR Technology Corporation',
                          'Demand Planning', 'AX Reports')
else:
    # setting up desired directories (Work Computer)
    source = os.path.join('C:\\', 'Users', 'SchubertK',
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

# it.rework_utility("M6150", TERMINAL_BOMS)

inventory = it.inv_loader(source, oh_list, TERMINAL_BOMS)


golden_retriever = it.inv_god(inventory, "M6150", 1)
# print(golden_retriever)
