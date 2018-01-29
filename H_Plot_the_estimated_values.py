
# coding: utf-8

# In[1]:

import csv
import time
import numpy as np
from scipy.stats.stats import pearsonr
from scipy.stats.stats import spearmanr
from scipy.stats.stats import kendalltau
import sys
import pandas as p
from bidi.algorithm import get_display
import matplotlib.pyplot as plt
import arabic_reshaper
import math


# In[10]:

import matplotlib as mpl
import matplotlib.cm as cm
from matplotlib import gridspec


# In[2]:


# In[3]:

reload(sys)
sys.setdefaultencoding("utf-8")


# In[4]:

'''
Description: produce a bar chart plot of the neighborhood index 
Input:
    NeighborhoodIndex: The curren neighborhood index (numpy -- val,neighborhood,Municipality)
Output:
    Barchart
'''
def GenerateNeighborhoodIndexBarChart(NeighborhoodIndex,FileLocation,FileName):
    fig = plt.figure(figsize=(10,20))
    ax = fig.add_subplot(111)
    Sorted = np.argsort(NeighborhoodIndex[:,0].astype(float)*1)
    #Draw the colored bars
    tempr = NeighborhoodIndex[Sorted][:,0].astype(float)
    count = 0
    barlist = ax.barh(range(len(tempr[tempr<1000])),tempr[tempr<1000],color='g',alpha=0.7,align='center')
    count+=len(tempr[tempr<1000])
    select = np.logical_and(tempr<2000,tempr>=1000)
    barlist = ax.barh(range(len(tempr[tempr<1000]),len(tempr[tempr<2000])),tempr[select],color='gray',alpha=0.7,align='center')
    count+=len(tempr[select])
    select = np.logical_and(tempr<3000,tempr>=2000)
    barlist = ax.barh(range(len(tempr[tempr<2000]),len(tempr[tempr<3000])),tempr[select],color='r',alpha=0.7,align='center')
    count+=len(tempr[select])
    select = np.logical_and(tempr<100000,tempr>=3000)
    barlist = ax.barh(range(len(tempr[tempr<3000]),len(tempr[tempr<100000])),tempr[select],color='steelblue',align='center')
    count+=len(tempr[select])
    
    #Add the neighborhoods names
    Neigh_names_new = []
    for item in NeighborhoodIndex[Sorted][:,1]:
        reshaped_text = arabic_reshaper.reshape(unicode(item))
        artext = get_display(reshaped_text)
        Neigh_names_new.append(artext)
    ax.yaxis.set_ticks(np.arange(0, len(Neigh_names_new), 1))
    ax.set_yticklabels(Neigh_names_new,fontsize=8)
    
    #Edit the chart details
    ax.legend(['0 - 1000','1000 - 2000','2000 - 3000','>3000'],fontsize=20,loc=7)
    #ax.grid()
    ax.xaxis.grid(True, which='major')
    ax.set_ylim([0,len(NeighborhoodIndex[:,0])])
    ax.set_xlim([0,9000])
    ax.set_xlabel('Estimated Value',fontsize=20)
    ax.set_ylabel('Neighborhoods',fontsize=20)


    plt.savefig(FileLocation+'/'+FileName+'.png',bbox_inches='tight',dpi=300)


# In[5]:

def show_colormap(cmap,minval,maxval,fig):
    im = np.outer(np.ones(10), np.arange(maxval))
    fig = plt.figure(figsize=(10, 2))
    ax2 = fig.add_subplot(212)
    ax2.imshow(im, cmap=cmap)
    ax2.set_xticks([minval,maxval])
    ax2.set_yticks([])


# In[87]:

'''
Description: produce a map plot of the neighborhood index 
Input:
    NeighborhoodIndex: The curren neighborhood index (numpy -- val,neighborhood,Municipality)
Output:
    Colored map
'''
from fiona import collection
from shapely.geometry import mapping, shape
from shapely.geometry.polygon import LinearRing, Polygon
from descartes import PolygonPatch
import matplotlib.patches as mpatches
def GenerateNeighborhoodIndexMap(NeighborhoodIndex,ShapeFileLocation,FileLocation,FileName):
    
    fig,ax =plt.subplots(1,figsize=(14,20))
    
    
    minval = np.min(NeighborhoodIndex[:,0].astype(float))
    maxval = np.max(NeighborhoodIndex[:,0].astype(float))
    norm = mpl.colors.Normalize(minval, maxval)
    #print minval,maxval
    cmap = cm.RdPu
    m = cm.ScalarMappable(norm=norm, cmap=cmap)
    temp = []
    ax.set_title('Estimated Value',fontsize=20)
    with collection(ShapeFileLocation, "r",encoding='utf8') as input:
        # schema = input.schema.copy()
        schema = { 'geometry': 'Polygon', 'properties': { 'NEIGHBORH1': 'str' } }
        for point in input:
            BoolPass = True
            ShapeFileDistrict = point['properties']['District_N']
            ShapeFileMunicipality = point['properties']['Municipali']
            
            temp.append([ShapeFileDistrict,ShapeFileMunicipality])
            
            try:
                select = np.logical_and(NeighborhoodIndex[:,1]==ShapeFileDistrict,NeighborhoodIndex[:,2]==ShapeFileMunicipality)
                EstVal = float(NeighborhoodIndex[select][0][0])
                BoolPass = True
            except Exception as e:
                BoolPass = False
                pass
            
            if BoolPass:
                poly = Polygon(np.array(point['geometry']['coordinates'][0]))
                x,y = poly.exterior.xy
                ring_patch = PolygonPatch(poly,fc=m.to_rgba(EstVal), ec=m.to_rgba(EstVal), alpha=0.9, zorder=2)
                ax.add_patch(ring_patch)
                ax.plot(x, y, color='#000000', alpha=0.85,linewidth=1, solid_capstyle='butt', zorder=2)
                
                x,y = poly.centroid.wkt.replace(')','').replace('(','').replace('POINT ','').split(' ')
                rx = float(x)
                ry = float(y)
                cx = rx# + ring_patch.get_width()/2.0
                cy = ry# + ring_patch.get_height()/2.0
                reshaped_text = arabic_reshaper.reshape(point['properties'][u'District_N'])
                artext = get_display(reshaped_text)
                ax.annotate(artext, (cx, cy), color='black', weight='bold',fontsize=4, ha='center', va='center')
            else:
                poly = Polygon(np.array(point['geometry']['coordinates'][0]))
                x,y = poly.exterior.xy
                ring_patch = PolygonPatch(poly,fc='#FFFFFF', ec='#FFFFFF', alpha=0.9, zorder=2)
                ax.add_patch(ring_patch)
                ax.plot(x, y, color='#000000', alpha=0.85,linewidth=1, solid_capstyle='butt', zorder=2)
                
                #Add the neighborhood name
                x,y = poly.centroid.wkt.replace(')','').replace('(','').replace('POINT ','').split(' ')
                rx = float(x)
                ry = float(y)
                cx = rx# + ring_patch.get_width()/2.0
                cy = ry# + ring_patch.get_height()/2.0
                reshaped_text = arabic_reshaper.reshape(point['properties'][u'District_N'])
                artext = get_display(reshaped_text)
                ax.annotate(artext, (cx, cy), color='black', weight='bold',fontsize=4, ha='center', va='center')
        
        #Get the min and max values of the method
        plt.xticks([])
        plt.yticks([])
        plt.savefig(FileLocation+'/'+FileName+'.png',bbox_inches='tight',dpi=300)
