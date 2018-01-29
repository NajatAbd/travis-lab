import pandas as p
import numpy as np
import json
import time
import math
import csv
from matplotlib import pyplot as plt
#Munc	Neighborhood	Median	Mean	Count	QuartilesAvg	ECDF	ZoneId	ZoneColor	CityIndex

def GetIndex(neigh,munc,Index):
	Index = np.array(Index)
	select = np.logical_and(Index[:,1] == neigh,Index[:,2] == munc)
	try:
		Value = Index[select][0][0]
	except:
		Value = np.nan
		pass
	return Value

'''
Description: This function prepares the final results of the lands valuation
NeighborhoodsList: Neighborhood, Munacipality
NeighborhoodsIndex_ECDF: Index, Neighborhood, Munacipality
NeighborhoodsIndex_Median: Index, Neighborhood, Munacipality
NeighborhoodsIndex_Quartiles: Index, Neighborhood, Munacipality
NeighborhoodsIndex_Mean: Index, Neighborhood, Munacipality
Zonning: Neighborhood, Munacipality, ZoneId, ZoneColor
Count: Count, Neighborhood, Munacipality
CityIndex: float
'''
def PrepareResults(NeighborhoodsList,NeighborhoodsIndex_ECDF,NeighborhoodsIndex_Median,NeighborhoodsIndex_Quartiles,NeighborhoodsIndex_Mean,Count,Zonning,CityIndex):
	AllNeighs = []
	AllIndicies = [NeighborhoodsIndex_Median,NeighborhoodsIndex_Mean,Count,NeighborhoodsIndex_Quartiles,NeighborhoodsIndex_ECDF]
	for neighborhood in NeighborhoodsList:
		Neigh = []
		Neigh.append(neighborhood[1])
		Neigh.append(neighborhood[0])
		for Index in AllIndicies:
			Neigh.append(GetIndex(neighborhood[0],neighborhood[1],Index))
		#Zonning data
		select = np.logical_and(Zonning[:,0] == neighborhood[0],Zonning[:,1] == neighborhood[1])
		try:
			Value1 = Zonning[select][0][2]
			Value2 = Zonning[select][0][3]
			Neigh.append(Value1)
			Neigh.append(Value2)
		except:
			Value1 = np.nan
			Value2 = np.nan
			Neigh.append(Value1)
			Neigh.append(Value2)
			pass
		Neigh.append(CityIndex)
		AllNeighs.append(Neigh)
	return np.array(AllNeighs)

def SaveResults(Result,FileLocation,FileName):
	with open(FileLocation+FileName+'.csv','wb') as csvfile:
		writer = csv.writer(csvfile,delimiter=',')
		header = ['Munc','Neighborhood','Median','Mean','Count','QuartilesAvg','ECDF','ZoneId','ZoneColor','CityIndex']
		writer.writerow(header)
		for item in Result:
			writer.writerow(item)

def SaveResults_Json(Result,FileLocation,FileName):
	AllDicts = []
	header = ['Munc','Neighborhood','Median','Mean','Count','QuartilesAvg','ECDF','ZoneId','ZoneColor','CityIndex']
	for item in Result:
		Dict = {}
		for i,ele in enumerate(item):
			if i == 0 or i == 1 or i == 8:
				Dict[header[i]] = str(ele)
			else:
				Dict[header[i]] = float(ele)
		AllDicts.append(Dict)
	
	with open(FileLocation+FileName+'.json','wb') as jsonfile:
		for i,item in enumerate(AllDicts):
			json.dump(item,jsonfile,ensure_ascii=False)
			if i != len(AllDicts) - 1:
				jsonfile.write(',')
				jsonfile.write('\n')

		# for i,dictt in enumerate(AllDicts):
		# 	jsonfile.write(dictt)
		# 	if i!= len(AllDicts) - 1:
		# 		jsonfile.write(',')
		# 		jsonfile.write('\n')
