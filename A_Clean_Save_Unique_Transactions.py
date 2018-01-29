
# coding: utf-8

# In[1]:

import csv
import numpy as np
import sys
import pandas as p


# In[3]:

reload(sys)
sys.setdefaultencoding("utf-8")

# In[27]:

TransHeader = {
    'Year':0,
    'Month':1,
    'Neighborhood':2,
    'Cat':3,
    'Type':4,
    'Plan':5,
    'Parcel':6,
    'TID':7,
    'TotalCost':8,
    'Area':9,
    'PPSM':10,
    'City':11,
    'Date':12,
    'NewNeighborhood':13,
    'NewMunc':14
}


# In[52]:

#The data should be in the following form (as a Dataframe)
#Year,Month,Neighborhood,Cat,Type,Plan,Parcel,TID,TotalCost,Area,PPSM,City,Date,NewNeighborhood,NewMunc
'''
Description: Clean the data collected from MOJ website (Remove duplicates)
Input:
    TransactionsData: MOJ transactions data
Output:
    Transactions list with no duplicates
'''
def RemoveDups(TransactionsData):
    Trans = TransactionsData
    #Convert the Dataframe into a numpy array to loop over the items
    TransNp = np.array(TransactionsData)
    # tempAllTrans = TransNp
    
    Accepted = []
    Trans = []
    c = 0
    #Avoid eliminating transactions that cannot be identified by the parcelID or PlanNo
    for item in TransNp:
        if item[5] == str('مخطط/أخرى') or item[5] == str('مخطط/بدون') or item[6] == str('قطعة بدون'):
            Accepted.append(item)
            c+=1
        else:
            Trans.append(item)
    #Remove duplicates from the items that can be identified and add it to the final array
    Trans = p.DataFrame(Trans)
    Trans = Trans.sort_values(by=[0,1],ascending=[True,True])
    Trans = np.array(Trans.drop_duplicates(subset=[TransHeader['Cat'],TransHeader['Plan'],TransHeader['Parcel'],TransHeader['Area'],TransHeader['NewNeighborhood'],TransHeader['NewMunc']], keep='last', inplace=False))
    for item in Trans:
        Accepted.append(item[:15])

    # NewTemp = []
    # AcceptedTIDs = np.array(Accepted)[:,7].astype(int)
    # for item in tempAllTrans:
    #     if int(item[7]) not in AcceptedTIDs:
    #         NewTemp.append(item)
    # with open('Data/RejectedTrans.csv','wb') as csvfile:
    #     writer = csv.writer(csvfile,delimiter=',')
    #     for item in NewTemp:
    #         writer.writerow(item)

    NewTrans = np.array(Accepted)
    return NewTrans
def RemoveNeighborhoods(Transactions,NeighborhoodsList,BlackList):
    #Remove Unaccepted transactions (out of neetaq)
    NewTrans = []
    for Trans in Transactions:
        Accept = True
        for neigh in BlackList:
            if neigh[0] == Trans[13] and neigh[1] == Trans[14]:
                Accept = False
                break
        if Accept:
            NewTrans.append(Trans)
    #Remove Unaccepted neighborhoods (out of neetaq)
    NewNeigh = []
    for Neighborhood in NeighborhoodsList:
        Accept = True
        for neigh in BlackList:
            if neigh[0] == Neighborhood[0] and neigh[1] == Neighborhood[1]:
                Accept = False
                break
        if Accept:
            NewNeigh.append(Neighborhood)

    return np.array(NewTrans),np.array(NewNeigh)
