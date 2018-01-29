'''
This is the full pipeline for the lands valuation project
Input:
	Transactions1: MOJ transactions
	NeetaqJson: The geojson of the shapefile
	AqarLand1: Json of aqar website lands data
	AqarVillas1: Json of aqar website villas data
	AqarBuildings1: Json of aqar website buildings data	(only for Makkah and Madinah)
'''

import pandas as p
import numpy as np
import json
import time
import math
import csv
from matplotlib import pyplot as plt

import A0_AqarWebsite_CleanAqarData_Files as A0
import A0_Assign_Transactions_To_Neighbourhoods_Copy1 as A0_1
import A_Clean_Save_Unique_Transactions as A
import B_Clean_MOH_Remove_outliers as B
import C_Clean_Transactions_Villas_Shared_Area as C
import C_SVM as C0
import D_Ranking_MOH_ECDF_Median_Quartiles_Copy1 as D
import E_Ranking_City_MOH_ECDFComparison_Cities as E
import F_Zonning_Index as F
import H_Plot_the_estimated_values as H
import I_Prepare_Results as I
import J_Manual_Mapping_Neighborhoods_Names as J

import warnings
warnings.filterwarnings('ignore')

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

listOfArguments = sys.argv[1:]
CityName = str(listOfArguments[0])
StartYear = int(listOfArguments[1])
EndYear = int(listOfArguments[2])
status = int(listOfArguments[3])

#CityName = str(input('Enter city name: '))
#CityName = 'Makkah'

#1. Collect the data from MOJ and Aqar
TransactionsDataLocation = 'Data/'+CityName+'-Final-MOJ-239.csv'
#Identify the location of the neighborhood names (Json file)
NeetaqJson = CityName+'/'+CityName+'_Districts.geojson'
NeetaqShp = CityName+'/'+CityName+'_Districts.geojson'
NeetaqLoc = CityName+'/'
NeetaqJsonFileName = CityName+'_Districts.geojson'

#StartYear = int(input('Enter Start Year: '))
#EndYear = int(input('Enter End Year: '))

start = time.clock()
#Read MOJData
Transactions1 = np.array(p.read_csv(TransactionsDataLocation))
select = np.logical_and(Transactions1[:,0]>=StartYear,Transactions1[:,0]<=EndYear)

# select1 = np.logical_and(Transactions1[:,0]==1438,Transactions1[:,1]>=9)
# select2 = np.logical_and(Transactions1[:,0]==1439,Transactions1[:,1]<3)
# select = np.logical_or(select1,select2)

Transactions1 = Transactions1[select]
print 'Finished choosing years of study ',len(Transactions1),' Time:', time.clock() - start


#Perform any cleanning to the collection stage related to Aqar
f = open(NeetaqJson)
ShpFile = json.load(f)

start = time.clock()

JsonFile = open('Data/Aqar_API/'+CityName+'_Land.json')
AqarLand1 = json.load(JsonFile)
AqarLand1,c = A0.ReorganizeAqarListings_Json(AqarLand1,ShpFile,True)

# CSVFile = 'Data/Aqar_API/'+CityName+'_Land_Aqar_All.csv'
# AqarLand1 = np.array(p.read_csv(CSVFile,sep='\t',header = None))
# AqarLand1 = A0.ReorganizeAqarListings_NoCleanning(AqarLand1,Lands=True)

JsonFile = open('Data/Aqar_API/'+CityName+'_Villa.json')
AqarVillas1 = json.load(JsonFile)
AqarVillas1,c = A0.ReorganizeAqarListings_Json(AqarVillas1,ShpFile,False)

# CSVFile = 'Data/Aqar_API/'+CityName+'_Villas_Aqar_All.csv'
# AqarVillas1 = np.array(p.read_csv(CSVFile,sep='\t',header = None))
# AqarVillas1 = A0.ReorganizeAqarListings_NoCleanning(AqarVillas1,Lands=False)

