# -*- coding: utf-8 -*-
import random
import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm
import os
import pandas as p

from matplotlib.font_manager import FontProperties
from bidi.algorithm import get_display
import arabic_reshaper

from tqdm import tqdm

#directory = "C:\Users\Zeyad\Desktop\Land Value/SVM/"
#cities = [ "Makkah", "Madinah" ]

#save_svm_plots = True
#save_aqar_plots = True

merge = { "Riyadh": [ ['النسيم الشرقي' ,'النسيم الغربي','النسيم'], ['أم الحمام الشرقي' ,'أم الحمام الغربي',  'أم الحمام'], ['ظهرة البديعة', 'البديعة'], ['السويدي الغربي','السويدي'], ['العريجاء الغربي','العريجاء','العريجاء الأوسط'] ]  }

def read_aqar_data(city,lands,villas):
    #with open(directory + "Data/Aqar_website_" + city + "_Land_Full_Cleaned.csv", 'r') as f:
        #lands = [ row.split('^') for row in f.read().splitlines() ]
    #with open(directory + "Data/Aqar_website_" + city + "_Villas_Full_Cleaned.csv", 'r') as f:
        #villas = [ row.split('^') for row in f.read().splitlines() ]

    #Read Aqar website data
    aqar = { } 
    for row in lands:
        if len(row) < 7 or row[6] == 'NA': continue
        if row[6] not in aqar: aqar[row[6]] = [] 
        aqar[row[6]].append( [np.log(float(row[1])), np.log(float(row[2])), 'Land' ] )
    for row in villas:
        if len(row) < 7 or row[6] == 'NA': continue
        if row[6] not in aqar: aqar[row[6]] = [] 
        aqar[row[6]].append( [np.log(float(row[1])), np.log(float(row[2])), 'Villa' ] )
    return aqar
