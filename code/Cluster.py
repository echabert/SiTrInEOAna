"""
  Classes:
    - Cluster: defined based on a list of pixels a cluster (size & barycenter) 
  Functions:
    - Clusterizer: return a list of clusters based on a list of pixels within a plane
    - all_equal and IsNeighbour: for internal use

"""


import math as m
import statistics as stats
from itertools import groupby
import matplotlib.pyplot as plt
import numpy as np



def all_equal(iterable):
    g = groupby(iterable)
    return next(g, True) and not next(g, False)

def distance(pixel1,pixel2):
    return  m.sqrt(m.pow(pixel1[0]-pixel2[0],2)+m.pow(pixel1[1]-pixel2[1],2))

def IsNeighbour(pixel1,pixel2):
    if distance(pixel1,pixel2) <=1: return True
    return False


class Cluster:
    def __init__(self,pixels=[]):
        self.pixels=pixels
        self.pixels.sort() #pixels are sorted !
        self.barycenter = (0,0)
        if len(pixels)>0:
           self.barycenter = (stats.mean([p[0] for p in pixels]),stats.mean([p[1] for p in pixels])) 
        
        #moments
        self.Ix = 0
        self.Iy = 0
        self.Ixy = 0
        #orientation or principal axes
        self.Theta = 0
        #moments about the principal axes
        self.Ixp = 0
        self.Iyp = 0
        self.secondMoment()
        #distance max between pixels
        self.length = 0
        self.maxDistance()

        

    def barycenter(self):
        return self.barycenter

    def size(self):
        return len(self.pixels)

    def isAligned(self):
        if all_equal([p[0] for p in pixels]) or all_equal([p[1] for p in pixels]): return True
        return False

    #def isSquare(self):


    def maxDistance(self):
        self.lenght = 0
        for i in self.pixels:
            for j in self.pixels:
                d = distance(i,j)
                if d>self.length: self.length = d



    def secondMoment(self):
        self.Ix = 0
        self.Iy = 0
        self.Ixy = 0
        for p in self.pixels:
            self.Ix+=m.pow(p[0]-self.barycenter[0],2)
            self.Iy+=m.pow(p[1]-self.barycenter[1],2)
            self.Ixy+=(p[0]-self.barycenter[0])*(p[1]-self.barycenter[1])
        if self.Ix==0 or self.Iy==0 or self.Ix==self.Iy: self.Theta=0
        else: 
            self.Theta = 0.5*m.atan((2*self.Ixy)/(self.Iy-self.Ix))
            self.Ixp = self.Ix*m.cos(self.Theta)**2+self.Iy*m.sin(self.Theta)**2-self.Ixy*m.sin(2*self.Theta)**2
            self.Iyp = self.Iy*m.sin(self.Theta)**2+self.Iy*m.cos(self.Theta)**2+self.Ixy*m.sin(2*self.Theta)**2

    def getMoment(self):
         print("Angle of principal axis:",self.Theta," Ixp = ",self.Ixp, " Iyp = ",self.Iyp)

    def plot(self):
       if not self.pixels: return
       #define ranges
       xmin = min([p[0] for p in self.pixels])-1
       xmax = max([p[0] for p in self.pixels])+1
       ymin = min([p[1] for p in self.pixels])-1
       ymax = max([p[1] for p in self.pixels])+1
       #fill image
       z = []
       for y in range(ymin,ymax):
           xvalues = []
           for x in range(xmin,xmax):
               if (x,y) in self.pixels: xvalues.append(0)
               else: xvalues.append(1)
           z.append(xvalues)
       
       #draw image with matplolib
       c = plt.imshow(z,cmap='gray')
       plt.show()





def Clusterizer(pixels):
  clusters = []
  for pixel in pixels:
      if len(clusters)==0: 
          clusters.append([pixel])
      else:
          alone = True
          #add the pixel to a cluster if it is a neighbour
          for i,cluster in enumerate(clusters):
              for p in cluster:
                 if IsNeighbour(p,pixel):
                     clusters[i].append(pixel)
                     alone = False
                     break
          #if no neighbour found, it should create a new cluster
          if alone:
              clusters.append([pixel])
  return clusters