AqarBuildings1 = []
if (CityName=='Makkah' or CityName=='Madinah'):
	JsonFile = open('Data/Aqar_API/'+CityName+'_Building.json')
	AqarBuildings1 = json.load(JsonFile)
	AqarBuildings1,c = A0.ReorganizeAqarListings_Json(AqarBuildings1,ShpFile,True)

temp = []
if status == 1 or status == 2:
	for item in AqarVillas1:
		temp.append(item)

if status == 2:
	for item in AqarBuildings1:
		temp.append(item)
AqarVillas1 = np.array(temp)

print 'Finished Clean Aqar Collected Data ',' Time:', time.clock() - start


#Fix the neighborhoods names based on a prepared mapping
try:
	Mapping = np.array(p.read_csv('Data/'+CityName+'_Neighborhood_names_fix.csv',header = None))
	Transactions1 = np.array(J.MapNames(Transactions1,Mapping))
except Exception as e:
	print e.args
	pass

start = time.clock()
#Get the city neighborhoods
NeighborhoodsList = A0_1.GenerateNeighborhoodList(NeetaqJson)
#Perform the cleanning of neighborhoods names in MOJ Data
if CityName == 'Riyadh':
	Mapping = np.array(p.read_csv('Data/'+CityName+'_Neighborhood_names_mapping.csv'))
	Transactions1 = A0_1.IdentifyTransactionsNeighborhoods_ForRiyadh(Transactions1,NeighborhoodsList,Mapping)
elif CityName == 'Jeddah' or CityName == 'Dammam':
	Mapping = np.array(p.read_csv('Data/'+CityName+'_Neighborhood_names_mapping.csv'))
	Transactions1 = A0_1.IdentifyTransactionsNeighborhoods_ForJeddah(Transactions1,NeighborhoodsList,Mapping)
else:
	Transactions1 = A0_1.IdentifyTransactionsNeighborhoods(Transactions1,NeighborhoodsList)

#To test some of the code
with open('Data/'+CityName+'_NotMappedNeighs.csv','wb') as csvfile:
	writer = csv.writer(csvfile,delimiter=',')
	for item in Transactions1:
		writer.writerow(item)

Transactions1 = Transactions1[Transactions1[:,13]!='NA']
print 'Finished Assign Transactions To Neighbourhoods ',len(Transactions1),' Time:', time.clock() - start

#Remove the duplicate transactions 
start = time.clock()
Transactions1 = A.RemoveDups(Transactions1)
print 'Finished RemoveDuplicates',len(Transactions1),' Time:', time.clock() - start

start = time.clock()
#Remove the outlier transactions
Transactions1 = B.RemoveOutliers(Transactions1)
print 'Finished RemoveOutliers ',len(Transactions1),' Time:', time.clock() - start
Transactions1 = np.array(Transactions1)

start = time.clock()
#Reject transactions based on Aqar website data
#Get the SVM Labels
header = ['Year','Month','Neighborhood','Cat','Type','Plan','Parcel','TID','TotalCost','Area','PPSM','City','Date','NewNeighborhood','MUNC']
NewData = [header]
temp = []
for item in Transactions1:
    temp.append(list(item))
NewData.extend(temp)
LabeledTran = C0.CleanMOJUsingSVM(NewData,AqarLand1,AqarVillas1,False,False,CityName)[1:]

tempr = []
for item in LabeledTran:
	if len(item)==17:
		tempr.append(item)
print 'tempr',len(tempr)
print 'Finished SVM prediction ',' Time:', time.clock() - start

#Perform the rejection of wrongly labeled transactions
start = time.clock()

Transactions1 = C.ApplyTransactionsRejections(AqarVillas1,AqarLand1,Transactions1,np.array(tempr))
print 'Finished Cleaning Wrongly Labeled Transactions ',len(Transactions1),' Time:', time.clock() - start

#To test some of the code
with open('Data/'+CityName+'_AfterCleanning.csv','wb') as csvfile:
	writer = csv.writer(csvfile,delimiter=',')
	for item in Transactions1:
		writer.writerow(item)


#Remove Certain neighborhoods that are not in Neetaq Omrani
try:
	Blacklist = np.array(p.read_csv('Data/'+CityName+'_Blacklist.csv',header=None))
except Exception as e:
	Blacklist = []
Transactions1,NeighborhoodsList = A.RemoveNeighborhoods(Transactions1,NeighborhoodsList,Blacklist)
print 'Finished Remove Blacklisted Neighborhoods',len(Transactions1),len(NeighborhoodsList)

#Generate the city index number
start = time.clock()
CityIndex = E.GenerateCityIndex([[CityName,Transactions1[:,10].astype(float)]],'MOHplots/',CityName+'-CityIndex')
print CityIndex
print 'Finished CityIndex',' Time:', time.clock() - start

# #Perform the Ranking
Transactions1 = np.array(Transactions1)
Transactions1 = Transactions1[:,:15]

start = time.clock()
Prepared = D.PrepareTransactionsPrices(Transactions1,NeighborhoodsList)
Prepared = np.array(Prepared)

# Prepared = [[10000,1000,5000],[10,4,5],[1,2,2],[2,3,4],[22,4,32]]
D.PlotECDFOfCity(Prepared,'MOHplots',CityName+'_ECDF')


ECDFSum,Notmapped = D.GenerateECDFSum(Prepared,NeighborhoodsList)
Medians = D.IdentifyAllmedians(Prepared)

NeighborhoodIndex_ECDF = D.GenerateECDFNeighborhoodIndex(ECDFSum,Medians,NeighborhoodsList)
NeighborhoodIndex_Median = D.GenerateMedianNeighborhoodIndex(Prepared,NeighborhoodsList)
NeighborhoodIndex_Quartiles = D.GenerateQuartilesNeighborhoodIndex(Prepared,NeighborhoodsList)
NeighborhoodIndex_Mean = D.GenerateMeanNeighborhoodIndex(Prepared,NeighborhoodsList)
Count = D.GenerateCountNeighborhoodIndex(Prepared,NeighborhoodsList)

print 'Finished Neighborhoods Index ',' Time:', time.clock() - start

start = time.clock()
#Perform the smoothing of the ranking
Adjacency = D.GenerateNeighborhoodsAdjacency(NeetaqLoc,NeetaqJsonFileName)
#print NeighborhoodIndex_ECDF
NeighborhoodIndex_ECDF = D.SpatialSmoothing(NeighborhoodIndex_ECDF,Adjacency)
if np.sum(np.isnan(NeighborhoodIndex_ECDF[:,0].astype(float)))>0:
	NeighborhoodIndex_ECDF = D.SpatialSmoothing(NeighborhoodIndex_ECDF,Adjacency)

NeighborhoodIndex_Median = D.SpatialSmoothing(NeighborhoodIndex_Median,Adjacency)
NeighborhoodIndex_Quartiles = D.SpatialSmoothing(NeighborhoodIndex_Quartiles,Adjacency)
NeighborhoodIndex_Mean = D.SpatialSmoothing(NeighborhoodIndex_Mean,Adjacency)
print 'Finished Spatial Smoothing ',' Time:', time.clock() - start


#NeighborhoodIndex_ECDF = np.array(NeighborhoodIndex_Median)
#do not compare untrusted transactions
# TrustedIndex = []
# Count = np.array(Count)
# for item in NeighborhoodIndex_ECDF:
# 	Selection = np.logical_and(Count[:,1] == item[1],Count[:,2] == item[2])
# 	try:
# 		SelectedRes = Count[Selection][0]
# 		TransCount = int(SelectedRes[0])
# 	except e as Exception:
# 		print e.args()
# 		TransCount = 0
# 	if TransCount > 50:
# 		TrustedIndex.append(item)
# NeighborhoodIndex_ECDF = np.array(TrustedIndex)

