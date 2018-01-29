
# coding: utf-8

# In[1]:

import csv
import time
import numpy as np
import json
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as p
import unicodedata
import re
from tqdm import tqdm

# In[2]:

reload(sys)
sys.setdefaultencoding("utf-8")



# In[4]:

def RemoveUnnesessaryText(str1):
    #Remove abnormal words
    tempStr1 = str1.replace('على ','')
    tempStr1 = tempStr1.replace('وادي ','')
    tempStr1 = tempStr1.replace('حارة ','')
    tempStr1 = tempStr1.replace(' حي ','')
    
    #Remove abnormal characters
    tempStr1 = tempStr1.replace('أ','ا')
    tempStr1 = tempStr1.replace('إ','ا')
    tempStr1 = tempStr1.replace('آ','ا')
    tempStr1 = tempStr1.replace("اً","ا")
    tempStr1 = tempStr1.replace('ى','ي')
    tempStr1 = tempStr1.replace('ة','ه')
    tempStr1 = tempStr1.replace('ؤ','و')
    tempStr1 = tempStr1.replace('ئ','ي')
    
    tempStr1 = tempStr1.replace("ابي ","")#Remove because they cause errors -- convert to expressions
    tempStr1 = tempStr1.replace("ابو ","")#Remove because they cause errors -- convert to expressions
    tempStr1 = tempStr1.replace("وال","ال")
    tempStr1 = tempStr1.replace('بال','ال')
    #Replace alttweel of the arabic words
    tempStr1 = tempStr1.replace('ـ','')
    
    tempStr1 = tempStr1.replace('.','')
    
    #Remove regular expressions
    tempStr1 = re.sub(r'(رقم)* [\d]', '', tempStr1)
    tempStr1 = tempStr1.strip()
    tempStr1 = re.sub(r'(يمين)*', '', tempStr1)
    tempStr1 = tempStr1.strip()
    tempStr1 = re.sub(r'(يسار)*', '', tempStr1)
    tempStr1 = tempStr1.strip()
    
    tempStr1 = re.sub(r'(/)*', '', tempStr1)
    tempStr1 = tempStr1.strip()
    
    
    #tempStr1 = re.sub(r' [\xd8-\xdb]{1}', '',tempStr1)
    #tempStr1 = tempStr1.strip()
    
    #tempStr1 = re.sub(r' [\xd8\xa1-\xd9\x85]*', '',tempStr1)
    #tempStr1 = tempStr1.strip()
    
    #tempStr1 = re.sub(r' [\xd8\x80-\xd9\xbf]*', '',tempStr1)
    #tempStr1 = tempStr1.strip()
    
    #tempStr1 = re.sub(r' [\xd8\x80-\xd9\xbf]$', '',tempStr1)
    #tempStr1 = tempStr1.strip()
    
    return tempStr1
    


# In[5]:

import codecs, difflib, distance
from fuzzywuzzy import fuzz
def StringsSimilarity(str1,str2):
    #jac   = difflib.SequenceMatcher(None, str1,str2).ratio()
    #jac     = Levenshtein.ratio(sr[3], sr[4]) 
    #sor     = distance.sorensen(str1,str2)
    #jac     = (100 - fuzz.partial_ratio(str1,str2))/100.0
    #Identify the similarity using jaccard
    jac     = distance.jaccard(str1,str2)
    #Identify the number of intersected words
    TotalIntersection = 0
    str1Arr = str1.split(' ')
    str2Arr = str2.split(' ')
    for item1 in str1Arr:
        for item2 in str2Arr:
            if item1 == item2:
                TotalIntersection+=1
    
    return jac,TotalIntersection/float(len(str1Arr))

    #return sor
    #return diffl


# In[6]:

#Prepare the neighborhood list (Neetaq Omrani)
def GenerateNeighborhoodList(NeetaqFile):
    fileToOpen = open(NeetaqFile)
    ShapeFile = json.load(fileToOpen,encoding='utf-8')
    NeighborhoodsList = []
    for feature in ShapeFile['features']:
        NeighborhoodsList.append([feature['properties']['District_N'],feature['properties']['Municipali']])
    return NeighborhoodsList


# In[7]:

#Identify the most similar neighborhood for a single transaction
#Use Jaccard Similarity
def MostSimilarNeighborhood_jac(NeighborhoodsList,Name):
    Similarity = []
    for neighborhood in NeighborhoodsList:
        t = []
        t.append(Name)
        t.append(neighborhood[0])
        t.append(neighborhood[1])
        Jac,Intersections = StringsSimilarity(RemoveUnnesessaryText(Name),RemoveUnnesessaryText(neighborhood[0]))
        t.append(Jac)
        t.append(Intersections)
        #for ele in StringsSimilarity(RemoveUnnesessaryText(Name),RemoveUnnesessaryText(neighborhood[0])):
            #t.append(ele)
        Similarity.append(t)
    #Identify the neighborhood with the lowest jaccard Index
    Similarity = np.array(Similarity)
    Similarity = Similarity[np.argsort(Similarity[:,3])]
    return Similarity[0]


# In[8]:

def CheckContainment(NeighborhoodsList,Name):
    #To identify the number of words
    SpaceCounter = str.count(str(Name),' ')
    
    Name = RemoveUnnesessaryText(Name)
    if SpaceCounter>0:
        for neighborhood in NeighborhoodsList:
            if Name in RemoveUnnesessaryText(str(neighborhood[0])):
                return [neighborhood[0],neighborhood[1],0.0,1]
        return None
    else:
        for neighborhood in NeighborhoodsList:
            counter = 0
            Neigh_Name = RemoveUnnesessaryText(str(neighborhood[0]))
            for word in str.split(Neigh_Name,' '):
                word = RemoveUnnesessaryText(word)
                if Name == word :
                    return [neighborhood[0],neighborhood[1],0.0,1]
        return None


