Perishable products Inventory Management using MC Simulation

Perishable products require accurate inventory control models as their effect on operations management can be critical. Food items such as unprocessed dairy products, or meats or even some medicines require proper handling and have a low shelf-life. The restocking size becomes an important variable considering the uncertain demand and limited storage capacity. Products may also suffer from possible damages during deliveries. The importance of the management was particularly observed during the Pandemic. Thus, it is crucial to have an estimate of demand while restocking so that wastage is avoided and profits are maximized. 

Objective:
Our main objective is to investigate the effect of adopting an optimum inventory for these perishable goods. And we plan on using Monte Carlo in order to simulate various scenarios and thus, calculating the effective loss for each.

Scenarios:
We have successfully created experiments for two different scenarios. In the first scenario we assume that we do not have an estimate of the demand, and thus we restock the inventory to its full capacity. We check and discard the expired items on a daily basis. However, the restocking is done weekly and we drop the items that are defective at the same time. 
For the second scenario, we restock based on previous week’s demand. Checking for expired items is still performed on a daily basis. Restocking and checking for any defectives is also done weekly as per previous scenario.

Hypothesis:
We hypothesize that restocking on the basis of demand will optimize our cost and minimize wastage.

Flowchart:

********Insert Flowchart*************
We first get the initial inventory for both the items which is stored as a data frame which mentions the product’s expiry as well. We then check the daily demand and accordingly drop the items that are sold. At the end of the day, we reduce 1 day from each item’s expiry. We check for expired items and if any, drop those items on a daily basis. These expired items are then added to the weekly wastage. After each day, we check if a week is completed.  At the end of each week, we check for any defective items and add them to the weekly wastage. The restocking logic is then initiated. 
If simulating for Scenario 1, we restock up to the full capacity of the inventory by appending new rows which represents the items that are restocked. 
In Scenario 2, instead of restocking to full capacity, we only restock the items based on the previous week’s demand till the time it expired. 
We repeat the same process every week and, in the end, display the summary statistics for 1 month (i.e., 4 weeks)

Assumptions:
We have designed the model based on the following assumptions:
i.	We are performing the experiment for 28 days i.e. 4 weeks.
ii.	Considering 2 items: A and B. A has a very low-shelf-life i.e. 3 days whereas B has a relatively higher 5 day shelf life.
iii.	Storage capacity for each product is 100 and it is fixed.
iv.	Cost per product A is 15$ and that per product B is 10$
v.	Profit per product A is 5$ and that per product B is 3$
vi.	If expiry of an item is more than a week i.e. 7 days, then there won’t be any missed opportunities.


Data Structure:
We are using DataFrame as our primary data structure for the Inventory. As it can be seen in the first picture, dataframe has 2 columns for 2 items. Each row of the dataframe represents each item and its corresponding expiry. The total number of rows at any given point represents the number of items in stock.
The screenshot to the right, is an instance of restocking at the end of the week. We can clearly see that the product A which had an expiry of 10 days will only have 3 days left at the end of the week. The new stock of product A will have an expiry of 10 days. It can be seen in the red highlighted rows. In this case, we had to restock 15 items.

Variables of uncertainty:
i.	Demand: It uses PERT distribution to calculate demand for each day for each item.
As it can be seen, the stock_demand is a dictionary of lists of with item A and item B as its keys. For 28 days, we can see 28 random values of demand that are generated.
ii.	Defective Items: We generate a random number between 5 to 10. This number represents the percentage of defective items from the total items which are to be restocked.

We evaluate the scenarios on the basis of 2 things:
i.	Loss 
ii.	Missed Profit

Loss is calculated as the cost of expired items + cost of defective items.
The missed opportunity is calculated as the profit that could have been made for missed orders. Orders are missed if there is not enough stock.

Results:
