
# coding: utf-8

# In[3]:

import csv
import time
import numpy as np
import sys
from statsmodels.distributions.empirical_distribution import ECDF
import matplotlib.pyplot as plt
import pandas as p
from scipy.stats import gaussian_kde
from bidi.algorithm import get_display
import matplotlib.pyplot as plt
import arabic_reshaper
import math
import matplotlib as mpl
import matplotlib.cm as cm

# In[3]:

reload(sys)
sys.setdefaultencoding("utf-8")


# In[20]:

'''
Description: Generate MOJ data in a format that can be used later
Input:
    NewMOJ_Data: The ministry of justice transactions after all cleaning stages
    Neighs_list: The list of neighborhoods to be analyzed
Output:
    Prices of MOJ transactions
'''
def PrepareTransactionsPrices(NewMOJ_Data,Neighs_list):
    PricesData = []
    NewMOJ_Data = np.array(NewMOJ_Data)
    for neigh in Neighs_list:
        select = np.logical_and(NewMOJ_Data[:,13]==neigh[0],NewMOJ_Data[:,14]==neigh[1])
        temp_NewMOJ = NewMOJ_Data[select]
        
        Prices = temp_NewMOJ[:,10]
        
        PricesData.append(Prices)
    return PricesData


# In[69]:

'''
Description: Generate the ECDF result for every neighborhood
Input:
    PricesData: The prices of transactions grouped by neighborhood in a 2D array
    Neighs_list: The list of neighborhoods to be analyzed
Output:
    The sum of the ECDF for every neighborhood
    NoTransactionsNeighborhoods: The neighborhoods that doesn't have any transactions
'''
#Need to be reviewed
def GenerateECDFSum(PricesData,Neighs_list):
    #PricesData = np.array(PricesData)
    maxx = -1
    for row in PricesData:
        row = row.astype(float)
        if len(row)>0:
            if np.max(row)>maxx:
                maxx = np.max(row)
    numberOfDensityPoints = int(maxx/(100))
    All_ECDFs = []
    NoTransactionsNeighborhoods = []
    #Generate the ECDF for every neighborhood
    for i,row in enumerate(PricesData):
        try:
            x = row.astype(float)
            x = x/float(maxx)
            ecdf = ECDF(x)
            x = np.linspace(0,1,numberOfDensityPoints)
            y1 = ecdf(x)
            temp = []
            for item in y1:
                temp.append(item)
            #temp.append((len(row)/float(maxx2)))
            if len(row)>=1:
                All_ECDFs.append([temp,Neighs_list[i][0],Neighs_list[i][1]])
            else:
                NoTransactionsNeighborhoods.append([Neighs_list[i][0],Neighs_list[i][1]])
        except Exception as e:#Keep track of neighborhoods with no transactions
            #print e.args
            NoTransactionsNeighborhoods.append([Neighs_list[i][0],Neighs_list[i][1]])
            pass
    All_ECDFs = np.array(All_ECDFs)
    #for item in NoTransactionsNeighborhoods:
        #print item[0]
    All_ECDFs_Res = []
    for item in All_ECDFs:
        All_ECDFs_Res.append([1-np.sum(item[0]),item[1],item[2]])
    return All_ECDFs_Res,NoTransactionsNeighborhoods


# In[84]:

