import math as m
import statistics as stats
from itertools import groupby
import matplotlib.pyplot as plt
import numpy as np
#from ROOT import TH2F

from code.Cluster import *

"""
  Input format: evtNb, planeNumber (1,2,3,4), column, line

"""



class CSVReader:
    def __init__(self,csvfilename, verbose=0, masking = False, maskingFile = 'masking.txt'):
        self.verbose = verbose
        self.ifile = open(csvfilename,encoding="ISO-8859-1", errors='ignore')
        self.error_nostr = 0
        self.error_longline = 0
        self.error_format = 0
        #reset pixels and clusters 
        self.pixels = [[],[],[],[]]
        self.clusters = [[],[],[],[]]
        self.evtNb_cur = 0  #current event number
        self.plane_cur = 0  #current plane
        self.masking = masking
        self.masked = {1:[],2:[],3:[],4:[]}
        if masking:
            mfile = open(maskingFile,'r')
            for line in mfile:
                values = [int(i) for i in line.split(',')]
                print(values)
                if len(values)!=3: 
                    print("Issue with the structure of ",maskingFile)
                    continue
                #print("tot",self.masked.get(values[0],[]))
                self.masked[values[0]].append((values[1],values[2]))
        print(self.masked)

    def reportErrors(self):
        print("-----------------------------")
        print("CSVRader - Report error:")
        print("Input not a string:\t",self.error_nostr)
        print("Line too long:\t",self.error_longline)
        print("self.error_format:\t",self.error_format)
        print("-----------------------------")

    def getEventNb(self): return self.evtNb_cur

    def getPixels(self, plane = -1):
        if plane == -1:
            out = []
            for i in range(len(self.pixels)):
                #apply masking
                if self.pixels[i] not in self.masked[plane]:
                    out+=self.pixels[i]
                else:
                    print("It has been masked: ", self.self.pixels[i])
            return out
        if 0<plane<=len(self.pixels):
            return self.pixels[plane-1]
        return []


    def getClusters(self, plane = -1):
        if plane == -1:
            out = []
            for i in range(len(self.clusters)):
                out+=self.clusters[i]
            return out
        if 0<plane<=len(self.clusters):
            return self.clusters[plane-1]
        return []

    def getEventInfo(self):
        print("EvtNb = ",self.evtNb_cur)
        for i in range(len(self.clusters)):
            meanSize = 0
            maxSize = 0  
            nbClusters = len(self.clusters[i])
            if nbClusters>0:
                meanSize = stats.mean([c.size() for c in self.clusters[i]])
                maxSize = max([c.size() for c in self.clusters[i]])
            print("Plane ",i+1,":", nbClusters, " clusters - mean size:", meanSize, "max size:", maxSize) 

    def readEvent(self):

        #reset pixels and clusters 
        #self.pixels = [[],[],[],[]]
        #self.clusters = [[],[],[],[]]
        
        #read file
        ipos = self.ifile.tell()
        print("Enter in function",ipos)
        for line in iter(self.ifile.readline,''):
            if ipos>15000000:
                print(line)
            #a = 0
            #return True
        #return False
            if not isinstance(line, str):
                self.error_nostr+=1
                if self.verbose>0:
                    print("line is not a string !")
                continue
            if len(line)>20:
                self.error_longline+=1
                if self.verbose>0:
                    print("line is anormaly too long !")
                continue
            if len(line.split(','))<4:
                self.error_format+=1
                if self.verbose>0:
                    print("line is not structured properly !")
                continue
            
            #read values:
            evtNb = int(line.split(',')[0])
            plane = int(line.split(',')[1])
            lp = int(line.split(',')[2])
            cp = int(line.split(',')[3])
            
            #apply masking
            #print(self.masked)
            #if self.masking and (lp,cp) in self.masked[plane]: 
            #    print((lp,cp),"should be masked")
            #    continue
        
            if self.evtNb_cur!=evtNb: 
                self.evtNb_cur = evtNb
                self.plane_cur = plane
                #update clusters
                #for all planes
                for iplane in range(1,5):
                    clusters = Clusterizer(self.pixels[iplane-1])
                    for c in clusters:
                        self.clusters[iplane-1].append(Cluster(c))
                #we need to come back to previous line
                #print("pos = ",ipos)
                self.ifile.seek(ipos)
                return True
            
            #update the file position
            ipos = self.ifile.tell()

            if 0<plane<5:
                if (lp,cp) not in self.masked[plane]:
                    self.pixels[plane-1].append((lp,cp))

        return False # end of file
