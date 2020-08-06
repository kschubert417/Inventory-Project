import json
import operator
import numpy as np
import pandas as pd
from numpy import random

import os
import logging
import logging.handlers
from pathlib import Path


# needs: ============================
# https://realpython.com/python-testing/#testing-your-code

class dataprep:
    def setup(self):
        # setting up logger ===================================================
        mdt = round(os.path.getmtime(os.path.basename(__file__)))
        log_path = 'logs/'
        Path(log_path).mkdir(parents=True, exist_ok=True)

        log_file_name = log_path+'inv_test.log'
        logging_level = logging.DEBUG
        formatter = logging.Formatter('''%(asctime)s,
                                      %(name)s, %(levelname)s, %(message)s''')
        handler = logging.handlers.TimedRotatingFileHandler(log_file_name,
                                                            when='midnight',
                                                            backupCount=365)
        handler.suffix = "%Y-%m-%d"

        handler.setFormatter(formatter)
        self.logger = logging.getLogger('invtestlog')
        self.logger.addHandler(handler)
        self.logger.setLevel(logging_level)
        self.logger.info("app: --------------------------------------------")
        self.logger.info("app: init. v: " + str(mdt))

        # General information =================================================
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
                    'M6150-10': ['SSD.64GB', 'RAM.4GB']}

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
        self.periodresults = {}
        self.demandinfo = {}

        # Different containers for simulation plots
        self.unoptimalplot = {}
        self.semioptimalplot = {}
        self.soptimalplot = {}

    # function to load data from configfile
    def loaddata(self):
        self.setup()

        # file name of the config configfile
        fn = "configfile.xlsx"
        self.logger.info("loading data from " + fn)

        itemmaster = pd.read_excel(fn, skiprows=1,
                                   sheet_name="itemmaster")

        # finding terminal/component part numbers
        is_terminal = itemmaster['type'] == 'Terminal'
        is_component = itemmaster['type'] == 'Component'

        # getting all terminal/component info from item master
        terminals = itemmaster[is_terminal]
        components = itemmaster[is_component]

        # getting list of terminals/components ================================
        # ['item1', 'item2', 'item3', 'item4']
        self.terminals = terminals['partnumber'].tolist()
        self.components = components['partnumber'].tolist()

        # creating dictionary for part values =================================
        # {Item: Value}
        self.values = dict(zip(itemmaster.partnumber, itemmaster.value))

        # creating bom info ===================================================
        # number of columns that contain BOM info I need

        # counting number of columns where BOMs live
        bomcount = 0
        for i in itemmaster:
            if "bom" in i:
                bomcount += 1

        # selecting columns I need to extract BOM info from
        bominfo = terminals.iloc[:, np.r_[0, 7:7+bomcount]]

        # initialize dictionary
        part_dict = {}

        # slice all but the first column
        columns = bominfo.columns[1:]

        # {'Part1': ['Component1', 'Component2', 'Component3']}
        for i in range(len(bominfo['partnumber'])):
            # store given part as variable
            part = bominfo['partnumber'][i]
            # make dict entry and initialize empty list
            part_dict[part] = []
            for col in columns:
                # append entry to list
                part_dict[part].append(bominfo.at[i, col])

        self.bom = part_dict

        # getting demand info =================================================
        # https://stackoverflow.com/questions/26716616/convert-a-pandas-dataframe-to-a-dictionary
        # number of columns that contain demand info
        n = 4

        demandinfo = terminals.iloc[:, np.r_[0, 3:3+n]]

        # {'Item': [Forecastmean, Forecaststd, Demandmean, Demandstd]}
        self.demandinfo = demandinfo.set_index('partnumber').T.to_dict('list')

        # =====================================================================
        # getting info to change simulation to a risk pooling based approach ==
        configchange = pd.read_excel(fn, "simchange", skiprows=1)

        # {'Part1': value}
        self.change = dict(zip(configchange.partnumber, configchange.newvalue))


