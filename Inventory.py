import os
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

# f = it.inv_tools("Instance")
# r = it.rework("Instance")
s = it.simulation("Instance")

# simulation for regular PAR
# s.run(1)

# simulation for postponement/riskpooling PAR
s.run2(200)

# save metrics in inventory.py?
# print(f.costs)
