import math as m
import statistics as stats
import matplotlib.pyplot as plt
import numpy as np

#dimension of the MIMOSA28
matrix_nc = 928
matrix_nl = 960

class ClusterMap:
    def __init__(self):
        data = []
        #rplot = TH2F("clusterMap","",928,0,928,960,0,960)
    '''
    def rfill(self,cluster):
        rplot.Fill(cluster.barycenter)

    def rplot(self):
        rplot.Draw()
    '''

class RawMap:
    def __init__(self):
        #960 columns by 928 lines
        self.pixels = np.zeros([matrix_nc,matrix_nl],dtype=int)
        self.overflow = 0

    def fill(self, pixel):
        if pixel[0]>matrix_nc or pixel[1]>matrix_nl:
            self.overflow+=1
            #print("error in pixel position:",pixel)
            return
        self.pixels[pixel[0]][pixel[1]]+=1
        #print("fill = ",np.count_nonzero(self.pixels))


    def fillMany(self, pixels):
        for pixel in pixels:
            self.fill(pixel)

    def plot(self):
       #draw image with matplolib
       c = plt.imshow(self.pixels)#,cmap='gray', vmin=1,vmax=100)
       plt.colorbar(c) 
       plt.show()