# In[9]:

def CheckContainment_Jaccard(NeighborhoodsList,Name):
    #To identify the number of words
    SpaceCounter = str.count(str(Name),' ')
    
    Name = RemoveUnnesessaryText(Name)
    if SpaceCounter>0:
        MostSimilar = MostSimilarNeighborhood_jac(NeighborhoodsList,Name)
        if float(MostSimilar[3]) <= 0.1:# or str.count(str(neigh),' ') > 3:
                return MostSimilar[1:]
        else:
            return None
    else:
        for neighborhood in NeighborhoodsList:
            counter = 0
            Neigh_Name = RemoveUnnesessaryText(str(neighborhood[0]))
            for word in str.split(Neigh_Name,' '):
                word = RemoveUnnesessaryText(word)
                jac,intersection = StringsSimilarity(Name,word)
                if jac <= 0.1 :
                    return [neighborhood[0],neighborhood[1],0.0,1]
        return None


# In[10]:

def IdentifyTransactionsNeighborhoods(TransactionsData,NeighborhoodsList):
    Result = []
    Neighs_Match = {}
    #Find the match for every unique name in the transactions list
    UniqueNeighs = np.unique(TransactionsData[:,2])
    for neigh in tqdm(UniqueNeighs):
        MostSimilar = MostSimilarNeighborhood_jac(NeighborhoodsList,neigh)
        if float(MostSimilar[3]) <= 0.1:# or str.count(str(neigh),' ') > 3:
            Neighs_Match[neigh] = MostSimilar[1:]
        else:#Use other method if jaccard doesn't work (Containment of first two words)
            TextSplitted = str.split(str(neigh),' ')
            try:
                NewName = TextSplitted[0]+' '+TextSplitted[1]
            except:
                NewName = TextSplitted[0]
            MostContained = CheckContainment_Jaccard(NeighborhoodsList,NewName)
            if MostContained == None: #if two words doesn't work, try Containment of first word.
                NewName = TextSplitted[0]
                MostContained = CheckContainment_Jaccard(NeighborhoodsList,NewName)
                if MostContained == None:#Check the containment of any word
                    Neighs_Match[neigh] = ['NA','NA',1.0,0.0]
                    TextSplitted = str.split(str(neigh),' ')
                    PossibleMatches = []
                    for word in TextSplitted:#Loop on every word in the neighborhood name
                        MostContained = CheckContainment_Jaccard(NeighborhoodsList,word)
                        if MostContained != None:
                            PossibleMatches.append(MostContained)
                    if len(PossibleMatches)>0:
                        Neighs_Match[neigh] = PossibleMatches[0]
                else:
                    Neighs_Match[neigh] = MostContained
            else:
                Neighs_Match[neigh] = MostContained
    #Find the neighborhood match from the dictionary of matches
    for trans in TransactionsData:
        MostSimilar = Neighs_Match[trans[2]]
        t = []
        for ele in trans:
            t.append(ele)
        for ele in MostSimilar:
            t.append(ele)
        Result.append(t)
    Result = np.array(Result)
    return Result[:,:15]


def IdentifyTransactionsNeighborhoods_ForRiyadh(TransactionsData,NeighborhoodsList):
    Result = []
    Neighs_Match = {}
    #Find the match for every unique name in the transactions list
    UniqueNeighs = np.unique(TransactionsData[:,2])
    for neigh in tqdm(UniqueNeighs):
        if neigh=='إشبيلية':
            neigh = 'اشبيليا'
        elif neigh=='الشفا':
            neigh = 'الشفاء'
        elif neigh=='غبيرا':
            neigh = 'غبيراء'
        elif neigh=='المعيزيلة':
            neigh = 'المعيزلية'
        elif neigh=='الإسكان':
            neigh = 'الاسكان'
        elif neigh=='الصفا':
            neigh = 'الصفاء'

        MostSimilar = MostSimilarNeighborhood_jac(NeighborhoodsList,neigh)
        if float(MostSimilar[3]) <= 0.1:# or str.count(str(neigh),' ') > 3:
            Neighs_Match[neigh] = MostSimilar[1:]
        else:#Use other method if jaccard doesn't work (Containment of first two words)
            TextSplitted = str.split(str(neigh),' ')
            try:
                NewName = TextSplitted[0]+' '+TextSplitted[1]
            except:
                NewName = TextSplitted[0]
            MostContained = CheckContainment_Jaccard(NeighborhoodsList,NewName)
            if MostContained == None: #if two words doesn't work, try Containment of first word.
                NewName = TextSplitted[0]
                MostContained = CheckContainment_Jaccard(NeighborhoodsList,NewName)
                if MostContained == None:#Check the containment of any word
                    Neighs_Match[neigh] = ['NA','NA',1.0,0.0]
                    TextSplitted = str.split(str(neigh),' ')
                    PossibleMatches = []
                    for word in TextSplitted:#Loop on every word in the neighborhood name
                        MostContained = CheckContainment_Jaccard(NeighborhoodsList,word)
                        if MostContained != None:
                            PossibleMatches.append(MostContained)
                    if len(PossibleMatches)>0:
                        Neighs_Match[neigh] = PossibleMatches[0]
                else:
                    Neighs_Match[neigh] = MostContained
            else:
                Neighs_Match[neigh] = MostContained
    #Find the neighborhood match from the dictionary of matches
    for trans in TransactionsData:
        MostSimilar = Neighs_Match[trans[2]]
        t = []
        for ele in trans:
            t.append(ele)
        for ele in MostSimilar:
            t.append(ele)
        Result.append(t)
    Result = np.array(Result)
    return Result[:,:15]
    



# In[ ]:



