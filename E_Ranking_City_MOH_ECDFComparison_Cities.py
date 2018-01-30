
# coding: utf-8

# In[1]:

import csv
import time
import numpy as np
import sys
import pandas as p
from scipy.stats import gaussian_kde

from bidi.algorithm import get_display
import matplotlib.pyplot as plt
import arabic_reshaper
import math


# In[2]:


# In[4]:

reload(sys)
sys.setdefaultencoding("utf-8")


# In[23]:

'''
Description: Generate Distribution plots of cities
Input:
    TransactionsPrices: The ministry of justice transactions after all cleaning stages
    (numpy -- [[CityName,[price1,price2,...]],[City2Name,[price1,price2,...]],...])
Output:
    Generate plot of distribution and metrics to be used as city index
'''
def GenerateCityIndex(TransactionsPrices,FileLocation,FileName):
    #Crete the figure
    #fig = plt.figure(figsize=(20,10))
    ax = fig.add_subplot(111)
    
    CityIndex = [['City','Mode','Median','Mean']]
    LegendArr = []
    for city in TransactionsPrices:
        data = np.array([np.log(item) for item in np.array(city[1])])
        temp = []
        for item in data:
            if item!=np.nan and item!=np.inf and item!=np.nan*-1 and item!=np.inf*-1:
                temp.append(item)
        data = np.array(temp)
        # this create the kernel, given an array it will estimate the probability over that values
        kde = gaussian_kde( list(data) )
        # these are the values over wich your kernel will be evaluated
        dist_space = np.linspace( min(data), max(data), len(data) )
        # plot the results
        ax.plot( dist_space, kde(dist_space),alpha=0.8)
        CityMode = dist_space[np.argmax(kde(dist_space))]
        CityMedian = np.median(data)#dist_space[np.argmax(kde(dist_space))]
        CityMean = np.mean(data)
        
        CityIndex.append([city[0],math.pow(np.e,float(CityMode)),math.pow(np.e,float(CityMedian)),math.pow(np.e,float(CityMean))])
        
        LegendArr.append(city[0])
        #print 'finished city index for '+city[0]
    ax.set_ylabel('$Kernel\ Density\ Estimation$',fontsize=20)
    ax.set_xlabel('$log(PPSM)$',fontsize=20)
    t = ''
    for ind in CityIndex[1:]:
        t+=ind[0]+' Mode: '+str(ind[1])+'\n'
    ax.text(10,0.3,t)
    #ax.grid()
    ax.set_xlim([4,12])
    ax.legend(LegendArr,fontsize=20)
    
    plt.savefig(FileLocation+'/'+FileName+'.png',bbox_inches='tight',dpi=300)
    
    return CityIndex


# In[ ]:

#ax.text(4.5,0.6,'Riyadh mode: '+str(math.pow(np.exp(1),RiyadhMode))[:9]+
#        '\nJeddah mode: '+str(math.pow(np.exp(1),JeddahMode))[:9]+
#        '\nDammam mode: '+str(math.pow(np.exp(1),DammamMode))[:9]+
#        '\nMakkah mode: '+str(math.pow(np.exp(1),MakkahMode))[:9],
#        fontsize=20,bbox={'facecolor':'red', 'alpha':0.5, 'pad':10},color='white')


# In[ ]:



