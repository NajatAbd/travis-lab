
# coding: utf-8

# In[50]:

import csv
import time
import numpy as np
import sys
import pandas as p
from scipy.stats import gaussian_kde
from bidi.algorithm import get_display
import matplotlib.pyplot as plt
import arabic_reshaper
import random
import math
from tqdm import tqdm


# In[3]:

reload(sys)
sys.setdefaultencoding("utf-8")


# In[ ]:

#def CreateLabeledData():#Zeyad code of labeled datapoints


# In[34]:

'''
Description: Defines the percentage of values accepted in each bin for a single neighborhood
Input:
    villas: Aqar villas data for a single neighborhood
    lands: Aqar lands data for a single neighborhood
    moj: MOJ data for a single neighborhood
Output:
    The percentage of values accepted in each bin, the bins
'''
def IdentifyRangesToKeep(villas,lands,moj):
    bins = np.linspace(4.0,11.0,100)

    Villas_Hist,temp = np.histogram(villas[:,2].astype(float),bins=bins)
    Lands_Hist,temp = np.histogram(lands[:,2].astype(float),bins=bins)
    MOJ_Hist,temp = np.histogram(moj[:,10].astype(float),bins=bins)
    
    #Define the percentage of each bin to be kept from the MOJ data
    boole = False
    temp_range_ToKeep = []
    for i,item in enumerate(Villas_Hist):
        if item!=0:
            boole = True
        if float(Villas_Hist[i])==0 and boole==False:
            temp_range_ToKeep.append([i,1.0])
        elif float(Villas_Hist[i])==0 and float(Lands_Hist[i])==0:
            temp_range_ToKeep.append([i,0.0])
        elif float(Villas_Hist[i])!=0 and float(Lands_Hist[i])==0:
            temp_range_ToKeep.append([i,0.0])
        elif float(Villas_Hist[i])==0 and float(Lands_Hist[i])!=0:
            #temp_range_ToKeep.append([i,Lands_Hist[i]/float(Villas_Hist[i])])
            temp_range_ToKeep.append([i,1.0])
        elif float(Villas_Hist[i])==float(Lands_Hist[i]):
            #temp_range_ToKeep.append([i,Lands_Hist[i]/float(Villas_Hist[i])])
            temp_range_ToKeep.append([i,0.5])
        else:
            temp_range_ToKeep.append([i,Lands_Hist[i]/(float(Lands_Hist[i]) + float(Villas_Hist[i]))])


    tempr = []
    for item in temp_range_ToKeep:
        if item[1]>1.0:
            tempr.append([item[0],1.0])
        else:
            tempr.append(item)
    temp_range_ToKeep = tempr
        
    return temp_range_ToKeep,bins


# In[51]:

'''
Description: After defining the percentage of values accepted in each bin, identify whcih transactions to be accepted
Input:
    temp_MOJ: MOJ data for a single neighborhood
    temp_range_ToKeep: Percentage to be accepted from MOJ data in each bin
    bins: The size of the bins and their values
Output:
    New list of transaction for the given neighborhood
'''
def GetTransactionsAcceptedbyRanges(temp_MOJ,temp_range_ToKeep,bins):
    TheNewMOJ = []
    for j,item in enumerate(bins):
        if j==(len(bins)-1):
            ToKeep = temp_range_ToKeep[j-1][1]
            select = temp_MOJ[:,10]>=item
            SelectedMOJ = temp_MOJ[select]
            if len(SelectedMOJ)>0.0:
                if ToKeep>0.0:
                    if ToKeep==1.0:
                        for row in SelectedMOJ:
                            temprr = []
                            for ele in row:
                                temprr.append(ele)
                            temprr.append(0)
                            TheNewMOJ.append(temprr)
                    else:
                        TheNumberOfEles = int(np.ceil(len(SelectedMOJ) * ToKeep))
                        if TheNumberOfEles==0.0 and len(SelectedMOJ)>0.0 and ToKeep>0.0:
                            TheNumberOfEles = 1.0
                        idxes = random.sample(range(len(SelectedMOJ)), TheNumberOfEles)
                        for row in SelectedMOJ[idxes,:]:
                            temprr = []
                            for ele in row:
                                temprr.append(ele)
                            temprr.append(0)
                            TheNewMOJ.append(temprr)
        else:
            ToKeep = temp_range_ToKeep[j][1]
            select = np.logical_and(temp_MOJ[:,10]>=item,temp_MOJ[:,10]<bins[j+1])
            SelectedMOJ = temp_MOJ[select]
            if len(SelectedMOJ)>0.0:
                if ToKeep>0.0:
                    if ToKeep==1.0:
                        for row in SelectedMOJ:
                            temprr = []
                            for ele in row:
                                temprr.append(ele)
                            temprr.append(0)
                            TheNewMOJ.append(temprr)
                    else:
                        TheNumberOfEles = int(np.ceil(len(SelectedMOJ) * ToKeep))
                        if TheNumberOfEles==0.0 and len(SelectedMOJ)>0.0 and ToKeep>0.0:
                            TheNumberOfEles = 1.0
                        idxes = random.sample(range(len(SelectedMOJ)), TheNumberOfEles)
                        for row in SelectedMOJ[idxes,:]:
                            temprr = []
                            for ele in row:
                                temprr.append(ele)
                            temprr.append(0)
                            TheNewMOJ.append(temprr)
    return TheNewMOJ