#D.PlotECDFOfCity(Prepared,'MOHplots','Test')
def RemoveNans(NeighborhoodIndex,col):
	NeighborhoodIndex_ECDF_Cleaned = []
	for item in NeighborhoodIndex_ECDF:
		if np.isnan(float(item[col])) == False:
			NeighborhoodIndex_ECDF_Cleaned.append(item)
	return NeighborhoodIndex_ECDF_Cleaned
#D.PlotECDFOfCity(Prepared,'MOHplots','Test')

#Show the correlation with aqar website
for c in range(1,12):
	try:
		CompanyEstimations = []
		with open('Data/External_Estimations/AqarisComparison_'+CityName+'_'+str(c)+'.csv','rb') as csvfile:
			reader = csv.reader(csvfile,delimiter=',')
			CompanyEstimationsPandas = p.read_csv(csvfile)
			CompanyName = CompanyEstimationsPandas.keys()[0]


		CompanyEstimations = np.array(CompanyEstimationsPandas) 
		H.GenerateCorrelationPlot(NeighborhoodIndex_ECDF,CompanyEstimations,CompanyName,'MOHplots/',CityName+'-Correlation_'+str(c))
	except Exception as e:
		print e.args
		print 'No more external estimations to compare to and completed', c - 1
		break

NeighborhoodIndex_ECDF = np.array(RemoveNans(NeighborhoodIndex_ECDF,0))
NeighborhoodIndex_ECDF = np.array(NeighborhoodIndex_ECDF)

start = time.clock()
Clusters = 4
clf = F.ClusterNeighborhoods(NeighborhoodIndex_ECDF,NumberOfClusters = Clusters)
ClassifiedNeighborhoods = F.ClassifyNeighborhoods(NeighborhoodIndex_ECDF,clf)
F.GenerateZoningIndexDensityPlot(NeighborhoodIndex_ECDF,clf,'MOHplots/',CityName+'-ZonningIndexDensity',NumberOfClusters = Clusters)
F.GenerateZoningIndexMapPlot(NeighborhoodIndex_ECDF,clf,NeetaqShp,'MOHplots/',CityName+'-ZonningIndexMap',NumberOfClusters = Clusters)
ClassifiedNeighborhoods = np.array(ClassifiedNeighborhoods)
print 'Finished Zoning ',' Time:', time.clock() - start


#Prepare the result of the lands valuation method
NeighborhoodIndex_ECDF = np.array(NeighborhoodIndex_ECDF)
NeighborhoodIndex_Median = np.array(NeighborhoodIndex_Median)
NeighborhoodIndex_Quartiles = np.array(NeighborhoodIndex_Quartiles)
NeighborhoodIndex_Mean = np.array(NeighborhoodIndex_Mean)
Count = np.array(Count)

FinalResult = I.PrepareResults(NeighborhoodsList,NeighborhoodIndex_ECDF,NeighborhoodIndex_Median,NeighborhoodIndex_Quartiles,NeighborhoodIndex_Mean,Count,ClassifiedNeighborhoods,CityIndex[1][1])
I.SaveResults(FinalResult,'MOHplots/','FinalResult-'+CityName)
I.SaveResults_Json(FinalResult,'MOHplots/','FinalResult-'+CityName)

#Plot the map of density
NeighborhoodIndex_ECDF = np.array(NeighborhoodIndex_ECDF)
NeighborhoodIndex_ECDF = np.array(RemoveNans(NeighborhoodIndex_ECDF,0))
NeighborhoodIndex_ECDF = NeighborhoodIndex_ECDF[np.argsort(NeighborhoodIndex_ECDF[:,0].astype(float))]

#Generate the map and bar chart of the index
H.GenerateNeighborhoodIndexMap(NeighborhoodIndex_ECDF,NeetaqShp,'MOHplots/',CityName+'-Map')
#H.GenerateNeighborhoodIndexBarChart(NeighborhoodIndex_ECDF,'MOHplots/',CityName+'-Bar')
# for item in NeighborhoodIndex_Median:
# 	print item[0]
#plt.show()