# Creating a "class" object
class inv_tools(dataprep):
    def __init__(self):
        self.loaddata()

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
        self.costs["Total Cost"] += self.costs['Inventory']["Inventory Value"]

    def simset(self):
        self.rework_order = {}
        self.periodresults = {}
        for item in self.bom:
            self.oh_dict[item] = 0
            for component in self.bom[item]:
                self.oh_dict[component] = 0
        self.costs = {"Total Cost": 0,
                      "Freight": {"Standard": {"Cost": 0.0, "Qty": 0.0},
                                  "Premium": {"Cost": 0.0, "Qty": 0.0}},
                      "Manufacturing": {"UnitsReworked": 0.0},
                      "Inventory": {}}

    # move items from components to terminals
    # used to help second simulation
    def thechange(self, items={'RAM.4GB': 380, 'RAM.8GB': 451}):
        for i in items:
            # removing components and adding them to terminals
            self.components.remove(i)
            self.terminals += [i]
            # adjusting value to get the "shell" of terminal with ram
            self.values[i] = items[i]

    # INVENTORY FUNCTIONS ===================================================
    # function to reset inventory before each simulation run need to turn
    # inventory to zero after first (non-optimized) simulation is run
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

    # safety valve to send back unused units to POSBank
    def compsafetyvalve(self, num):
        for component in self.components:
            qtyoh = self.oh_dict[component]
            if qtyoh > num:
                qtysendback = qtyoh - num
                self.remove_inventory(component, qtysendback)

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

    # creating function that will add/remove parts from inventory as necessary
    # to perform reworks
    def get_gainz(self, have, need, qty, period):  # rework
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

        # find components needed to take out of terminal
        counter = 1
        for component in need:
            if component not in have:
                comp_in['Component' + '' + str(counter)] = component
            counter += 1

        # find components needed to take out of terminal
        counter = 1
        for component in have:
            if component not in need:
                comp_out['Component' + '' + str(counter)] = component
            counter += 1

        return({"In": comp_in, "Out": comp_out})
        # {In: {Component #: SSD.XXXXX, Component #: RAM.XXXXX,
        #       Component #: Stand},
        # Out: {Component #: SSD.XXXXX, Component #: RAM.XXXXX,
        #       Component #: Stand}}

    # Will find parts needed to put into and take out of terminal if needed
    # returns the score needed to rework each terminal we have into the
    # terminal we need
    def rework_rank(self, term_need):  # rework
        # different scores, higher means more difficulty required
        stand_score, ssd_score, ram_score = 2, 5, 10

        hw_need = self.bom[term_need]

        # want to create an algorithm that "weighs" the different terminals
        # I can reconfigure from, lower number will be less difficult to
        # rework than higher numbers
        if len(hw_need) == 3:
            for terminal in self.bom:
                if len(self.bom[terminal]) == 3 and terminal != term_need:
                    counter = 0
                    score = 0
                    # def getscore(self, terminal)
                    for components in self.bom[terminal]:
                        # Any component not in BOM is something I will need to
                        # add in and for the rework.
                        if components != hw_need[counter]:
                            if "SSD" in components:
                                score += ssd_score
                            elif "RAM" in components:
                                score += ram_score
                        counter += 1
                    self.rework_order[score] = terminal

                # Creating seperate conditions for terminals with no stand
                # BOM has only a length of 2
                elif len(self.bom[terminal]) == 2 and terminal != term_need:
                    counter = 0
                    score = stand_score
                    for components in self.bom[terminal]:
                        # Any component not in BOM is something I will need to
                        # add in and for the rework
                        if components != hw_need[counter]:
                            if "SSD" in components:
                                score += ssd_score
                            elif "RAM" in components:
                                score += ram_score
                        counter += 1
                    self.rework_order[score] = terminal
        else:
            for terminal in self.bom:
                if len(self.bom[terminal]) == 3 and terminal != term_need:
                    counter = 0
                    score = stand_score
                    for components in self.bom[terminal]:
                        # Any component not in BOM is something I will need to
                        # add in and for the rework.
                        if counter == 2:
                            pass
                        elif components != hw_need[counter]:
                            if "SSD" in components:
                                score += ssd_score
                            elif "RAM" in components:
                                score += ram_score
                        counter += 1
                    self.rework_order[score] = terminal
        # self.rework_order = {score: terminal}


    # Will find parts needed to put into and take out of terminal if needed
    # returns the score needed to rework each terminal we have into the
    # terminal we need
    def rework_rank2(self, term_need):  # rework

        hw_need = self.bom[term_need]

        # want to create an algorithm that "weighs" the different terminals
        # I can reconfigure from, lower number will be less difficult to
        # rework than higher numbers
        if len(hw_need) == 3:
            for terminal in self.bom:
                if terminal != term_need:
                    print(terminal)
                    counter = 1
                    score = 0
                    # def getscore(self, terminal)
                    for components in self.bom[terminal]:
                        print(components + " " + str(counter))
                        # Any component not in BOM is something I will need to
                        # add in and for the rework.
                        if components != hw_need[counter-1]:
                            score += counter
                        counter += 1
                    self.rework_order[score] = terminal
                else:
                    pass

        # self.rework_order = {score: terminal}



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
            self.rework_rank2(model)
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

        # {PartNumber: [Forecast, Demand]}
        self.demand = {}

    # function to make forecast and demand for parts
    # {PartNumber: [Forecast, Demand]}
    def demandfc(self, demandinfo):
        self.demand = {}
        for item in demandinfo:
            part = item

            # forecast stats (mean and standard deviation)
            fcmean = demandinfo[item][0]
            fcstd = demandinfo[item][1]

            # demand stats (mean and standard deviation)
            dmndmean = demandinfo[item][2]
            dmndstd = demandinfo[item][3]

            # getting forecast from demand data
            forecast = round(abs(random.normal(fcmean, fcstd)))
            demand = round(abs(random.normal(dmndmean, dmndstd)))

            self.demand[part] = [forecast, demand]

    # Simulation for PAR if it was run by Gorillas
    def run0(self, np):
        random.seed(123)
        # np = number of periods I want to run simulation
        p = 1

        # need to tell simulation I will need to call inv_tools
        f = inv_tools()

        # making sure simulation starts at absolute 0
        f.simset()

        while p <= np:
            f.periodstats(p)
            print("\nPeriod:", str(p), "=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=\n\n\n")

            # setting random variables at the beginning of each iteration
            # {Terminal: [Forecast,
            #             Demand]}
            # self.demandfc()
            self.demandfc(f.demandinfo)

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
        f = inv_tools()

        # making sure simulation starts at absolute 0
        f.simset()

        while p <= np:
            f.periodstats(p)
            print("\nPeriod:", str(p), "=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=\n\n\n")

            # setting random variables at the beginning of each iteration
            # {Terminal: [Forecast,
            #             Demand]}
            # self.demandfc()
            self.demandfc(f.demandinfo)

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
        f = inv_tools()

        # making sure simulation starts at absolute 0
        f.simset()
        f.thechange(f.change)

        while p <= np:
            f.periodstats(p)
            print("\nPeriod:", str(p), "=v=v=v=v=v=v=v=v=v=v=v=v=v=v=v=\n\n\n")

            # setting random variables at the beginning of each iteration
            # {Terminal: [Forecast, Demand]}
            # self.demandfc()
            self.demandfc(f.demandinfo)

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
