import pandas as pd

file = pd.read_excel('configfile.xlsx', skiprows=1)
print(file)

# finding terminal/components
is_terminal = file['type'] == 'Terminal'
is_component = file['type'] == 'Component'

terminals = file[is_terminal]['partnumber'].tolist()
components = file[is_component]['partnumber'].tolist()

# creating dictionary for part values
values = dict(zip(file.partnumber, file.value))

for i in file:
    column = file[[i]]
    for j in file[column]:
        print("asdfasdf")
        print(j)
