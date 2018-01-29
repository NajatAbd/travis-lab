import pandas as p
import numpy as np
import json
import time
import math
import csv
from matplotlib import pyplot as plt

import A0_AqarWebsite_CleanAqarData_Files as A0

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

AqarBuildings1 = np.array(p.read_csv('Data/Aqar_website_Makkah_Building_Full.csv',sep='^'))


CityName = str(input('Enter city name: '))

NeetaqJson = '../../SHAPEFILES_MOH/'+CityName+'/'+CityName+'_Districts.geojson'
NeetaqShp = '../../SHAPEFILES_MOH/'+CityName+'/'+CityName+'_Districts.geojson'
NeetaqLoc = '../../SHAPEFILES_MOH/'+CityName+'/'
f = open(NeetaqJson)
ShpFile = json.load(f)

AqarLand1 = np.array(p.read_csv('Data/Aqar_website_'+CityName+'_Land_Full.csv',sep='^'))
AqarLand1,c = A0.ReorganizeAqarListings(AqarLand1,ShpFile,True)

with open('Data/Aqar_website_'+CityName+'_Land_Full_Cleaned.csv','wb') as csvfile:
	writer = csv.writer(csvfile,delimiter='^')
	for item in AqarLand1:
		writer.writerow(item)

AqarVillas1 = np.array(p.read_csv('Data/Aqar_website_'+CityName+'_Villas_Full.csv',sep='^'))
AqarVillas1,c = A0.ReorganizeAqarListings(AqarVillas1,ShpFile,False)
if CityName=='Makkah':
	AqarBuildings1 = np.array(p.read_csv('Data/Aqar_website_'+CityName+'_Building_Full2.csv',sep='^'))
	AqarBuildings1,c = A0.ReorganizeAqarListings(AqarBuildings1,ShpFile,True)

#Read Aqar Buildings and Combine

with open('Data/Aqar_website_'+CityName+'_Villas_Full_Cleaned2.csv','wb') as csvfile:
	writer = csv.writer(csvfile,delimiter='^')
	for item in AqarVillas1:
		writer.writerow(item)
	if CityName=='Makkah':
		for item in AqarBuildings1:
			writer.writerow(item)

