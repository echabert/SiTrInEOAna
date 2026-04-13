"""
SiTrInEO - Noise analysis module for silicon tracker sensors

Analyzes noise pixel distribution using ROOT histograms.
Identifies hot/noisy pixels based on hit frequency thresholds.

Requires: ROOT (CERN data analysis framework), NumPy
"""

from ROOT import TH1F, TH2F, TProfile, TCanvas, TFile, TLegend
#import ctypes as c
import numpy as np

# MIMOSA-28 sensor dimensions (pixel matrix)
matrix_nc = 928  # number of columns
matrix_nl = 960  # number of lines


class NoiseAna:
    """
    Noise analysis for SiTrInEO silicon tracker sensors.
    
    Uses ROOT histograms to analyze:
    - Hit occupation maps (TH2F)
    - Rate distribution per pixel (TH1F)
    - Noisy pixel identification
    
    Attributes:
        planes: List of detector plane numbers (1-4)
        noisyThreshold: Hits threshold to classify pixel as noisy
    """

    def __init__(self, planes=None, noisyThreshold=5):
        """
        Initialize noise analyzer for specified detector planes.
        
        :param planes: List of plane numbers (default: [1])
        :param noisyThreshold: Minimum hits to flag as noisy pixel
        """
        if planes is None:
            planes = [1]
        self.noisyThreshold = noisyThreshold
        self.cNoise = TCanvas("cNoise")
        self.map = {}
        self.rate = {}
        self.noisy = {}
        self.planes = planes
        for plane in planes:
            self.map[plane] = TH2F(
                f"rawmap_{plane}",
                f"Raw map plane {plane}",
                matrix_nc, 0, matrix_nc,
                matrix_nl, 0, matrix_nl
            )
            self.rate[plane] = TH1F(
                f"rate_{plane}",
                f"Noise rate plane {plane}",
                20, 0, 20
            )
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
        Analyze noise distribution and identify hot pixels.
        
        Iterates through all sensor pixels to:
        - Fill rate histogram with hit counts
        - Identify noisy pixels exceeding threshold
        """
        for plane in self.planes:
            hist = self.map[plane]
            # Use histogram methods directly instead of nested Python loops
            # GetNonEmptyXbins would be more efficient but this preserves logic
            for i in range(1, hist.GetNbinsX() + 1):
                for j in range(1, hist.GetNbinsY() + 1):
                    count = hist.GetBinContent(i, j)
                    self.rate[plane].Fill(count)
                    if count > self.noisyThreshold:
                        self.noisy[plane].append((i - 1, j - 1))

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
