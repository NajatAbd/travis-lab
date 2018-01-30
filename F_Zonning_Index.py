
# coding: utf-8

# In[1]:

import pandas as p
import numpy as np
import matplotlib.pyplot as plt
from bidi.algorithm import get_display
import arabic_reshaper

# In[2]:

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

AllColors = [
        '#F19E25',#orange
        '#3D58EC',#purple
        '#14A216',#green 
        '#e7163c',#red
        '#808080',#Gray
        '#000000',#Black
        '#04F7EC',#Cayan
        '#EC04F7',#Pink
        '#FFF704',#Yellow
    ]
# ListOfColors = {
#         0:'#F19E25',#orange
#         1:'#3D58EC',#purple
#         3:'#14A216',#green 
#         2:'#e7163c',#red
#         4:'#808080',#Gray
#         5:'#000000',#Black
#         6:'#04F7EC',#Cayan
#         7:'#EC04F7',#Pink
#         8:'#FFF704',#Yellow
#         -1:'#FFFFFF'
#     }
# In[10]:

'''
Description: Generate the clusters of the neighborhoods based on the value of the neighborhood index
Input:
    NeighborhoodIndex: The neighborhood index of a city
    NumberOfClusters: The number of groups to have in the data
Output:
    GMM Classifier
'''
from sklearn import mixture
def ClusterNeighborhoods(NeighborhoodIndex,NumberOfClusters = 4):
    # fit a Gaussian Mixture Model with n components
    n_components=NumberOfClusters
    clf = mixture.GMM(n_components)
    #the feature is the average price of a neighborhood
    x = [ [i] for i in NeighborhoodIndex[:,0].astype(float)];
    return clf.fit(x)


# In[11]:
def CreateColorsDict(clf):
    #Create the colors based on the values of the clusters
    ListOfColors = {}
    clusMeans = []
    for i,item in enumerate(clf.means_):
        clusMeans.append([i,item])
    clusMeans = np.array(clusMeans)
    clusMeans = clusMeans[np.argsort(clusMeans[:,1])]

    for i,item in enumerate(clusMeans):
        ListOfColors[item[0]] = AllColors[i]
    ListOfColors[-1] = '#FFFFFF'
    return ListOfColors
'''
Description: Generate the clusters of the neighborhoods based on the value of the neighborhood index
Input:
    NeighborhoodIndex: The neighborhood index of a city
    clf: The classifier
Output:
    Classified neighborhoods
'''
#from sklearn import mixture
def ClassifyNeighborhoods(NeighborhoodIndex,clf):
    ListOfColors = CreateColorsDict(clf)
    # fit a Gaussian Mixture Model with n components
    #the feature is the average price of a neighborhood
    x = []
    for item in NeighborhoodIndex:
        Prediction = clf.predict(float(item[0]))[0]
        Color = ListOfColors[Prediction]
        x.append([item[1],item[2],Prediction,Color])
    return x

# In[ ]:

'''
Description: Generate the density plot of the clusters
Input:
    NeighborhoodIndex: The neighborhood index of a city
    clf: The GMM classifier
    NumberOfClusters: The number of groups to have in the data
Output:
    List of neighborhood names and the cluster number
'''
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from sklearn import mixture
import matplotlib.mlab as mlab
import math
from scipy.stats import gaussian_kde
def GenerateZoningIndexDensityPlot(NeighborhoodIndex,clf,FileLocation,FileName,NumberOfClusters = 4):
    
    #plt.figure(figsize=(20,10))
    
    colors=['g','m','b','k','r']
    
    #Create the colors based on the values of the clusters
    ListOfColors = CreateColorsDict(clf)

    n_components = NumberOfClusters
    l=np.linspace(0,max(NeighborhoodIndex[:,0].astype(float))+1000,100);

    # #Plot the density of each cluster
    # Prediction = []
    # for item in NeighborhoodIndex:
    #     Prediction.append([float(item[0]),clf.predict(float(item[0]))])
    # Prediction = np.array(Prediction)
    # for clus in range(0,n_components):
    #     temp = Prediction[Prediction[:,1] == clus][:,0]
    #     data = temp
    #     # this create the kernel, given an array it will estimate the probability over that values
    #     kde = gaussian_kde( list(data) )
    #     # these are the values over wich your kernel will be evaluated
    #     dist_space = np.linspace( min(data), max(data), len(data) )
    #     # plot the results
    #     plt.plot( dist_space, kde(dist_space),alpha=0.8,color = ListOfColors[clus])


    for i in range(0,n_components):
        #plt.plot(l,mlab.normpdf(l, clf.means_[i], math.sqrt(clf.covars_[i][0])),linewidth=2.0,color=ListOfColors[i])

    #patching the histogram with colors  
    #n, bins, patches = plt.hist(NeighborhoodIndex[:,0].astype(float),60,normed=1,color='k')

    #bin_centers = 0.5 * (bins[:-1] + bins[1:])

    # scale values to interval [0,1]
    
     #col = bin_centers - min(bin_centers)
    #col /= max(col)

    #for c,p,b_c in zip(col, patches,bin_centers):
        #plt.setp(p, 'facecolor', ListOfColors[clf.predict([[b_c]])[0]])

    

    #plt.axis('tight')
    #plt.xlabel('neighborhood average ppm',fontsize=20)
    #plt.ylabel('p(neighborhood average ppm)',fontsize=20)
    #plt.xticks(fontsize=20)
    #plt.yticks(fontsize=20)


    print 'the average price of each cluster: \n'
    for i in range(0,n_components):
        print 'cluster {0} has mean {1}'.format(i,clf.means_[i])
        
    #plt.savefig(FileLocation+'/'+FileName+'.png',bbox_inches='tight',dpi=300)


