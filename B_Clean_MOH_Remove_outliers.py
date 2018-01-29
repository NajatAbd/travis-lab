
# coding: utf-8

# In[1]:

import csv
import time
import numpy as np
import sys
import pandas as p
import unicodedata
from tqdm import tqdm

# In[8]:

reload(sys)
sys.setdefaultencoding("utf-8")

# In[10]:

'''
Description: remove the upper and lower 5% of the neighborhood transactions
Input:
    AllData: MOJ data for a single neighborhood
    iq_range: Percentage of the data to be kept
Output:
    MOJ data for a single neighborhood with outliers removed
'''
def reject_outliers_data(AllData, iq_range=0.5):
    pcnt = (1 - iq_range) / 2
    sr = p.Series(AllData[:,10].astype(float))
    AllDataNew = []
    qlow, median, qhigh = sr.dropna().quantile([pcnt, 0.50, 1-pcnt])
    iqr = qhigh - qlow
    for i,item in enumerate(AllData):
        if np.abs(float(item[10]) - median) <= iqr:
            AllDataNew.append(item)
    return np.array(AllDataNew)


# In[14]:

'''
Description: remove the upper and lower 5% of the neighborhood transactions
Input:
    TransactionsData: MOJ data for all neighborhoods
Output:
    MOJ data for all neighborhoods with outliers removed
'''
#The data should be in the following form (as a Numpy Array)
#Year,Month,Neighborhood,Cat,Type,Plan,Parcel,TID,TotalCost,Area,PPSM,City,Date,NewNeighborhood,NewMunc
def RemoveOutliers(TransactionsData):
    #Get the lis of all the neighborhoods in the transactionList
    NeighborhoodsList = p.DataFrame(TransactionsData[:,[13,14]])
    NeighborhoodsList = np.array(NeighborhoodsList.drop_duplicates(subset=[0,1]))
    CleanedTrans = []
    #Loop over every neighbourhood and remove the outlier transactions in the neighborhood
    for neigh in tqdm(NeighborhoodsList):
        select = np.logical_and(TransactionsData[:,13]==neigh[0],TransactionsData[:,14]==neigh[1])
        Neigh_transactions = TransactionsData[select]
        CleanedTrans_ForNeigh = np.array(reject_outliers_data(Neigh_transactions, iq_range=0.9))
        for item in CleanedTrans_ForNeigh:
            CleanedTrans.append(item)
    return CleanedTrans

