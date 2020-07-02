import json
import operator
from numpy import random

# needs: ============================
# tweak data structure
# Assume monkeys run the business and remove reworks

# Assumptions =======================
# 1) inventory like RAM, SSD, and Stands are in infinite supply. The purpose
# of this model is to simulate how the supply chain can operate under the
# different scenarios where the ES600 is a buy, make, and hybrid model


# Creating a "class" object
class inv_tools:
    def __init__(self, name):
        self.name = name

        # All terminals
        self.terminals = ['M6150', 'M6150-01', 'M6150-02', 'M6150-03',
                          'M6150-10']

        # components that go into terminals
        self.components = ['SSD.64GB', 'SSD.128GB', 'RAM.4GB', 'RAM.8GB',
                           'Stand']

        self.values = {'M6150': 430, 'M6150-01': 435, 'M6150-02': 559,
                       'M6150-03': 520, 'M6150-10': 420,
                       'RAM.4GB': 59, 'RAM.8GB': 108,
                       'SSD.64GB': 47, 'SSD.128GB': 84,
                       'Stand': 21}

        # {Itemnumber: [Hard Drive, RAM, Stand]}
        self.bom = {'M6150': ['SSD.64GB', 'RAM.4GB', 'Stand'],
                    'M6150-01': ['SSD.128GB', 'RAM.4GB', 'Stand'],
                    'M6150-02': ['SSD.64GB', 'RAM.8GB', 'Stand'],
                    'M6150-03': ['SSD.128GB', 'RAM.8GB', 'Stand'],
                    'M6150-10': ['SSD.64GB', 'RAM.4GB'],
                    'RAM.4GB': ['RAM.4GB'],  # '980027040'
                    'RAM.8GB': ['RAM.8GB'],  # '980027040'
                    'SSD.64GB': ['SSD.64GB'],  # '980027040'
                    'SSD.128GB': ['SSD.128GB'],  # '980027040'
                    'Stand': ['Stand']}  # '980027040'

        # create dictionary for cost types
        self.costs = {"Total Cost": 0,
                      "Freight": {"Standard": {"Cost": 0.0, "Qty": 0.0},
                                  "Premium": {"Cost": 0.0, "Qty": 0.0}},
                      "Manufacturing": {"ReworkLabor": 0.0,
                                        "UnitsReworked": 0.0},
                      "Inventory": {}}

        self.plotdata = {"Standard Freight Cost": [],
                         "Standard Freight Units": [],
                         "Premium Freight Cost": [],
                         "Premium Freight Units": [],
                         "Total Inventory": [],
                         "Total Cost": []}

        self.oh_dict = {}
        self.rework_order = {}
        self.rework_labor = {}
        self.periodresults = {}

        # Different containers for simulations
        self.unoptimalplot = {}
        self.semioptimalplot = {}
        self.soptimalplot = {}

    # Tracking data throughout simulation ===================================
    # using this as a container for each metric I want to track to aggregate
    # and append into "plotdata" object
    def periodstats(self, Period, Stats=["Standard Freight Cost",
                                         "Standard Freight Units",
                                         "Premium Freight Cost",
                                         "Premium Freight Units",
                                         "Total Inventory",
                                         "Total Cost"]):
        if Period in self.periodresults.keys():
            pass
        else:
            self.periodresults[Period] = {}
            for stat in Stats:
                self.periodresults[Period][stat] = 0.0

    def periodstatsplot(self, period):
        # inventory values
        totalvalue = 0
        for item in self.oh_dict:
            totalvalue += self.oh_dict[item] * self.values[item]
        self.periodresults[period]["Total Inventory"] = totalvalue

        self.plotdata["Standard Freight Cost"].\
            append(self.periodresults[period]["Standard Freight Cost"])
        self.plotdata["Standard Freight Units"].\
            append(self.periodresults[period]["Standard Freight Units"])
        self.plotdata["Premium Freight Cost"].\
            append(self.periodresults[period]["Premium Freight Cost"])
        self.plotdata["Premium Freight Units"].\
            append(self.periodresults[period]["Premium Freight Units"])
        self.plotdata["Total Inventory"].\
            append(self.periodresults[period]["Total Inventory"])
        self.plotdata["Total Cost"].\
            append(self.periodresults[period]["Standard Freight Cost"] +
                   self.periodresults[period]["Premium Freight Cost"] +
                   self.periodresults[period]["Total Inventory"])

    # INVENTORY FUNCTIONS ===================================================
    # function to reset inventory before each simulation run need to turn
    # inventory to zero after first (non-optimized) simulation is run
    def simset(self):
        self.rework_order = {}
        self.rework_labor = {}
        self.periodresults = {}
        for item in self.bom:
            self.oh_dict[item] = 0
            for component in self.bom[item]:
                self.oh_dict[component] = 0
        self.costs = {"Total Cost": 0,
                      "Freight": {"Standard": {"Cost": 0.0, "Qty": 0.0},
                                  "Premium": {"Cost": 0.0, "Qty": 0.0}},
                      "Manufacturing": {"ReworkLabor": 0.0,
                                        "UnitsReworked": 0.0},
                      "Inventory": {}}

    def build(self, model, qty, period):
        print("\t\t\tBuilding", model, "with:")
        for component in self.bom[model]:
            onhand = self.oh_dict[component]
            if qty > onhand:
                orderqty = qty - onhand
                self.freight(component, orderqty, "Premium", period)
                self.add_inventory(component, orderqty)
                print("\t\t\t", str(qty), component)
                self.remove_inventory(component, qty)
            else:
                print("\t\t\t", str(qty), component)
                self.remove_inventory(component, qty)

    # safety valve to send back unused units to POSBank
    def compsafetyvalve(self, num):
        for component in self.components:
            qtyoh = self.oh_dict[component]
            if qtyoh > num:
                qtysendback = qtyoh - num
                self.remove_inventory(component, qtysendback)

    # MAX REPORT AS FINISHED
    # will check to see how much of a part is available
    def maxreportaf(self, model):
        max = 0
        counter = 1
        for component in self.bom[model]:
            ohqty = self.oh_dict[component]
            if counter == 1:
                max = ohqty
            elif ohqty < max:
                max = ohqty
        return(max)

    # move items from components to terminals
    # used to help second simulation
    def thechange(self, items=['RAM.4GB', 'RAM.8GB']):
        for i in items:
            # removing components and adding them to terminals
            self.components.remove(i)
            self.terminals += [i]
            # adjusting value to get the "shell" of terminal with ram
            self.values[i] += 383

    # creating function to return desired inventory metrics
    # like total value, units on hand by type, etc
    def inventorymetrics(self):
        # inventory values
        invdict = {}
        totalvalue = 0
        for item in self.oh_dict:
            totalvalue += self.oh_dict[item] * self.values[item]
        invdict["Inventory Value"] = totalvalue
        invdict["Units"] = self.oh_dict
        self.costs["Inventory"] = invdict

        # total cost
        self.costs["Total Cost"] += self.costs['Freight']["Standard"]["Cost"]
        self.costs["Total Cost"] += self.costs['Freight']["Premium"]["Cost"]
        self.costs["Total Cost"] += self.costs['Manufacturing']["ReworkLabor"]
        self.costs["Total Cost"] += self.costs['Inventory']["Inventory Value"]

    # Need to figure freight out... and net/average inventory
    def freight(self, Itemnumber, Qty, Freighttype, Period):
        # adding part we are bringing in into inventory
        # if item number is terminal, need to apply freight cost for terminal
        if Itemnumber in self.terminals:
            # freight cost per terminal for different methods
            standardfreight = 10.0
            premiumfreight = 45.0
            if Freighttype == "Premium":
                print("\tPremium freight:", Itemnumber, str(Qty))
                self.costs["Freight"]["Premium"]["Cost"]\
                    += premiumfreight * Qty
                self.costs["Freight"]["Premium"]["Qty"] += Qty

                # adding stats to periodresults
                self.periodresults[Period]["Premium Freight Cost"] +=\
                    premiumfreight * Qty
                self.periodresults[Period]["Premium Freight Units"] += Qty
            else:
                print("\tStandard freight:", Itemnumber, str(Qty))
                self.costs["Freight"]["Standard"]["Cost"]\
                    += standardfreight * Qty
                self.costs["Freight"]["Standard"]["Qty"] += Qty

                # adding stats to periodresults
                self.periodresults[Period]["Standard Freight Cost"] +=\
                    standardfreight * Qty
                self.periodresults[Period]["Standard Freight Units"] += Qty
        # if item is not a terminal
        else:
            # freight cost per component for different methods
            standardfreight = 5.0
            premiumfreight = 25.0
            if Freighttype == "Premium":
                print("\tPremium freight:", Itemnumber, str(Qty))
                self.costs["Freight"]["Premium"]["Cost"]\
                    += premiumfreight * Qty
                self.costs["Freight"]["Premium"]["Qty"] += Qty

                # adding stats to periodresults
                self.periodresults[Period]["Premium Freight Cost"] +=\
                    premiumfreight * Qty
                self.periodresults[Period]["Premium Freight Units"] += Qty
            else:
                print("\tStandard freight:", Itemnumber, str(Qty))
                self.costs["Freight"]["Standard"]["Cost"]\
                    += standardfreight * Qty
                self.costs["Freight"]["Standard"]["Qty"] += Qty

                # adding stats to periodresults
                self.periodresults[Period]["Standard Freight Cost"] +=\
                    standardfreight * Qty
                self.periodresults[Period]["Standard Freight Units"] += Qty

    # function to add inventory
    def add_inventory(self, part, qty):
        if part in self.oh_dict.keys():
            self.oh_dict[part] += qty
        else:
            self.oh_dict[part] = qty

    # function to reduce inventory
    def remove_inventory(self, part, qty):
        # checking to see if we can't remove inventory
        if self.oh_dict[part] > 0:
            self.oh_dict[part] -= qty

    # function to take forecasted quantity, subtract current inventory from
    # it and add the difference to inventory
    # ex: if inventory > forecast, do not need to order more inventory
    def mrp(self, part, forecast, period):
        if part in self.oh_dict.keys():
            inventory = self.oh_dict[part]
            if forecast > inventory:
                qty = forecast - inventory
                self.add_inventory(part, qty)
                print("\tAdding ", str(qty), part, "to inventory")
                self.freight(part, qty, 'Standard', period)
            else:
                print("\tInventory enough to cover forecast\n\n")
        else:
            self.oh_dict[part] = forecast

    # function to go through all parts forecast and add components to inventory
    def mrp2(self, demanddict, period):
        compforecast = {}
        for terminal in demanddict:
            # forecast quantity for terminal
            fcqty = demanddict[terminal][0]
            for component in self.bom[terminal]:
                if component in compforecast.keys():
                    compforecast[component] += fcqty
                else:
                    compforecast[component] = fcqty
        for component in compforecast:
            self.mrp(component, compforecast[component], period)

    # creating function that adds all necessary parts into/out of inventory
    # from rework info
    def get_gainz(self, have, need, qty, period):  # rework
        """
        Parameters
        ----------
        have : type
            The part we have available for rework
        need : type
            The item we need to turn the part we "have" into
        qty : type
            Qty of the part we are reworking

        Returns
        -------
        type
            Description of returned object.
        """
        # self.rework_comp(have, need)
        rework = self.rework_comp(have, need)
        # removing inventory needed to perform rework
        for i in rework["In"]:
            component = rework["In"][i]
            onhand = self.oh_dict[component]
            if qty > onhand:
                orderqty = qty - onhand
                self.freight(component, orderqty, "Premium", period)
                self.add_inventory(component, orderqty)
            print("\t\ttaking from inventory: ", component)
            self.remove_inventory(component, qty)
        # adding parts we need to take out of terminal and put into Inventory
        for i in rework["Out"]:
            component = rework["Out"][i]
            print("\t\tadding into inventory: ", component)
            self.add_inventory(component, qty)
        # removing terminal we used for the rework from inventory
        self.remove_inventory(have, qty)

    # ENGINEERING FUNCTIONS ===================================================
    # defining function to inform program what parts need to come in/out
    # of a terminal for a rework to happen... do not really need
    def rework_comp(self, have, need):  # rework
        have = self.bom[have]
        need = self.bom[need]

        comp_in = {}
        comp_out = {}

        # checking length of the BOM for terminal to see if stand is needed
        if len(have) > len(need):
            comp_out["Stand"] = "Stand"
        elif len(have) < len(need):
            comp_in["Stand"] = "Stand"
        else:
            pass

        # find components needed to take out of terminal
        counter = 1
        for component in need:
            if component not in have:
                if counter == 1:
                    comp_in['HD'] = component
                elif counter == 2:
                    comp_in['RAM'] = component
            counter += 1

        # find components needed to take out of terminal
        counter = 1
        for component in have:
            if component not in need:
                if counter == 1:
                    comp_out['HD'] = component
                if counter == 2:
                    comp_out['RAM'] = component
            counter += 1

        return({"In": comp_in, "Out": comp_out})
        # self.rework_in_out = {"In": comp_in, "Out": comp_out}
        # {In: {HD: SSD#, RAM: RAM#, Stand: Stand},
        # Out: {HD: SSD#, RAM: RAM#, Stand: Stand}}

    # Will find parts needed to put into and take out of terminal if needed
    # returns the score needed to rework each terminal we have into the
    # terminal we need
    def rework_rank(self, term_need):  # rework
        # different scores, higher means more difficulty/labor required
        stand_score, ssd_score, ram_score = 2, 5, 10

        # going to add cost of labor in as well
        stand_labor, ssd_labor, ram_labor = 10, 5, 20

        hw_need = self.bom[term_need]

        # want to create an algorithm that "weighs" the different terminals
        # I can reconfigure from, lower number will be less difficult to
        # rework than higher numbers
        if len(hw_need) == 3:
            for terminal in self.bom:
                if len(self.bom[terminal]) == 3 and terminal != term_need:
                    counter = 0
                    score = 0
                    labor = 0
                    # def getscore(self, terminal)
                    for components in self.bom[terminal]:
                        # Any component not in BOM is something I will need to
                        # add in and for the rework.
                        if components != hw_need[counter]:
                            if "SSD" in components:
                                score += ssd_score
                                labor += ssd_labor
                            elif "RAM" in components:
                                score += ram_score
                                labor += ram_labor
                        counter += 1
                    self.rework_order[score] = terminal
                    self.rework_labor[terminal] = labor

                # Creating seperate conditions for terminals with no stand
                # BOM has only a length of 2
                elif len(self.bom[terminal]) == 2 and terminal != term_need:
                    counter = 0
                    score = stand_score
                    labor = stand_labor
                    for components in self.bom[terminal]:
                        # Any component not in BOM is something I will need to
                        # add in and for the rework
                        if components != hw_need[counter]:
                            if "SSD" in components:
                                score += ssd_score
                                labor += ssd_labor
                            elif "RAM" in components:
                                score += ram_score
                                labor += ram_labor
                        counter += 1
                    self.rework_order[score] = terminal
                    self.rework_labor[terminal] = labor
        else:
            for terminal in self.bom:
                if len(self.bom[terminal]) == 3 and terminal != term_need:
                    counter = 0
                    score = stand_score
                    labor = stand_labor
                    for components in self.bom[terminal]:
                        # Any component not in BOM is something I will need to
                        # add in and for the rework.
                        if counter == 2:
                            pass
                        elif components != hw_need[counter]:
                            if "SSD" in components:
                                score += ssd_score
                                labor += ssd_labor
                            elif "RAM" in components:
                                score += ram_score
                                labor += ram_labor
                        counter += 1
                    self.rework_order[score] = terminal
                    self.rework_labor[terminal] = labor
        # self.rework_order = {score: terminal}
        # self.rework_labor = {terminal: labor}

    # SIMULATION BRAINS ======================================================
    # Inventory Gorilla, this guy just listens to what is cooking inside the
    # ERP System, no reworks, no brains, just pure animalistic instincts
    def inv_gorilla(self, model, demandqty, period):
        print("\tDemand for", str(demandqty), model, '\n')
        # model is the terminal called out on demand
        # demandqty is the quantity of the terminal needed
        # checking to see if demandqty of part on hand is enough to satisfy
        # demand
        if self.oh_dict[model] >= demandqty:
            self.remove_inventory(model, demandqty)

        else:
            # when demand is higher than inventory just expedite remaining
            # freight in
            qtyshort = demandqty - self.oh_dict[model]
            # expediting freight here
            self.freight(model, qtyshort, "Premium", period)

    # Inventory god function, somwhat smarter than the Gorilla
    # finds the parts you are looking for and decides if a rework is needed.
    # If rework is needed, will find the parts needed to perform rework
    # and expedite in
    def inv_god(self, model, demandqty, period):
        print("\tDemand for", str(demandqty), model, '\n')
        # model is the terminal called out on demand
        # demandqty is the quantity of the terminal needed
        # checking to see if demandqty of part on hand is enough to satisfy
        # demand
        if self.oh_dict[model] >= demandqty:
            self.remove_inventory(model, demandqty)

        else:
            # when demand is higher than inventory, add function in to
            # keep track of terminals I need to expedite in
            print("\tRework Required")

            # getting total quantity of terminals we are short
            qtyshort = demandqty - self.oh_dict[model]
            # qty = qtyshort
            # expediting freight here
            # self.freight(model, qtyshort, "Premium", period)

            # removing what is left of this part from inventory
            self.remove_inventory(model, self.oh_dict[model])

            # sorting rework order from least to most difficult
            self.rework_rank(model)
            order = sorted(self.rework_order.items(),
                           key=operator.itemgetter(0))

            print("\tQty left:", str(qtyshort), "\n")
            for score, terminal in order:
                ohqty = self.oh_dict[terminal]
                if ohqty > 0:
                    if qtyshort > 0:
                        print("\t\tReworking:", terminal, "into", model)
                        # if ohqty larger than qtyshort then take the terminal
                        # qty we are short. Else, we are taking everything in
                        # inventory we have of that part
                        if ohqty > qtyshort:
                            print("\t\tQty Taking: ", qtyshort)
                            # adding and removing components from invetory
                            self.get_gainz(terminal, model, qtyshort, period)

                            # adding associated rework costs to dictionary
                            self.costs["Manufacturing"]["UnitsReworked"]\
                                += qtyshort
                            self.costs["Manufacturing"]["ReworkLabor"]\
                                += qtyshort * self.rework_labor[terminal]

                            # decrementing total quantity short
                            qtyshort -= qtyshort
                            print("\t\tDemand Qty left:", str(qtyshort), "\n")
                        else:
                            print("\t\tQty Taking: ", ohqty)
                            # adding and removing components from invetory
                            self.get_gainz(terminal, model, ohqty, period)

                            # adding associated rework costs to dictionary
                            self.costs["Manufacturing"]["UnitsReworked"]\
                                += ohqty
                            self.costs["Manufacturing"]["ReworkLabor"]\
                                += ohqty * self.rework_labor[terminal]

                            # decrementing total quantity short
                            qtyshort -= ohqty
                            print("\t\tDemand Qty left:", str(qtyshort), "\n")
                else:
                    pass
            # adding inventory ERP system would have said to expedite here
            # self.add_inventory(model, qty)

    # Inventory Deity =======================================================
    # Inventory god function, finds the parts you are looking for
    # and decides if a rework is needed
    def inv_deity(self, model, demandqty, period):
        print("\tDemand for", str(demandqty), model, '\n')
        # model is the terminal called out on demand
        # demandqty is the quantity of the terminal needed
        # checking to see if demandqty of part on hand is enough to satisfy
        # demand
        if self.maxreportaf(model) >= demandqty:
            self.build(model, demandqty, period)


