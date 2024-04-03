import math as m
import statistics as stats
from itertools import groupby
import matplotlib.pyplot as plt
import numpy as np
#from ROOT import TH2F
from code.Cluster import *




class CSVReader:
    
    """
      CSVReader is class dedicated the reading of SITRINEO files formated as evtNb, planeNumber (1,2,3,4), column, line
      **readEvent** is the main method to be used in a loop to read all events in the file
      many accessors are defined to retrive pixels or clusters for a given plane in the current event
      additional accessors are defined to get information about the event or the errors during the reading
    """


    def __init__(self,csvfilename, verbose=0, masking = False, maskingFile = 'masking.txt'):
        """ The constructor
        :param str cvsfilename: name of the file (relative path)
            Input format should be: evtNb, planeNumber (1,2,3,4), column, line
        :param int verbose: level of verbosity
        :param bool masking: activate or not the masking of noisy pixels
        :param str maskingFile: name of the file containg the list of masked pixels - structure should be "plane,pixels,pixely"
        """
        self.verbose = verbose
        self.ifile = open(csvfilename,encoding="ISO-8859-1", errors='ignore')
        self.error_nostr = 0
        self.error_longline = 0
        self.error_format = 0
        #reset pixels and clusters 
        self.pixels_tmp = [[],[],[],[]]
        self.clusters_tmp = [[],[],[],[]]
        self.clusters = [[],[],[],[]]
        self.evtNb_cur = 0  #current event number
        self.plane_cur = 0  #current plane
        self.masking = masking
        self.masked = {1:[],2:[],3:[],4:[]}
        if verbose>1:
            print("Read the file",csvfilename)
            print("Use of masking", masking)
            if masking: print("Masking file",maskingFile)
        if masking:
            mfile = open(maskingFile,'r')
            for line in mfile:
                values = [int(i) for i in line.split(',')]
                if verbose>2:
                    print(values)
                if len(values)!=3: 
                    print("Issue with the structure of ",maskingFile)
                    continue
                #print("tot",self.masked.get(values[0],[]))
                self.masked[values[0]].append((values[1],values[2]))
        #print(self.masked)
        self.ipos = self.ifile.tell()
        self.imax = self.ifile.seek(0, 2)
        self.ifile.seek(self.ipos)
        self.needToGoToPreviousLine = False

    def reportErrors(self):
        """
        Print a report list of categorized issues during the reading of the file
        """
        print("-----------------------------")
        print("CSVRader - Report error:")
        print("Input not a string:\t",self.error_nostr)
        print("Line too long:\t",self.error_longline)
        print("self.error_format:\t",self.error_format)
        print("-----------------------------")

    def getEventNb(self): 
        """
        :returns: the current event number
        :rtype: int
        """
        return self.evtNb_cur

    def getPixels(self, plane = -1):
        """
        List of pixels
        :param int plane: the selected plane (1,2,3,4). -1 means all planes
        :returns: the list of pixels for the selected plane(s)
        :rtype: list of (int,int)
        """
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
        """
        List of clusters
        :param int plane: the selected plane (1,2,3,4). -1 means all planes
        :returns: the list of clusters for the selected plane(s)
        :rtype: list of Cluster
        """
        if plane == -1:
            out = []
            for i in range(len(self.clusters)):
                out+=self.clusters[i]
            return out
        if 0<plane<=len(self.clusters):
            return self.clusters[plane-1]
        return []

    def getEventInfo(self):
        """
        Print the main event info
        """
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
        """
        Read the event (all lines related to an event in the csv file
        :returns: True/False (if end of file is finished)
        :rtype: Bool
        """

        ####################################################
        #reset pixels and clusters 
        ####################################################
        self.pixels = [[],[],[],[]]
        self.clusters = [[],[],[],[]]
        
        ####################################################
        #if we need to go to previous line (end of plane pixel info)
        ####################################################
        if self.needToGoToPreviousLine:
            #print(self.ipos,"/",self.imax)
            self.ifile.seek(self.ipos)
        if self.ipos == self.imax:
            return False
        
        ####################################################
        # Loop over lines
        ####################################################
        #for line in iter(self.ifile.readline,''):
        while line := self.ifile.readline():
        
            ####################################################
            # Check if there are issues on the line
            ####################################################
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
            
            
            ####################################################
            #read values:
            ####################################################
            evtNb = int(line.split(',')[0])
            plane = int(line.split(',')[1])
            lp = int(line.split(',')[2])
            cp = int(line.split(',')[3])
           
            #print(evtNb,plane,lp,cp)
        
            if self.evtNb_cur!=evtNb: 
                self.evtNb_cur = evtNb
                self.plane_cur = plane
                #update clusters based on the list of pixels
                #for all planes
                for iplane in range(1,5):
                    clusters = Clusterizer(self.pixels[iplane-1])
                    for c in clusters:
                        self.clusters[iplane-1].append(Cluster(c))
                #we need to come back to previous line
                self.needToGoToPreviousLine = True
                #need to exit
                return True
            else:
                self.needToGoToPreviousLine = False
                #update the file position
                self.ipos = self.ifile.tell()

            if 0<plane<5:
                #update the pixels if not masked
                if (lp,cp) not in self.masked[plane]:
                    self.pixels[plane-1].append((lp,cp))

        return False # end of file
