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


oh_list = 'On-hand inventory.xlsx'

f = it.inv_tools("Instance")

f.inv_loader(fle_path)
print(f.oh_list)

f.rework_utility("M6150")
print(f.rework_rank)

# call function from another function?
f.inv_god("M6150", 2)
print(f.inv_retriever)
