from tempProfile import tempProfile
from densityProfile import densityProfile
from salinityProfile import salinityProfile
import numpy as np
import gsw as gsw
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import os
import pickle

def profilePlotter(x,y,line,depths,variable,lat,lon,path):
    plt.plot(x,y)
    plt.ylim(500,0)
    plt.axhline(line)
    for i in depths:
        #Make random markers with labels
        plt.plot(x[i[0]],y[i[0]],'ro')
    plt.xlabel("Densities (kg/m^3)")
    plt.ylabel("Pressures (dbar)")
    plt.title(str("lat : "+lat+
                "lon : "+lon+
                "path :  "+path + "  mlt: " + path))
    plt.show()
out = []
for file in os.listdir("profiles"):
    if file.endswith(".nc"):
        filename = os.path.join("profiles", file)
        dataset = Dataset(filename)
        cycleNumber = dataset.variables["CYCLE_NUMBER"][:][0]
        pressures = dataset.variables["PRES"][:][0]
        salts = dataset.variables["PSAL"][:][0]
        temps = dataset.variables["TEMP"][:][0]

        pressuresa = dataset.variables["PRES_ADJUSTED"][:][0]
        saltsa = dataset.variables["PSAL_ADJUSTED"][:][0]
        tempsa = dataset.variables["TEMP_ADJUSTED"][:][0]

        if pressuresa[0] <99999:
            pressures =pressuresa
            salts = saltsa
            temps = tempsa
        if np.where(np.where(pressures) ==99999)[0]<5:
            print("well shucks")
        else:
            tempsOut=[]
            pressuresOut=[]
            densitiesOut=[]
            for index in range(len(pressures)):
                if pressures[index] != "_":
                    pres = pressures[index]
                    psal = salts[index]
                    temp = temps[index]
                    temp = gsw.conversions.CT_from_t(psal,temp,pres)
                    tempsOut.append(temp)
                    pressuresOut.append(float(pres))
                    densitiesOut.append(float(gsw.sigma0(psal,temp)))
            #temps = tempsOut
            densities = densitiesOut
            pressuress = pressuresOut
            salinities = salts
            #b = densityProfile(densitiesOut,ps)
            line = {}
            t = tempProfile(pressures,temps)
            line["tempAlgo"] = t.findMLD()
            num = ""
            for i in dataset.variables["PLATFORM_NUMBER"][:][0]:
                if len(str(i)) >= 4:
                    num+=str(i)[2]
            line["platformNumber"] = num 
            s = salinityProfile(pressures,temps,salinities,densities)
            line["salinityAlgo"] = s.findMLD()
            d = densityProfile(pressures,temps,salts,densities,sp=s)
            line["densityAlgo"] = d.findMLD()
            line["tempThreshold"] = t.TTMLDPressure
            line["tempGradient"] = t.DTMPressure
            line["densityThreshold"] = d.DThresholdPressure 
            line["densityGradient"] = d.DGradientThresholdPressure
            line["cycleNumber"] = cycleNumber
            line["debug"] = t.debug
            out.append(line)
            #print(s)k
            #profilePlotter(salinities,pressures,s.foundMLD,s.importantDepths(),"Salinities",
                #str(dataset.variables["LATITUDE"][0]),
                #str(dataset.variables["LONGITUDE"][0]),
                #str(s.path)
                #)
            #print(d)
            #profilePlotter(densities,pressures,d.foundMLD,d.importantDepths(),"Densities",
                #str(dataset.variables["LATITUDE"][0]),
                #str(dataset.variables["LONGITUDE"][0]),
                #str(d.path)
            #)
with open("pyOutput.pickle","wb") as f:
    pickle.dump(out,f)
