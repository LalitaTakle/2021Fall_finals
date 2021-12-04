import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statistics import mean


def mod_pert_random(low, likely, high, confidence=4, samples=1):
    """Produce random numbers according to the 'Modified PERT' distribution.

    :param low: The lowest value expected as possible.
    :param likely: The 'most likely' value, statistically, the mode.
    :param high: The highest value expected as possible.
    :param confidence: This is typically called 'lambda' in literature
                        about the Modified PERT distribution. The value
                        4 here matches the standard PERT curve. Higher
                        values indicate higher confidence in the mode.
                        Currently allows values 1-18

    I got this function from Professor Weible's class examples :
    https://github.com/iSchool-597PR/Examples_2021Fall/blob/main/week_07/Probability_Distributions.ipynb
    """
    # Check for reasonable confidence levels to allow:
    if confidence < 1 or confidence > 18:
        raise ValueError('confidence value must be in range 1-18.')

    mean1 = (low + confidence * likely + high) / (confidence + 2)

    a = (mean1 - low) / (high - low) * (confidence + 2)
    b = ((confidence + 1) * high - low - confidence * likely) / (high - low)

    beta = np.random.beta(a, b, samples)
    beta = beta * (high - low) + low
    beta = [int(x) for x in beta]
    return beta


def initial_stock():
    '''
    Generates inventory dataframe, storage capacity for each item and initializes expiry days for all items

    :return: Inventory Dataframe, Expiry dictionary and storage
    '''
    expiry_days = {'A': 3, 'B': 5}
    storage = 100
    df_stock = pd.DataFrame({'A': [expiry_days['A']] * storage, 'B': [expiry_days['B']] * storage})
    return df_stock, expiry_days, storage


def demand_items(storage):
    '''
    Generates daily demand using PERT for each item and stores it in a list corresponding to each item key in dictionary.

    :param storage: maximum storage capacity for each item
    :return: a dictionary of lists of daily demand for each item
    '''
    days_to_run = 28
    stock_demand = {'A': mod_pert_random(0.15 * storage, 0.18 * storage, 0.20 * storage, samples=days_to_run),
                    'B': mod_pert_random(0.10 * storage, 0.12 * storage, 0.15 * storage, samples=days_to_run)}
    return stock_demand


def defective(items):
    '''
    Generates a random integer which represents the number of defective items form the total restocked items.

    :param items: total number of items to be restocked, out of which we check the defective items
    :return: an integer number of defective items
    '''
    percent_of_defective = np.random.choice(list(range(5, 11)))
    defective_items = (items * percent_of_defective) // 100
    return defective_items


def item_df(df):
    '''
    Makes a list of dataframes for each item

    :param df: Whole dataframe with each column as each item and number of rows represent the number of itemsw in stock
    :return: list of dataframes for each item
    '''
    l1 = list(df.columns)
    df_list = []
    for i in l1:
        df_list.append(df[[i]].copy())
    return df_list


def loss(missed, weekly_wastage, key):
    '''
    Calculates total loss and total missed profit for each item

    :param missed: Number of missed orders due to no stock
    :param weekly_wastage: Number of waste items because they were defctive or expired
    :param key: Name of item (A or B)
    :return: List of loss and missed profit
    '''
    cost_a = 15
    cost_b = 10
    profit_a = 5
    profit_b = 3

    if key == 'A':
        total_loss = (cost_a * weekly_wastage)
        missed_profit = (missed * profit_a)
    else:
        total_loss = (cost_b * weekly_wastage)
        missed_profit = (missed * profit_b)

    return [total_loss, missed_profit]


def restocking(scenario, storage, df, weekly_demand):
    '''
    Generates the total number of items to be restocked in the inventory on the basis of type of scenario

    :param scenario: type of scenario (1 or 2)
    :param storage: storage capacity for each item
    :param df: Dataframe of item (current stock)
    :param weekly_demand: Previous week's demand (integer)
    :return: an integer number of the items to be restocked
    '''
    if scenario == 1:
        items_to_restock = storage - df.shape[0]
        return items_to_restock

    if scenario == 2:
        items_to_restock = weekly_demand  # restocks to full capacity

        if items_to_restock > storage:
            items_to_restock = storage - df.shape[0]

        return items_to_restock