# In[ ]:

'''
Description: Generate the density plot of the clusters
Input:
    NeighborhoodIndex: The neighborhood index of a city
    clf: The GMM classifier
    NumberOfClusters: The number of groups to have in the data
Output:
    List of neighborhood names and the cluster number
'''
from fiona import collection
from shapely.geometry import mapping, shape
from shapely.geometry.polygon import LinearRing, Polygon
from descartes import PolygonPatch
import matplotlib.patches as mpatches
def GenerateZoningIndexMapPlot(NeighborhoodIndex,clf,ShapeFileLocation,FileLocation,FileName,NumberOfClusters = 4):
    
    #fig,ax =plt.subplots(1,figsize=(14,20))
    #fig,ax =plt.subplots(1)

    #Create the colors based on the values of the clusters
    ListOfColors = CreateColorsDict(clf)

    #Identify the clusters values
    Clusters_Values = []
    for c in range(NumberOfClusters):
        Clusters_Values.append([c,[]])
    #assign cluster to each nighborhood
    assignments= []
    temp = []
    for i in range(0,len(NeighborhoodIndex)):
        Prediction = clf.predict([[float(NeighborhoodIndex[i,0])]])[0]
        arr = Clusters_Values[Prediction][1]
        arr.append(float(NeighborhoodIndex[i,0]))
        Clusters_Values[Prediction][1] = arr
        assignments.append([NeighborhoodIndex[i,1],NeighborhoodIndex[i,2],Prediction])
    assignments = np.array(assignments)
    
    with collection(ShapeFileLocation, "r",encoding='utf8') as input:
        # schema = input.schema.copy()
        schema = { 'geometry': 'Polygon', 'properties': { 'NEIGHBORH1': 'str' } }
        for point in input:
            try:
                select = np.logical_and(NeighborhoodIndex[:,1]==point['properties'][u'District_N'],
                                       NeighborhoodIndex[:,2]==point['properties'][u'Municipali'])
                a = int(assignments[select][0][2])
            except Exception as e:
                a = -1;
            poly = Polygon(np.array(point['geometry']['coordinates'][0]))
            x,y = poly.exterior.xy
            ring_patch = PolygonPatch(poly,fc=ListOfColors[a], ec=ListOfColors[a], alpha=0.9, zorder=2)
            #ax.add_patch(ring_patch)
            #ax.plot(x, y, color='#000000', alpha=0.85,linewidth=1, solid_capstyle='butt', zorder=2)

            x,y = poly.centroid.wkt.replace(')','').replace('(','').replace('POINT ','').split(' ')
            rx = float(x)
            ry = float(y)
            cx = rx# + ring_patch.get_width()/2.0
            cy = ry# + ring_patch.get_height()/2.0
            reshaped_text = arabic_reshaper.reshape(point['properties'][u'District_N'])
            artext = get_display(reshaped_text)
            #ax.annotate(artext, (cx, cy), color='black', weight='bold',fontsize=4, ha='center', va='center')


        
        #Get the min and max values of the method
        Clus_Summary = []
        for clus in Clusters_Values:
            Clus_Summary.append([clus[0],int(np.min(clus[1])),int(np.max(clus[1]))])
        Clus_Summary = np.array(Clus_Summary)
        Clus_Summary = Clus_Summary[np.argsort(Clus_Summary[:,1])]
        handlers = []
        for clus in Clus_Summary:
            Thelabel = str(clus[1])+ ' - '+str(clus[2])+' SAR'
            patch = mpatches.Patch(color=ListOfColors[clus[0]], label=Thelabel,linewidth=10);#orange
            handlers.append(patch)
        
        #plt.legend(handles=handlers,prop={'size':20})
        #plt.xticks([])
        #plt.yticks([])
        #plt.savefig(FileLocation+'/'+FileName+'.png',bbox_inches='tight',dpi=300)