'''
Description: Scale a set of values from one range to another
Input:
    OldValue: The value that you need to scale
    OldMin: The minimum value of the current scale
    OldMax: The maximum value of the current scale
    NewMin: The minimum value of the new scale
    NewMax: The minimum value of the new scale
Output:
    The value after scalling it
'''
def scale(OldValue,OldMin,OldMax,NewMin,NewMax):
    return (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin


# In[73]:

'''
Description: Identify the median of every neighborhood
Input:
    PricesData: The prices of transactions grouped by neighborhood in a 2D array
Output:
    A list of medians for every neighborhood
'''
def IdentifyAllmedians(PricesData):
    PricesData = np.array(PricesData)
    Neigh_Medians = []
    for i,Neigh_transactions in enumerate(PricesData):
        if len(Neigh_transactions)>9:
            Neigh_Medians.append(np.median(Neigh_transactions.astype(float)))
    Neigh_Medians = np.array(Neigh_Medians)
    Sorted = np.argsort(Neigh_Medians.astype(float)*-1)
    Neigh_Medians = Neigh_Medians[Sorted]
    return Neigh_Medians

# def IdentifyAllmedians(PricesData):
#     PricesData = np.array(PricesData)
#     Neigh_Medians = []
#     for i,Neigh_transactions in enumerate(PricesData):
#         if len(Neigh_transactions)>9:
#             Neigh_transactions = Neigh_transactions.astype(float)
#             kde = gaussian_kde( list(Neigh_transactions) )
#             dist_space = np.linspace( min(Neigh_transactions), max(Neigh_transactions), len(Neigh_transactions) )
#             NeighMode = float(dist_space[np.argmax(kde(dist_space))])
#             Neigh_Medians.append(NeighMode)
#     Neigh_Medians = np.array(Neigh_Medians)
#     Sorted = np.argsort(Neigh_Medians.astype(float)*-1)
#     Neigh_Medians = Neigh_Medians[Sorted]
#     return Neigh_Medians

# In[86]:

'''
Description: Generate the neighborhood index using the ECDF methodology
Input:
    All_ECDFs_Res: The sum of the ECDF for every neighborhood
    Neighborhoods_Medians: The medians lis of all the neighborhoods
Output:
    A list of ECDF value for every neighborhood
'''
def GenerateECDFNeighborhoodIndex(All_ECDFs_Res,Neighborhoods_Medians,NeighborhoodsList):
    All_ECDFs_Res = np.array(All_ECDFs_Res)
    #Sort the ECDF sum values
    ECDF_NotSorted = np.array(All_ECDFs_Res)
    temp = [float(i[0]) for i in ECDF_NotSorted]
    Sorted = np.argsort(temp)
    ECDFNP = ECDF_NotSorted[Sorted]
    ECDFNP_new = []
    for item in ECDFNP:
        ECDFNP_new.append(item)
    ECDFNP = np.array(ECDFNP_new)

    temp = []
    temp2 = []
    
    Vals = [float(i[0]) for i in ECDFNP]
    #Identify the min, max values for the ECDF
    ArrMax = np.max(ECDFNP[:,0].astype(float))
    ArrMin = np.min(ECDFNP[ECDFNP[:,0].astype(float)<0.0][:,0].astype(float))
    ArrMean = np.mean(ECDFNP[ECDFNP[:,0].astype(float)<0.0][:,0].astype(float))
    
    #Normalize the ECDF values to be between 0 and 1
    for item in ECDFNP[:,0].astype(float):
        TheECDFVal = (((item - ArrMin)/(ArrMax - ArrMin)))
        temp.append(TheECDFVal)
    ECDFNP[:,0] = temp
    
    #plt.plot(range(len(ECDFNP[:,0])),ECDFNP[:,0].astype(float),'*')
    
    #Define the max and min medians in the city
    Lowest_Median = np.min(Neighborhoods_Medians)
    Highest_Median = np.max(Neighborhoods_Medians)
    print Lowest_Median,Highest_Median,'Medians'
    #Map the values to the scal of the min and max medians of the city
    ArrMax = np.max(ECDFNP[:,0].astype(float))
    ArrMin = np.min(ECDFNP[:,0].astype(float))
    ArrMean = np.mean(ECDFNP[:,0].astype(float))
    for item in ECDFNP[:,0].astype(float):
        TheVal = scale(item,ArrMin,ArrMax,Lowest_Median,Highest_Median)
        temp2.append(TheVal)
    ECDFNP[:,0] = temp2

    New_ECDFNP = []
    for neigh in ECDFNP:
        New_ECDFNP.append(neigh)

    for neighborhood in NeighborhoodsList:
        NoEstimation = True
        for neigh in ECDFNP:
            if neigh[1] == neighborhood[0] and neigh[2] == neighborhood[1]:
                NoEstimation = False
                break
        if NoEstimation:
            New_ECDFNP.append([np.nan,neighborhood[0],neighborhood[1]])

    ECDFNP = np.array(New_ECDFNP)
    return ECDFNP


# In[168]:

'''
Description: Generate the neighborhood index using the Median methodology
Input:
    PricesData: PricesData: The prices of transactions grouped by neighborhood in a 2D array
    (numpy -- [[price1,price2,...],[price1,price2,...],...])
    Neighs_list: The list of neighborhoods to be analyzed
Output:
    A list of median value for every neighborhood
'''
def GenerateMedianNeighborhoodIndex(PricesData,Neighs_list):
    PricesData = np.array(PricesData)
    AllMedians = []
    for i,row in enumerate(PricesData):
        if len(row)>9:
            try:
                AllMedians.append([np.median(row.astype(float)),Neighs_list[i][0],Neighs_list[i][1]])
            except:
                AllMedians.append([np.nan,Neighs_list[i][0],Neighs_list[i][1]])
                pass
        else:
            AllMedians.append([np.nan,Neighs_list[i][0],Neighs_list[i][1]])
    return AllMedians

'''
Description: Generate the neighborhood index using the Mean methodology
Input:
    PricesData: PricesData: The prices of transactions grouped by neighborhood in a 2D array
    (numpy -- [[price1,price2,...],[price1,price2,...],...])
    Neighs_list: The list of neighborhoods to be analyzed
Output:
    A list of mean value for every neighborhood
'''
def GenerateMeanNeighborhoodIndex(PricesData,Neighs_list):
    PricesData = np.array(PricesData)
    AllMeans = []
    for i,row in enumerate(PricesData):
        if len(row) > 9:
            AllMeans.append([np.mean(row.astype(float)),Neighs_list[i][0],Neighs_list[i][1]])
        else:
            AllMeans.append([np.nan,Neighs_list[i][0],Neighs_list[i][1]])
    return AllMeans
# In[180]:
'''
Description: Generate the number of transactions in every neighborhood
Input:
    PricesData: PricesData: The prices of transactions grouped by neighborhood in a 2D array
    (numpy -- [[price1,price2,...],[price1,price2,...],...])
    Neighs_list: The list of neighborhoods to be analyzed
Output:
    A list of count value for every neighborhood
'''
def GenerateCountNeighborhoodIndex(PricesData,Neighs_list):
    PricesData = np.array(PricesData)
    AllCounts = []
    for i,row in enumerate(PricesData):
        try:
            AllCounts.append([len(row),Neighs_list[i][0],Neighs_list[i][1]])
        except:
            AllCounts.append([np.nan,Neighs_list[i][0],Neighs_list[i][1]])
            pass        
    return AllCounts
'''
Description: Generate the neighborhood index using the Quartiles methodology
Input:
    PricesData: PricesData: The prices of transactions grouped by neighborhood in a 2D array
    (numpy -- [[price1,price2,...],[price1,price2,...],...])
    Neighs_list: The list of neighborhoods to be analyzed
Output:
    A list of quartiles value for every neighborhood
'''
def GenerateQuartilesNeighborhoodIndex(PricesData,Neighs_list):
    PricesData = np.array(PricesData)
    AllQs = []
    for i,row in enumerate(PricesData):
        if len(row)>9:
            try:
                sr = p.Series(np.array(row).astype(float))
                qlow2, median2, qhigh2 = sr.dropna().quantile([0.25, 0.50, 0.75])
                TheMed = (qlow2+median2+qhigh2)/3.0
                AllQs.append([TheMed,Neighs_list[i][0],Neighs_list[i][1]])
            except Exception as e:
                #print e.args
                AllQs.append([np.nan,Neighs_list[i][0],Neighs_list[i][1]])
                pass
        else:
            AllQs.append([np.nan,Neighs_list[i][0],Neighs_list[i][1]])
    return AllQs


# In[185]:

'''
Description: Generate the neighborhood index using the Quartiles methodology
**Written by Mohammed Alrished
Input:
    CityShapeFile: The shapefile of the city
Output:
    The adjacency of every neighborhood 
    # FArray = [Dist, Mun, [[Dist,Mun],[Dist,Mun],[Dist,Mun], ...., [Dist,Mun]]]
'''
from os import listdir
from shapely.geometry import Polygon
import pygeoj
def GenerateNeighborhoodsAdjacency(CityShapeFileLocation,CityShapeFile):#Khorshed worked on it
    directory = CityShapeFileLocation
    files = [ CityShapeFile ]
    
    for filename in files[:]:
        testfile = pygeoj.load(directory+filename)
        count = 0
        a = []
        aa = []
        pair = []
        for feature in testfile:
            a.append(feature.geometry.coordinates)
            aa.append(feature.properties['OBJECTID'])
            pair.append([feature.properties['District_N'],feature.properties['Municipali']])
            count = count + 1
        p = []
        output = []
        for i in aa:
            p0 = Polygon(a[i-1][0])
            p = a
            intpoly = []
            for j in range(len(p)):
                if p0.intersects(Polygon(p[j][0])) == True:
                    if aa[j] != i:
                        intpoly.append(aa[j]) 
            output.append([i,intpoly])

        FArray = [] 
        Adj = []   
        for ii in range(len(output)):
            Adj = []
            for k in range(len(output[ii][1])):
                Adj.append([pair[output[ii][1][k]-1][0],pair[output[ii][1][k]-1][1]])

            FArray.append([pair[ii][0],pair[ii][1],Adj])
            
        return FArray


# In[148]:

'''
Description: Perform spatial smoothing for the neighborhoods that doesn't have a value 
Input:
    NeighborhoodIndex: The curren neighborhood index (numpy -- val,neighborhood,Municipality)
    NeighborhoodsAdjacency: The Adjacent neighborhoods for every neighborhood 
    (numpy -- neighborhood,Municipality,[[neighborhood,Municipality],[],...])
Output:
    A new neighborhood index smoothed based on the adjacency matrix
'''
def SpatialSmoothing(NeighborhoodIndex,NeighborhoodsAdjacency):
    NeighborhoodIndex = np.array(NeighborhoodIndex)
    
    #Identify the neighborhoods that are not mapped
    New_NeighborhoodIndex = []
    c = 0
    for item in NeighborhoodIndex:
        if item[0] == None or np.isnan(float(item[0])):
            #print item[1],c
            c+=1
            #Find all the adjacent neighborhoods
            for neigh in NeighborhoodsAdjacency:
                if neigh[0] == item[1] and neigh[1] == item[2]:
                    Adjacents = neigh[2]
                    break
            
            #Get the average of adjacent neighborhoods
            Sum = 0
            Count = 0.0
            for Adjacent in Adjacents:
                select = np.logical_and(NeighborhoodIndex[:,1] == Adjacent[0],NeighborhoodIndex[:,2] == Adjacent[1])
                try:
                    neigh = NeighborhoodIndex[select][0]
                    if neigh[0] == None or np.isnan(float(neigh[0])) == False:
                        Sum+= float(neigh[0])
                        Count+= 1.0
                except:
                    pass
            #Add the new value only if there is ajacents with value

            if Count!=0:
                New_NeighborhoodIndex.append([Sum/Count,item[1],item[2]])
            else:
                New_NeighborhoodIndex.append(item)
        else:
            New_NeighborhoodIndex.append(item)
    return np.array(New_NeighborhoodIndex)


# In[166]:

'''
Description: Generate a plot of the ECDF that shows the differences between the neighborhoods 
Input:
    PricesData: PricesData: The prices of transactions grouped by neighborhood in a 2D array
    (numpy -- [[price1,price2,...],[price1,price2,...],...])
    FileLocation: The location of the plot to save
    FileName: The name of the plot to save
Output:
    Saved plot
'''
def PlotECDFOfCity(PricesData,FileLocation,FileName):
    PricesData = np.array(PricesData)
    #Generate the ECDFs
    numberOfDensityPoints = 20
    maxx = -1
    All_ECDFs = []
    maxx = 10000
    for row in PricesData:
        try:
            x = np.array(row).astype(float)
            x = x/float(maxx)
            ecdf = ECDF(x)
            x = np.linspace(0,1,numberOfDensityPoints)
            y1 = ecdf(x)
            temp = []
            for item in y1:
                temp.append(item)
            #temp.append((len(row)/float(maxx2)))
            All_ECDFs.append(temp)
        except:
            pass

    All_ECDFs = np.array(All_ECDFs)
    

    
    fig = plt.figure(figsize=(20,10))
    ax = fig.add_subplot(111)
    ax.plot(np.linspace(0,1.0,numberOfDensityPoints),'--',color = 'black')
    
    
    Varss = []
    maxx = -1
    # for row in PricesData:
    #     if len(row)>0:
    #         if np.max(row)>maxx:
    #             maxx = np.max(row)
    for row in All_ECDFs:
        TheVal1 = 1-np.sum(row)
        Varss.append(TheVal1)
    maxx = 10000
    minval = np.min(Varss)
    maxval = np.max(Varss)
    norm = mpl.colors.Normalize(minval, maxval)
    cmap = cm.plasma
    m = cm.ScalarMappable(norm=norm, cmap=cmap)
    
    for i,row in enumerate(All_ECDFs):
        y1 = row
        ax.plot(y1,'-',color = m.to_rgba(Varss[i]))
        
    ax.set_ylim([0,1])
    ax.set_xlim([0,20])
    XtickLabels = []
    #for item in range(numberOfDensityPoints):
        #XtickLabels.append(item * (maxx/numberOfDensityPoints)*4)
    #ax.set_xticklabels(XtickLabels)
    ax.xaxis.set_ticks(np.arange(0, 20, 1))
    ax.xaxis.set_ticklabels(np.arange(0, maxx, (maxx/numberOfDensityPoints)))

    ax.set_xlabel('PPSM',fontsize=20)
    ax.set_ylabel('ECDF',fontsize=20)

    plt.savefig(FileLocation+'/'+FileName+'.png',bbox_inches='tight',dpi=300)