from scipy.stats import gaussian_kde
def CreateDistributionPlot(ToPlot,CompanyName,FileLocation,FileName,bins):
    fig = plt.figure(figsize=(7,7))
    ax = fig.add_subplot(111)

    data = np.array(ToPlot)
    # this create the kernel, given an array it will estimate the probability over that values
    #kde = gaussian_kde( list(data) )
    # these are the values over wich your kernel will be evaluated
    dist_space = bins
    # plot the results
    #ax.plot( dist_space, kde(dist_space),alpha=0.8)
    ax.hist(data,bins=dist_space)
    ax.set_title('Error distribution with '+CompanyName)

    plt.savefig(FileLocation+'/'+FileName+'_ErrorDist.png',bbox_inches='tight',dpi=300)


def GenerateCorrelationPlot(NeighborhoodIndex,CompanyEstimations,CompanyName,FileLocation,FileName):

    RankCorr = []

    for Neigh in NeighborhoodIndex:
        for Neigh2 in CompanyEstimations:
            if Neigh[1] == Neigh2[1] and Neigh[2] == Neigh2[2]:
                RankCorr.append([Neigh[0],Neigh2[0],Neigh[1],Neigh[2]])
                break
    RankCorr = np.array(RankCorr)

    Errors = np.abs(RankCorr[:,0].astype(float) - RankCorr[:,1].astype(float))
    Error = np.mean(Errors)

    PercentageDiff = []
    for item in RankCorr[:,[0,1]].astype(float):
        PercentageDiff.append(np.abs((item[0] - item[1])/item[1]))

    #compute Rsquared
    dividend = np.sum(np.power(RankCorr[:,1].astype(float) - RankCorr[:,0].astype(float),2))
    divisor = np.sum(np.power(RankCorr[:,1].astype(float) - np.mean(RankCorr[:,1].astype(float)),2))
    Rsquared = 1 - (dividend/divisor)

    #print PercentageDiff
    CreateDistributionPlot(Errors,CompanyName,FileLocation,FileName,np.linspace( 0, 50000, 50 ))
    CreateDistributionPlot(PercentageDiff,CompanyName,FileLocation,FileName+'_PercentageDiff',np.linspace( 0, 1, 20 ))

    r,pvalue = spearmanr(RankCorr[:,0].astype(float),RankCorr[:,1].astype(float))

    fig = plt.figure(figsize=(7,7))
    ax = fig.add_subplot(111)
    ax.scatter(RankCorr[:,0].astype(float),RankCorr[:,1].astype(float))
    ax.set_xlabel('ECDF estimation',fontsize=20)
    ax.set_ylabel(CompanyName,fontsize=20)



    
    for i, txt in enumerate(RankCorr[:,2]):
    	reshaped_text = arabic_reshaper.reshape(unicode(txt))
    	artext = get_display(reshaped_text)
    	ax.annotate(artext, (RankCorr[i,0],RankCorr[i,1]),fontsize = 6)

    MaxECDF = np.max(RankCorr[:,0].astype(float))
    MaxOther = np.max(RankCorr[:,1].astype(float))
    
    if MaxECDF>MaxOther:
        ax.set_xlim([0,MaxECDF])
        ax.set_ylim([0,MaxECDF])
        ax.plot(range(int(MaxECDF)),range(int(MaxECDF)),'--',color='black')
    else:
        ax.set_xlim([0,MaxOther])
        ax.set_ylim([0,MaxOther])
        ax.plot(range(int(MaxOther)),range(int(MaxOther)),'--',color='black')


    ax.set_title(str((r,pvalue))+'\n'+'MAE:'+str(Error)+'\n R_squared'+str(Rsquared))

    

    plt.savefig(FileLocation+'/'+FileName+'.png',bbox_inches='tight',dpi=300)

    return r,pvalue