# In[59]:

#The data must be cleaned before this step (Names should be the same across all the three datasets)
'''
Description: The purpose of the function is to remove the transactions that are more likely to be villas and keep 
            only the transactions that are lands
Input:
    Aqar_Villas: Villas listings from Aqar website
    Aqar_Lands: Lands listings from Aqar website
    MOJ_Data: The ministry of justice transactions
    LabeledTransactions: MOJ transactions labeled based on the GMM model (villa or land)
Output:
    New list of MOJ data
'''
def ApplyTransactionsRejections(Aqar_Villas,Aqar_Land,MOJ_Data,LabeledTransactions):
    

    #Final MOJ
    MOJ_Cleaned = []
    #Get All the neighborhoods in the transactions
    MOJ_Data = np.array(MOJ_Data)
    Aqar_Villas = np.array(Aqar_Villas)
    Aqar_Land = np.array(Aqar_Land)

    LabeledTransactions = np.array(LabeledTransactions)

    Neigs_dups = MOJ_Data[:,[13,14]]
    Neighs = np.vstack({tuple(e) for e in Neigs_dups})
    
    
    for neigh in tqdm(Neighs):
        #Find the neighborhood land transactions in Aqar
        if len(Aqar_Land) > 0:
            select = np.logical_and(Aqar_Land[:,6]==neigh[0],Aqar_Land[:,7]==neigh[1])
            temp_lands = Aqar_Land[select]
            if len(temp_lands)>0:
                temp_lands[:,1] = np.log(temp_lands[:,1].astype(float))
                temp_lands[:,2] = np.log(temp_lands[:,2].astype(float))
                #Make sure there are no nan and inf values in the list
                tempr = []
                for item in temp_lands:
                    if item[2]!=-1*np.inf and item[2]!=np.inf and item[2]!=-1*np.nan and str(item[2])!='nan':
                        tempr.append(item)
                temp_lands = np.array(tempr)
        else:
            temp_lands = []
        #Find the neighborhood villas transactions in Aqar
        if len(Aqar_Villas) > 0:
            select = np.logical_and(Aqar_Villas[:,6]==neigh[0],Aqar_Villas[:,7]==neigh[1])
            temp_villas = Aqar_Villas[select]
            if len(temp_villas)>0:
                temp_villas[:,1] = np.log(temp_villas[:,1].astype(float))
                temp_villas[:,2] = np.log(temp_villas[:,2].astype(float))
                #Make sure there are no nan and inf values in the list
                tempr = []
                for item in temp_villas:
                    if item[2]!=-1*np.inf and item[2]!=np.inf and item[2]!=-1*np.nan and str(item[2])!='nan':
                        tempr.append(item)
                temp_villas = np.array(tempr)
        else:
            temp_villas = []
        
        #Find the neighborhood transactions in MOJ
        select = np.logical_and(MOJ_Data[:,13]==neigh[0],MOJ_Data[:,14]==neigh[1])
        temp_MOJ = MOJ_Data[select]
        if len(temp_MOJ)>0:
            temp_MOJ[:,9] = np.log(temp_MOJ[:,9].astype(float))
            temp_MOJ[:,10] = np.log(temp_MOJ[:,10].astype(float))
            #Make sure there are no nan and inf values in the list
            tempr = []
            for item in temp_MOJ:
                if item[10]!=-1*np.inf and item[10]!=np.inf and item[10]!=-1*np.nan and str(item[10])!='nan':
                    tempr.append(item)
            temp_MOJ = np.array(tempr)
        
        # Bools = True
        # List = np.array(p.read_csv('Data/Temp_Neighs.csv',header=None))
        # for item in List:
        #     if item == neigh[0]:
        #         Bools = False

        if (len(temp_MOJ)>=3 and len(temp_villas)>=3 and len(temp_lands)>=3):
            #return temp_villas,temp_lands,temp_MOJ
            TheRangeToKeep,bins = IdentifyRangesToKeep(temp_villas,temp_lands,temp_MOJ)

            NewMOJ_forNeigh = GetTransactionsAcceptedbyRanges(temp_MOJ,TheRangeToKeep,bins)
            for item in NewMOJ_forNeigh:
                MOJ_Cleaned.append(item)
        elif (len(temp_villas)==0 and len(temp_lands)==0):
            for item in temp_MOJ:
                MOJ_Cleaned.append(item)
        else:
            #print LabeledTransactions
            #perform Zeyad's SVM function
            if len(LabeledTransactions)>0:
                TIDs = list(LabeledTransactions[LabeledTransactions[:,15].astype(float) == 0.0][:,7].astype(float))
                for item in temp_MOJ:
                    if float(item[7]) in TIDs:
                        MOJ_Cleaned.append(item)
    
    Temp = []
    for trans in MOJ_Cleaned:
        tempr = []
        try:
            for i,ele in enumerate(trans):
                if i == 9 or i == 10:
                    tempr.append(math.pow(np.e,float(ele)))
                    #if i == 10:
                        #print tempr[10]
                elif i <= 14:
                    tempr.append(ele)
            Temp.append(tempr)
        except Exception as e:
            print e.args
            pass
    MOJ_Cleaned = np.array(Temp)
    return MOJ_Cleaned


# In[ ]:

'''
Description: Generate the density plots of Aqar data (lands and villas) and MOJ data (new and old)
Input:
    Aqar_Villas: Villas listings from Aqar website
    Aqar_Lands: Lands listings from Aqar website
    MOJ_Data: The ministry of justice transactions before removing villas
    NewMOJ_Data: The ministry of justice transactions after removing villas
    Neighs_list: The list of neighborhoods to be plotted
Output:
    Generate a density plot for every neighborhood
'''
def PlotDensity(Aqar_Villas,Aqar_Land,MOJ_Data,NewMOJ_Data,Neighs_list,PlotsLocation):
    
    for neigh in Neighs_list:
        fig = plt.figure(figsize=(15,6))
        ax = fig.add_subplot(111)
        #Get the transactions of a single neighborhood
        select = np.logical_and(Aqar_Land[:,6]==neigh[0],Aqar_Land[:,7]==neigh[1])
        temp_lands = Aqar_Land[select]
        
        select = np.logical_and(Aqar_Villas[:,6]==neigh[0],Aqar_Villas[:,7]==neigh[1])
        temp_Villas = Aqar_Villas[select]
        
        select = np.logical_and(MOJ_Data[:,13]==neigh[0],MOJ_Data[:,14]==neigh[1])
        temp_MOJ = MOJ_Data[select]
        
        select = np.logical_and(NewMOJ_Data[:,13]==neigh[0],NewMOJ_Data[:,14]==neigh[1])
        temp_NewMOJ = NewMOJ_Data[select]
        
        #Get the prices and areas of the transactions
        MOJ_Prices = temp_MOJ[:,[9,10]]
        NewMOJ_Prices = temp_NewMOJ[:,[9,10]]
        Land_Prices = temp_lands[:,[1,2]]
        Villas_Prices = temp_Villas[:,[1,2]]
        LegendArr = []
        
        try:
            data = MOJ_Prices[:,1]
            # this create the kernel, given an array it will estimate the probability over that values
            kde = gaussian_kde( list(data) )
            # these are the values over wich your kernel will be evaluated
            dist_space = linspace( min(data), max(data), len(data) )
            # plot the results
            ax.plot( dist_space, kde(dist_space) , color = 'b',alpha=0.5)
            LegendArr.append('Old_MOJ')
        except:
            pass
        
        try:
            data = NewMOJ_Prices[:,1].astype(float)
            # this create the kernel, given an array it will estimate the probability over that values
            kde = gaussian_kde( list(data) )
            # these are the values over wich your kernel will be evaluated
            dist_space = linspace( min(data), max(data), len(data) )
            # plot the results
            ax.plot( dist_space, kde(dist_space) , color = 'black',alpha=0.5)
            LegendArr.append('New_MOJ')
        except Exception as e:
            #print e.args
            pass
        
        try:
            data = Land_Prices[:,1]
            # this create the kernel, given an array it will estimate the probability over that values
            kde = gaussian_kde( list(data) )
            # these are the values over wich your kernel will be evaluated
            dist_space = linspace( min(data), max(data), len(data) )
            # plot the results
            ax.plot( dist_space, kde(dist_space) , color = 'r',alpha=0.5)
            LegendArr.append('Aqar_Land')
        except:
            pass
        
        try:
            data = Villas_Prices[:,1]
            # this create the kernel, given an array it will estimate the probability over that values
            kde = gaussian_kde( list(data) )
            # these are the values over wich your kernel will be evaluated
            dist_space = linspace( min(data), max(data), len(data) )
            # plot the results
            ax.plot( dist_space, kde(dist_space) , color = 'g',alpha=0.5)
            LegendArr.append('Aqar_Villas')
        except:
            pass
        
        reshaped_text = arabic_reshaper.reshape(unicode(neigh[1]))
        artext = get_display(reshaped_text)
        ax.set_title(unicode(artext),fontsize=20)
        
        ax.set_xlabel('$log(PPSM)$',fontsize=20)
        ax.set_ylabel('$Kernel\ Density\ Estimation$',fontsize=20)
        ax.legend(LegendArr) 
        plt.savefig(PlotsLocation+'/'+neigh[1]+'.png',bbox_inches='tight')

