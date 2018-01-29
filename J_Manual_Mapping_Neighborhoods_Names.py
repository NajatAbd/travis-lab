# -*- coding: utf-8 -*-
import numpy as np
import json
import time
import math
import csv


def MapNames(Data,Mapping):
	NewData = []
	c = 0
	for row in Data:
		temp = []
		for i,ele in enumerate(row):
			if i == 2:
				try:
					selection = Mapping[:,0] == row[2]
					NewName = Mapping[selection][0][1]
				except Exception as e:
					#print e.args
					NewName = ele
				temp.append(NewName)
			else:
				temp.append(ele)
		NewData.append(temp)
	return NewData
