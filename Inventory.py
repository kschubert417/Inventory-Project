import os
import json
import socket as soc
import inv_tools as it

compname = soc.gethostname()

if compname == 'DESKTOP-3U5BV0O':
    # setting up desired directories (Home Desktop)
    cpu = 'Karl'
else:
    # setting up desired directories (Work Computer)
    cpu = 'SchubertK'

fle_path = os.path.join('C:\\', 'Users', cpu,
                        'Onedrive - PAR Technology Corporation',
                        'Demand Planning', 'AX Reports')

f = it.inv_tools("Instance")
s = it.simulation("Instance")

# f.inv_god("M6150", 500)

s.run(1)

# can't print inventory or costs at end?
# print(f.oh_dict)
# print(json.dumps(f.costs))
