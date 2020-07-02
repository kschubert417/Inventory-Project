import os
import socket as soc
import inv_tools as it
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

s = it.simulation("Instance")

# number of times you want to run a simulation
n = int(input("Number of times to run simulation: "))

# Simulation for PAR if it was run by Gorillas
gorilla = s.run0(n)

# simulation for regular PAR
semioptimal = s.run1(n)

# simulation for postponement/riskpooling PAR
optimal = s.run2(n)

'''
"Standard Freight Cost",
"Standard Freight Units",
"Premium Freight Cost",
"Premium Freight Units",
"Total Inventory"
'''
# plotting data =============================================================
# Line Plots ===================================
# Inventory Value
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(y=gorilla["Total Inventory"],
                         mode='lines', name='Oversimplified Inventory Value'),
              secondary_y=False)
fig.add_trace(go.Scatter(y=semioptimal["Total Inventory"],
                         mode='lines', name='Semi-Optimal Inventory Value'),
              secondary_y=False)
fig.add_trace(go.Scatter(y=optimal["Total Inventory"],
                         mode='lines', name='Optimal Inventory Value'),
              secondary_y=False)
fig.update_layout(title='Inventory Value',
                  xaxis_title='Period',
                  yaxis_title='Value')
fig.show()


# Standard Freight Cost
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(y=gorilla["Standard Freight Cost"],
                         mode='lines', name='Oversimplified Inventory Value'),
              secondary_y=False)
fig.add_trace(go.Scatter(y=semioptimal["Standard Freight Cost"],
                         mode='lines', name='Semi-Optimal Inventory Value'),
              secondary_y=False)
fig.add_trace(go.Scatter(y=optimal["Standard Freight Cost"],
                         mode='lines', name='Optimal Inventory Value'),
              secondary_y=False)
fig.update_layout(title='Standard Freight Cost',
                  xaxis_title='Period',
                  yaxis_title='Value')
fig.show()


# Standard Freight Units
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(y=gorilla["Standard Freight Units"],
                         mode='lines', name='Oversimplified Inventory Units'),
              secondary_y=False)
fig.add_trace(go.Scatter(y=semioptimal["Standard Freight Units"],
                         mode='lines', name='Semi-Optimal Inventory Units'),
              secondary_y=False)
fig.add_trace(go.Scatter(y=optimal["Standard Freight Units"],
                         mode='lines', name='Optimal Inventory Units'),
              secondary_y=False)
fig.update_layout(title='Standard Freight Units',
                  xaxis_title='Period',
                  yaxis_title='Value')
fig.show()


# Premium Freight Cost
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(y=gorilla["Premium Freight Cost"],
                         mode='lines', name='Oversimplified Premium Freight Cost'),
              secondary_y=False)
fig.add_trace(go.Scatter(y=semioptimal["Premium Freight Cost"],
                         mode='lines', name='Semi-Optimal Premium Freight Cost'),
              secondary_y=False)
fig.add_trace(go.Scatter(y=optimal["Premium Freight Cost"],
                         mode='lines', name='Optimal Premium Freight Cost'),
              secondary_y=False)
fig.update_layout(title='Premium Freight Cost',
                  xaxis_title='Period',
                  yaxis_title='Value')
fig.show()


# Premium Freight Units
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(y=gorilla["Premium Freight Units"],
                         mode='lines', name='Oversimplified Premium Freight Units'),
              secondary_y=False)
fig.add_trace(go.Scatter(y=semioptimal["Premium Freight Units"],
                         mode='lines', name='Semi Optimal Premium Freight Units'),
              secondary_y=False)
fig.add_trace(go.Scatter(y=optimal["Premium Freight Units"],
                         mode='lines', name='Optimal-Premium Freight Units'),
              secondary_y=False)
fig.update_layout(title='Premium Freight Units',
                  xaxis_title='Period',
                  yaxis_title='Value')
fig.show()


# Total Cost
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(y=gorilla["Total Cost"],
                         mode='lines', name='Oversimplified Total Cost'),
              secondary_y=False)
fig.add_trace(go.Scatter(y=semioptimal["Total Cost"],
                         mode='lines', name='Semi-Optimal Total Cost'),
              secondary_y=False)
fig.add_trace(go.Scatter(y=optimal["Total Cost"],
                         mode='lines', name='Optimal Total Cost'),
              secondary_y=False)
fig.update_layout(title='Total Cost',
                  xaxis_title='Period',
                  yaxis_title='Value')
fig.show()


# Box Plots ===================================
fig = go.Figure()

fig.add_trace(go.Box(y=gorilla["Total Cost"], name='Oversimplified Total Cost'))
fig.add_trace(go.Box(y=semioptimal["Total Cost"],
                     name='Semi-Optimal Total Cost'))
fig.add_trace(go.Box(y=optimal["Total Cost"], name='Optimal Total Cost'))
fig.update_layout(title='Total Cost',
                  yaxis_title='Value')

fig.show()