class simulation:
    def __init__(self, np):
        # np = how many times I want to run simulation
        # Demand information

        # {Terminal: [Forecast, Demand]}
        self.demand = {}
        '''
        self.demand = {'M6150': [10, 100],
                       'M6150-01': [10, 10],
                       'M6150-02': [10, 10],
                       'M6150-03': [10, 10],
                       'M6150-10': [10, 10]}
        '''
    # function to make forecast and demand for parts
    # {Part Number: [Forecast, Demand]}
    def demandfc(self):
        self.demand = {'M6150': [round(abs(random.normal(700, 10)), 0),
                                 round(abs(random.normal(200, 200)), 0)],
                       'M6150-01': [round(abs(random.normal(400, 10)), 0),
                                    round(abs(random.normal(600, 150)), 0)],
                       'M6150-02': [round(abs(random.normal(0, 0)), 0),
                                    round(abs(random.normal(50, 10)), 0)],
                       'M6150-03': [round(abs(random.normal(200, 10)), 0),
                                    round(abs(random.normal(100, 10)), 0)],
                       'M6150-10': [round(abs(random.normal(0, 0)), 0),
                                    round(abs(random.normal(50, 10)), 0)]}

    # Simulation for PAR if it was run by Gorillas
    def run0(self, np):
        random.seed(123)
        # np = number of periods I want to run simulation
        p = 1

        # need to tell simulation I will need to call inv_tools
        f = inv_tools("Something")

        f.simset()

        while p <= np:
            f.periodstats(p)
            print("\nPeriod:", str(p), "=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=\n\n\n")

            # setting random variables at the beginning of each iteration
            # {Terminal: [Forecast,
            #             Demand]}
            self.demandfc()

            # running MRP function to see what needs to be added to inventory
            # first
            print("Running MRP =========================================== \n")
            for item in self.demand:
                print(f.oh_dict)
                forecast = self.demand[item][0]

                print("\n", item, "\n\tForecast:", str(forecast),
                      "\n\tInventory:", str(f.oh_dict[item]), "\n")
                f.mrp(item, forecast, p)

            print("\n\n\n\nModeling Demand =============================== \n")
            for item in self.demand:
                print(f.oh_dict)
                forecast = self.demand[item][0]
                demand = self.demand[item][1]
                inventory = f.oh_dict[item]

                print(item, "\n\tForecast:", str(forecast),
                      "\n\tInventory:", str(inventory))

                # now time for the real demand for the part
                f.inv_gorilla(item, demand, p)

            f.periodstatsplot(p)
            p += 1

        f.inventorymetrics()
        # print("\n\nReturning Total Cost Data")
        print(json.dumps(f.costs))
        # print("\n\nReturning Data for Plot")
        f.unoptimalplot = f.plotdata
        print(f.unoptimalplot)
        return(f.unoptimalplot)

    # simulation for regular PAR
    def run1(self, np):
        random.seed(123)
        # np = number of periods I want to run simulation
        p = 1

        # need to tell simulation I will need to call inv_tools
        f = inv_tools("Something")

        f.simset()

        while p <= np:
            f.periodstats(p)
            print("\nPeriod:", str(p), "=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=\n\n\n")

            # setting random variables at the beginning of each iteration
            # {Terminal: [Forecast,
            #             Demand]}
            self.demandfc()

            # running MRP function to see what needs to be added to inventory
            # first
            print("Running MRP =========================================== \n")
            for item in self.demand:
                print(f.oh_dict)
                forecast = self.demand[item][0]

                print("\n", item, "\n\tForecast:", str(forecast),
                      "\n\tInventory:", str(f.oh_dict[item]), "\n")
                f.mrp(item, forecast, p)

            print("\n\n\n\nModeling Demand =============================== \n")
            for item in self.demand:
                print(f.oh_dict)
                forecast = self.demand[item][0]
                demand = self.demand[item][1]
                inventory = f.oh_dict[item]

                print(item, "\n\tForecast:", str(forecast),
                      "\n\tInventory:", str(inventory))

                # now time for the real demand for the part
                f.inv_god(item, demand, p)
                f.compsafetyvalve(800)

            f.periodstatsplot(p)
            p += 1

        f.inventorymetrics()
        # print("\n\nReturning Total Cost Data")
        print(json.dumps(f.costs))
        # print("\n\nReturning Data for Plot")
        f.semioptimalplot = f.plotdata
        print(f.semioptimalplot)
        return(f.semioptimalplot)

    # simulation for postponement/riskpooling PAR
    def run2(self, np):
        # setting seed
        random.seed(123)

        # np = number of periods I want to run simulation
        p = 1

        # need to tell simulation I will need to call inv_tools
        f = inv_tools("Something")

        f.simset()
        f.thechange()

        while p <= np:
            f.periodstats(p)
            print("\nPeriod:", str(p), "=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=\n\n\n")

            # setting random variables at the beginning of each iteration
            # {Terminal: [Forecast, Demand]}
            self.demandfc()

            # running MRP function to see what needs to be added to inventory
            # first
            print("Running MRP =========================================== \n")

            for item in self.demand:
                forecast = self.demand[item][0]
                demand = self.demand[item][1]
                inventory = f.oh_dict[item]

                print(item, "\n\tForecast:", str(forecast),
                      "\n\tInventory:", str(inventory))
            f.mrp2(self.demand, p)

            print("\n\n\n\nModeling Demand =============================== \n")
            for item in self.demand:
                print(f.oh_dict)
                forecast = self.demand[item][0]
                demand = self.demand[item][1]
                inventory = f.oh_dict[item]

                print(item, "\n\tForecast:", str(forecast),
                      "\n\tInventory:", str(inventory))

                # now time for the real demand for the part
                f.inv_deity(item, demand, p)
                f.compsafetyvalve(800)

            f.periodstatsplot(p)
            p += 1

        f.inventorymetrics()
        # print("\n\nReturning Total Cost Data")
        print(json.dumps(f.costs))
        # print("\n\nReturning Data for Plot")
        f.soptimalplot = f.plotdata
        print(f.soptimalplot)
        return(f.soptimalplot)