def update_inventory(a, expiry, storage, scenario):
    '''
    Updates the inventory on the basis of demand.
    Drops sold and expired items each day and at the end of each week, calls the restocking function to restock the inventory.

    :param a: Dataframe of inventory with all items
    :param expiry: Dictionary of expiry days for all items
    :param storage: storage capacity for each item
    :param scenario: type of scenario (1 or 2)
    :return: list of Dictionaries for loss and missed profit. Each dictionary again contains a list for each item.
    '''
    demand = demand_items(storage)
    df_list = item_df(a)
    wastage_dict = {'A': [], 'B': []}
    loss_dict = {'A': [], 'B': []}
    missed_profit_dict = {'A': [], 'B': []}

    for df, k in zip(df_list, demand):  # dataframe and demand
        week = 1
        day = 1
        weekly_expired_items = 0
        missed = 0
        weekly_demand = 0

        for i in demand[k]:  # demand for each day

            if day <= expiry[k]:
                weekly_demand += i

            if i <= df.shape[0]:
                df.drop(df.index[:i], axis=0, inplace=True)  # sold items
                df.reset_index(inplace=True, drop=True)

            else:
                missed += i

            df[k] = df[k] - 1  # remaining days before expiry

            weekly_expired_items += df[df[k] < 0].count()[0]  # expired items

            df.drop(df[df[k] < 0].index, inplace=True)
            df.reset_index(inplace=True, drop=True)

            if day == 7:
                items_to_restock = restocking(scenario, storage, df, weekly_demand)

                df2 = pd.DataFrame(list([expiry[k]] * items_to_restock), columns=list(k))
                df = df.append(df2, ignore_index=True)

                weekly_defective = defective(items_to_restock)
                weekly_wastage = weekly_defective + weekly_expired_items
                weekly_loss = loss(missed, weekly_wastage, k)

                wastage_dict[k].append(weekly_wastage)
                loss_dict[k].append(weekly_loss[0])
                missed_profit_dict[k].append(weekly_loss[1])

                day = 0
                weekly_expired_items = 0
                week += 1
                weekly_demand = 0
                missed = 0

            day = day + 1

    return [loss_dict, missed_profit_dict]


def mc_simulation():
    '''
    Runs the program multiple times as specified by the user in number of simulations.
    Also plots graphs to represent the aggregate statistics after all simulations.

    :return: None
    '''
    loss_simulation_dict = {1: {'A': [], 'B': []}, 2: {'A': [], 'B': []}}
    missed_opportunity_simulation_dict = {1: {'A': [], 'B': []}, 2: {'A': [], 'B': []}}
    simulations = int(input('Enter number of simulations\n'))
    flag = 0
    while True:
        how_to_restock = int(input(
            "1. Press '1' to restock weekly to full capacity\n2. Press '2' to restock weekly based on demand\n3. Press '3' for comparison\n4. Press '4' to exit\n"))
        if how_to_restock == 4:
            break

        if how_to_restock < 3:
            flag += 1
            for j in range(simulations):
                i, e, s = initial_stock()
                u1 = update_inventory(i, e, s, how_to_restock)
                for k in loss_simulation_dict[how_to_restock]:
                    loss_simulation_dict[how_to_restock][k].append(sum(u1[0][k]))
                    missed_opportunity_simulation_dict[how_to_restock][k].append(sum(u1[1][k]))

            for k in loss_simulation_dict[how_to_restock]:
                i, e, s = initial_stock()
                lb = str(k) + '(' + str(e[k]) + ' days)'
                plt.figure(1, figsize=(8, 5))
                plt.tight_layout(pad=2)
                st = 'Scenario ' + str(how_to_restock)
                plt.suptitle(st)

                plt.subplot(121)
                plt.title('Loss (Monthly)')
                plt.xlabel('Number of simulations')
                plt.ylabel('Loss (in $)')
                plt.plot(loss_simulation_dict[how_to_restock][k], label=lb)
                plt.legend()

                plt.subplot(122)
                plt.title('Missed Opportunity (Monthly)')
                plt.xlabel('Number of simulations')
                plt.ylabel('Profit (in $)')
                plt.plot(missed_opportunity_simulation_dict[how_to_restock][k], label=lb)
                plt.legend()

            plt.show()

        if how_to_restock == 3:
            if flag != 2:
                print('Please run both simulations first\n')
            else:
                for k in loss_simulation_dict:
                    for j in loss_simulation_dict[k]:
                        l2 = 'Scenario_' + str(k) + '_Item_'+j
                        plt.figure(2, figsize=(8, 5))
                        plt.tight_layout(pad=2)
                        st = 'Scenario 1    vs    Scenario 2 '
                        plt.suptitle(st)

                        plt.subplot(121)
                        plt.title('Loss (Monthly)')
                        plt.xlabel('Number of simulations')
                        plt.ylabel('Loss (in $)')
                        plt.plot(loss_simulation_dict[k][j], label=l2)
                        plt.legend()

                        plt.subplot(122)
                        plt.title('Missed Opportunity (Monthly)')
                        plt.xlabel('Number of simulations')
                        plt.ylabel('Profit (in $)')
                        plt.plot(missed_opportunity_simulation_dict[k][j], label=l2)
                        plt.legend()

                plt.figure(3, figsize=(8, 5))
                plt.title('Average Monthly Loss (Including all items)')
                plt.ylabel('Loss (in $)')
                s1_avg = mean(loss_simulation_dict[1]['A'])+mean(loss_simulation_dict[1]['B'])
                s2_avg = mean(loss_simulation_dict[2]['A'])+mean(loss_simulation_dict[2]['B'])
                plt.bar(['Scenario 1', 'Scenario 2'], [s1_avg, s2_avg])
                plt.show()


if __name__ == '__main__':
    mc_simulation()