def CleanMOJUsingSVM(data,lands,villas,save_svm_plots,save_aqar_plots,cityName):

    if len(villas) == 0:
        TransactionsTemp = []
        for item in data:
            tempr = []
            for i,ele in enumerate(item):
                tempr.append(ele)
            tempr.append(0)
            tempr.append(1.0)
            TransactionsTemp.append(tempr)
        return np.array(TransactionsTemp)


    directory = "MOHplots/"

    if not os.path.exists(directory + ""): 
        os.mkdir(directory + "/")
        if save_svm_plots: os.mkdir(directory + "/SVM Plots/")
        if save_aqar_plots: os.mkdir(directory + "/Aqar Plots/")
    
    city = cityName
    if save_svm_plots and not os.path.exists(directory + "/SVM Plots/" + city + "/"): os.mkdir(directory + "/SVM Plots/" + city + "/")
    if save_aqar_plots and not os.path.exists(directory + "/Aqar Plots/" + city + "/"): os.mkdir(directory + "/Aqar Plots/" + city + "/")
    
    aqar = read_aqar_data(city,lands,villas)
    ranked2 = sorted( [ (len(values), key) for key, values in aqar.items() ], reverse = True)

    names = {}
    if city in merge:
        for nameList in merge[city]:
            name = min(nameList, key=len)
            for n in nameList: names[n] = name
    for neigh in aqar:
        if neigh not in names: names[neigh] = neigh
    
    X = []
    index = { neigh: i for i, neigh in enumerate(aqar) }
    for count, neigh in ranked2:
        for x, y, c in aqar[neigh]:
            if not ( np.isnan(x) or np.isnan(y) ):
                c2 = 0 if c=='Land' else 1
                X.append( [ c2, x, y ] + [ 1 if i==index[neigh] else 0 for i in range(len(aqar)) ] )

    random.shuffle(X)
    X_train = [ x[1:] for x in X ]
    X_label = [ x[0] for x in X ]
    clf = svm.SVC(kernel='rbf', probability = True)
    clf.fit( X_train, X_label)
    
    nbh = {}
    #with open(directory + "Data/" + city + "-Final-MOJ.csv", 'r') as f:
        #data = [ row.split(',') for row in f.read().splitlines() ]
    #MOJ data
    
    columns = { n: i for i, n in enumerate(data[0]) }
    if "NewNeighborhood" in columns: name = columns["NewNeighborhood"]
    elif "OriginalName" in columns: name = columns["OriginalName"]
    else: name = columns["Neighborhood"]
    #name = 13
    data2 = [ [ names[unicode(d[name])], float(d[9]), float(d[10]), i ] for i, d in enumerate(data) if i > 0 and unicode(d[name]) in names and len(d) > 10 ]#and d[0] == '1437' ]
    
    for neigh, area, ppm, i in data2:
        if neigh not in nbh: nbh[neigh] = []
        nbh[neigh].append( [np.log(area), np.log(ppm), i] )
    for n in nbh:
        nbh[n] = [ (a,p,i) for a, p, i in nbh[n] if np.isfinite(a) and np.isfinite(p) ]
    
    colors = [ 'aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure', 'beige', 'bisque', 'blanchedalmond', 'blue', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkcyan', 'darkgoldenrod', 'darkkhaki', 'darkmagenta', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkturquoise', 'deeppink', 'deepskyblue', 'dimgray', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'fuchsia', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'gray', 'green', 'greenyellow', 'honeydew', 'hotpink', 'indianred', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgreen', 'lightgray', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightsteelblue', 'lightyellow', 'lime', 'limegreen', 'linen', 'magenta', 'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'oldlace', 'olive', 'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple', 'red', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'silver', 'skyblue', 'slateblue', 'slategray', 'snow', 'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'white', 'whitesmoke', 'yellow', 'yellowgreen' ]
    random.shuffle(colors)
    ranked = sorted( [ (len(values), key) for key, values in nbh.items() ], reverse = True)
    for count, neigh in ranked[:]:
        if neigh not in aqar: continue
        X_train = []
        for x, y, i in nbh[neigh]:
            X_train.append( [ x, y ] + [ 1 if i==index[neigh] else 0 for i in range(len(aqar)) ] )
        X_labels = clf.predict(X_train) 
        X_prob = clf.predict_proba(X_train)       
        for i, label in enumerate(X_labels):
            #Final_Labels.append([data[int(nbh[neigh][i][2])][7],label, max(X_prob[i]) ])
            data[int(nbh[neigh][i][2])] += [ label, max(X_prob[i]) ]
        
        if save_svm_plots:
            colors2 = [ 'red', 'blue', 'green', 'orange', 'purple' 'brown', 'yellow', 'lime', 'lightsteelblue', 'darksalmon', 'cyan', 'teal', 'tan', 'slategray' ] + colors
            labels_found = list( set([c for c in X_labels]) )
            x, y, c = [ r[0] for r in X_train ], [ r[1] for r in X_train ], [ 'blue' if c == labels_found[0] else 'red' for c in X_labels ]
            plt.scatter( x, y, c=c, lw=0)
            prop = FontProperties("Arabic Typesetting")
            test = neigh.decode("utf-8") 
            reshaped_text = arabic_reshaper.reshape(test)
            bidi_text = get_display(reshaped_text)
    
            plt.title('SVM Classification for ' + bidi_text + ' ('+city+')', fontproperties=prop, fontsize = 32 )
            plt.axis('tight')
            #plt.show()
            plt.xlim( 4, 10 )
            plt.ylim( 4, 10 )
            plt.savefig(directory + "/SVM Plots/" + city + "/" + neigh.decode("utf-8") + ".pdf") 
            plt.clf()
        if save_aqar_plots:
            for count, neigh in ranked[:]:
                if neigh in aqar:
                    colors2 = [ 'red', 'blue', 'green', 'orange', 'purple' 'brown', 'yellow', 'lime', 'lightsteelblue', 'darksalmon', 'cyan', 'teal', 'tan', 'slategray' ] + colors
                    labels_found = list( set([c for c in X_labels]) )
                    x, y, c = [ r[0] for r in aqar[neigh] ], [ r[1] for r in aqar[neigh] ], [ 'blue' if r[2] == 'Land' else 'red' for r in aqar[neigh] ]
                    plt.scatter( x, y, c=c, lw=0)
                    prop = FontProperties("Arabic Typesetting")
                    test = neigh.decode("utf-8") 
                    reshaped_text = arabic_reshaper.reshape(test)
                    bidi_text = get_display(reshaped_text)
                    
                    plt.title('Aqar Distribution for ' + bidi_text + ' ('+city+')', fontproperties=prop, fontsize = 32 )
                    plt.axis('tight')
                    #plt.show()
                    plt.xlim( 4, 10 )
                    plt.ylim( 4, 10 )
                    plt.savefig(directory + "/Aqar Plots/" + city + "/" + neigh.decode("utf-8") + ".pdf") 
                    plt.clf()
        
    return data
    # with open(directory + "Results/"+city+" Labels.csv", "w+") as f:
    #     for i, row in enumerate(data):
    #         if i > 0: f.write("\n")
    #         for j, col in enumerate(row):
    #             f.write(col if j==0 else ","+str(col))
    #         if i == 0: f.write(",label")
       
    """
        with open("C:/Users/Zeyad/Desktop/Land Value/Price Clusters/GMM/Riyadh_Mapped_Parcels_New_Zeyad2.csv", "r") as f:
                coordData = [ row.split(',') for row in f.read().splitlines() ]
                coords = { row[7]: (row[26],row[25]) for row in coordData }
        
        
        with open("C:\Users\Zeyad\Desktop\Land Value\Price Clusters\SVM/Labelled Coordinates.csv", "w+") as f:
                f.write("lon,lat,label,probability,log(ppm)")
                for i, row in enumerate(data):
                    if i==0 or row[7] not in coords: continue
                    ppm = float(row[10])
                    ppm = 0 if ppm < 1 else np.log(ppm)
                    if len(row) > 15: 
                        f.write("\n"+coords[row[7]][0]+","+coords[row[7]][1]+","+str(row[-2])+","+str(row[-1])+','+str(ppm) )
                    else: 
                        f.write("\n"+coords[row[7]][0]+","+coords[row[7]][1]+",-1,-1,"+str(ppm))
    """
# CityName = 'Makkah'

# data = np.array(p.read_csv('Data/AfterCleanning.csv'))
# print len(data)
# lands = np.array(p.read_csv('Data/Aqar_website_'+CityName+'_Land_Full_Cleaned.csv',sep='^'))
# villas = np.array(p.read_csv('Data/Aqar_website_'+CityName+'_Villas_Full_Cleaned.csv',sep='^'))
# header = ['Year','Month','Neighborhood','Cat','Type','Plan','Parcel','TID','TotalCost','Area','PPSM','City','Date','NewNeighborhood','MUNC']

# NewData = [header]
# temp = []
# for item in data:
#     temp.append(list(item))
# NewData.extend(temp)
# LabeledTran = CleanMOJUsingSVM(NewData,lands,villas,False,False,CityName)[1:]

# print len(LabeledTran)
# #print len(LabeledTran[0])
# print LabeledTran[1]

