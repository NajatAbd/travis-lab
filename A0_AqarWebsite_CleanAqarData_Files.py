
# coding: utf-8

# In[79]:

import csv
import time
import numpy as np
import sys
import pandas as p
import json
from shapely.geometry import shape, Point
from tqdm import tqdm


# In[117]:

'''
Description: Identify the name of neighborhood and municipality a lat,lot belongs to
Input:
    lat: latitude
    lon: longitude
    PolygonsDict: Dictionary of polygons
Output:
    Neighborhood name,Municipality of the location given
'''
def IdentifyNeighborhoodName2(lat,lon,PolygonsDict):#Identify the neighborhood,Municipality where the listing belongs to
    point = Point(lon, lat)
    # check each polygon to see if it contains the point
    for key in PolygonsDict.keys():
        polygon = PolygonsDict[key]
        #Create the bounding box
        Maxlat = polygon[0][0]
        MinLat = polygon[0][1]
        Maxlon = polygon[0][2]
        MinLon = polygon[0][3]
        if lon>MinLon and lon<Maxlon and lat>MinLat and lat<Maxlat:
            if polygon[1].contains(point):
                return polygon[2],polygon[3]
    return 'NA','NA'

# In[118]:

'''
Description: Clean the text collected from Aqar website (area and cost)
Input:
    area: area tex
    cost: cost text
Output:
    Area as float,cost as float and price per sq. meter as float
'''
def CleanListingInfo(area,cost):#Returns the area and cost in the correct format
    try:
        if 'المساحة' in area and 'متر مربع' in area and ('ريال سعودي' in cost or 'ريال' in cost):
            cost = cost.replace('ريال سعودي','')
            cost = cost.replace('ريال','')
            if 'ألف' in cost:
                cost = cost.replace('ألف','').replace('يومي','').replace('سنوي','').replace('\\','').replace(' ','').replace(',','')
                try:   
                    cost = float(cost)*1000
                except:
                    cost = float(re.findall("[-+]?\d+[\.]?\d*[eE]?[-+]?\d*", cost)[0])*1000
            elif 'مليون' in cost:
                cost = cost.replace('مليون','').replace('يومي','').replace('سنوي','').replace('\\','').replace(' ','').replace(',','')
                try:   
                    cost = float(cost)*1000000
                except:
                    cost = float(re.findall("[-+]?\d+[\.]?\d*[eE]?[-+]?\d*", cost)[0])*1000000
            elif 'مليار' in cost:
                cost = cost.replace('مليار','').replace('يومي','').replace('سنوي','').replace('\\','').replace(' ','').replace(',','')
                try:   
                    cost = float(cost)*1000000000
                except:
                    cost = float(re.findall("[-+]?\d+[\.]?\d*[eE]?[-+]?\d*", cost)[0])*1000000000
            else:
                cost = cost.replace('مليار','').replace('يومي','').replace('سنوي','').replace('\\','').replace(' ','').replace(',','')
                try:   
                    cost = float(cost)
                except:
                    cost = float(re.findall("[-+]?\d+[\.]?\d*[eE]?[-+]?\d*", cost)[0])
            

            AreaValue = float(area.replace('المساحة','').replace('متر مربع','').replace(' ','').replace('\يومي',''))
            CostValue = cost
            PPMValue = CostValue/AreaValue
            
            return AreaValue,CostValue,PPMValue
    except Exception as e:
        #print e.args
        return np.nan,np.nan,np.nan


# In[ ]:




# In[120]:

'''
Description: Clean the data collected from Aqar website and arrange features
Input:
    AllAqarData: The Aqar data
    ShapeFile: Shapefile of the city
    Lands: a boolean of weather the data represent land or villas
Output:
    Area as float,cost as float and price per sq. meter as float
'''
def ReorganizeAqarListings(AllAqarData,ShapeFile,Lands=True):
    NewAqar = []
    c = 0
    if Lands == True:
        locs = [3,8,9,10,11]
    else:
        locs = [3,8,'',9,10]
            
    for dp in AllAqarData:
        cost = dp[locs[0]]
        area = dp[locs[1]]
        #Clean the numbers
        area,cost,ppm = CleanListingInfo(area,cost)
        if area != np.nan and cost != np.nan and ppm != np.nan:
            try:
                cat = dp[locs[2]]
            except:
                cat = 'NA'
            lat = dp[locs[3]]
            lon = dp[locs[4]]
            Neighborhood,Munc = IdentifyNeighborhoodName(lat,lon,ShapeFile)

            NewAqar.append([cost,area,ppm,cat,lat,lon,Neighborhood,Munc])
        else:
            c+=1
    
    return NewAqar,c
def ReorganizeAqarListings_NoCleanning(AllAqarData,Lands=True):
    NewAqar = []
            
    for dp in AllAqarData:
        cost = dp[0]
        area = dp[1]
        ppm = dp[2]
        if Lands == True:
            cat = dp[3]
            lat = dp[4]
            lon = dp[5]
            Neighborhood = dp[6]
            Munc = dp[7]
        else:
            cat = 'NA'
            lat = dp[3]
            lon = dp[4]
            Neighborhood = dp[5]
            Munc = dp[6]

        NewAqar.append([cost,area,ppm,cat,lat,lon,Neighborhood,Munc])
    return NewAqar


def ReorganizeAqarListings_Json(AllAqarData,ShapeFile,Lands=True):
    PolygonsDict = {}
    i = 0
    for feature in ShapeFile['features']:
        polygon = shape(feature['geometry'])
        geom = feature['geometry']['coordinates'][0]
        lons, lats = zip(*geom)
        Maxlat = np.max(lats)
        MinLat = np.min(lats)
        Maxlon = np.max(lons)
        MinLon = np.min(lons)
        BBox = [Maxlat,MinLat,Maxlon,MinLon]
        PolygonsDict[i] = [BBox,polygon,feature['properties']['District_N'],feature['properties']['Municipali']]
        i+=1
    NewAqar = []
    c = 0
    for dp in tqdm(AllAqarData):
        start = time.clock()
        cost = float(dp['price'])
        area = float(dp['size'])
        #Clean the numbers
        try:
            ppm = cost/area
        except:
            c+=1
            ppm = np.nan
            pass
        if np.isnan(area) == False and np.isnan(cost) == False and np.isnan(ppm) == False:
            try:
                cat = dp['c_type']
            except:
                cat = 'NA'
            lat = dp['lat']
            lon = dp['lng']
            Neighborhood,Munc = IdentifyNeighborhoodName2(lat,lon,PolygonsDict)
            NewAqar.append([cost,area,ppm,cat,lat,lon,Neighborhood,Munc])
        else:
            c+=1
    return NewAqar,c

# In[ ]:




# In[127]:

#SampleAqarData = np.array(p.read_csv('Data/Aqar_website_Madinah_Land_Full.csv',sep='^'))
#f = open('../../SHAPEFILES_MOH/Madinah/Madinah_Districts.geojson')
#ShapeFile = json.load(f)
#NewAqar,c = ReorganizeAqarListings(SampleAqarData,ShapeFile,True)


# In[ ]:




# In[ ]:



