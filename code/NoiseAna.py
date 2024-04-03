from ROOT import TH1F, TH2F, TProfile, TCanvas, TFile, TLegend
#import ctypes as c
import numpy as np

#dimension of the MIMOSA28
matrix_nc = 928
matrix_nl = 960

class NoiseAna:
    """
    Class NoiseAna is using ROOT to perform a noise analysis of SITRINEO sensors
    """

    def __init__(self, planes = [1], noisyThreshold = 5):
        """
        Constructor
        :param list planes: planes could be 1,2,3 or 4
        :param int noisyThreshold: threshold to define a noisy pixels based on the number of events where it was activated (could depends on the acquisition lenght)
        """
        self.noisyThreshold = noisyThreshold
        self.cNoise = TCanvas("cNoise")
        self.map = {}
        self.rate = {}
        self.noisy = {}
        self.planes = planes
        for plane in planes:
            self.map[plane] = TH2F("rawmap"+"_"+str(plane),"Raw map",matrix_nc,0,matrix_nc,matrix_nl,0,matrix_nl)
            self.rate[plane] = TH1F("rate"+"_"+str(plane),"Rate",20,0,20)
            self.noisy[plane] = []

    def fill(self,plane,pixel):
        """
        :param int plane: plane number
        :param (int,int): pixel
        """
        if not self.check(plane): return False
        self.map[plane].Fill(pixel[0],pixel[1])
        return True

    def fillMany(self,plane,pixels):
        """
        :param int plane: plane number
        :param list of (int,int): list of pixels
        """
        if not self.check(plane): return False
        for p in pixels:
            self.fill(plane,p)
        return True

    def compute(self):
        """
        Method which perform the noise analysis
        """
        for plane in self.planes:
            for i in range(self.map[plane].GetNbinsX()+1):
                for j in range(self.map[plane].GetNbinsY()+1):
                    count = self.map[plane].GetBinContent(i,j)
                    self.rate[plane].Fill(count)
                    if count>self.noisyThreshold:
                        print("Really !",(i,j),count)
                        self.noisy[plane].append((i-1,j-1))

    def getStats(self):
        """
        Print some statistical quantities
        """
        proba = np.array([0.5])
        quantiles = np.array([0.])
        for plane in self.planes:
            print("Mean = ",self.rate[plane].GetMean())
            self.rate[plane].GetQuantiles(1,quantiles,proba)
            print("Mediane = ",quantiles[0])

    def writeNoisy(self,ofilename="noisy.txt"):
        """
        Write a file with the noisy pixels
        The structure will be plane,pixelx,pixely
        :param str ofilename: name of the txt file
        """
        ofile = open(ofilename,"w")
        for plane in self.planes:
            for n in self.noisy[plane]:
                ofile.write("{},{},{}\n".format(plane,n[0],n[1]))
        ofile.close()
   
    def draw(self):
        """
        Draw ROOT TCanvas
        """
        self.cNoise.Divide(2,2)
        count = 1
        drawOption = ""
        for plane in self.planes:
            self.cNoise.cd(count)
            count+=1
            self.rate[plane].Draw(drawOption)
            drawOption = "same"

    def write(self,ofilename="noise.root"):
        """
        Write graphe in a root file
        :param str ofilename: name of the root file
        """
        rfile = TFile(ofilename,"RECREATE")
        rfile.cd()
        for plane in self.planes:
            self.rate[plane].Write()
            self.map[plane].Write()
        self.cNoise.Write()
    
    def check(self,plane):
        """
        For internal use
        """
        if plane not in self.planes:
            print("this plane number is not found:", plane)
            return False
        return True
