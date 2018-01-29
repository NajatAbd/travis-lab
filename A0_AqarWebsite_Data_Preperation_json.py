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

CityName = str(input('Enter city name: '))
WithBuildings = bool(input('Include Buildings? True or False: '))

NeetaqJson = '../../SHAPEFILES_MOH/'+CityName+'/'+CityName+'_Districts.geojson'
NeetaqShp = '../../SHAPEFILES_MOH/'+CityName+'/'+CityName+'_Districts.geojson'
NeetaqLoc = '../../SHAPEFILES_MOH/'+CityName+'/'
f = open(NeetaqJson)
ShpFile = json.load(f)

JsonFile = open('Data/Aqar_API/'+CityName+'_Land.json')
AqarLand1 = json.load(JsonFile)
AqarLand1,c = A0.ReorganizeAqarListings_Json(AqarLand1,ShpFile,True)

print 'Lands',c

with open('Data/Aqar_website_'+CityName+'_Land_Full_Cleaned.csv','wb') as csvfile:
	writer = csv.writer(csvfile,delimiter='^')
	for item in AqarLand1:
		writer.writerow(item)

JsonFile = open('Data/Aqar_API/'+CityName+'_Villa.json')
AqarVillas1 = json.load(JsonFile)
AqarVillas1,c = A0.ReorganizeAqarListings_Json(AqarVillas1,ShpFile,False)
print 'Villa',c


if (CityName=='Makkah' or CityName=='Madinah') or WithBuildings:
	JsonFile = open('Data/Aqar_API/'+CityName+'_Building.json')
	AqarBuildings1 = json.load(JsonFile)
	AqarBuildings1,c = A0.ReorganizeAqarListings_Json(AqarBuildings1,ShpFile,True)
	print 'Building',c

#Read Aqar Buildings and Combine
with open('Data/Aqar_website_'+CityName+'_Villas_Full_Cleaned.csv','wb') as csvfile:
	writer = csv.writer(csvfile,delimiter='^')
	for item in AqarVillas1:
		writer.writerow(item)
if (CityName=='Makkah' or CityName=='Madinah') or WithBuildings:
	with open('Data/Aqar_website_'+CityName+'_Buildings_Full_Cleaned.csv','wb') as csvfile:
		writer = csv.writer(csvfile,delimiter='^')
		for item in AqarBuildings1:
			writer.writerow(item)
