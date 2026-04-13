"""
SiTrInEO - Cluster analysis module for silicon tracker

Produces ROOT histograms for cluster property analysis including:
- Size distribution
- Position dependence (X, Y, R)
- Large cluster properties (orientation, moments, length)

Requires: ROOT, numpy
"""

from ROOT import TH1F, TProfile, TCanvas, TFile, TLegend
import math as m
from code.Cluster import *


class ClusterAna:
    """
    Cluster analysis producing ROOT histograms for silicon tracker data.
    
    Generates:
    - Cluster size distribution (TH1F)
    - Size vs position profiles (TProfile)
    - Large cluster orientation/moments (TH1F)
    """

    def __init__(self, planes=None, largeSize=20, xref=464, yref=480):
        """
        Initialize cluster analyzer.
        
        :param planes: List of plane numbers (default: [1])
        :param largeSize: Threshold for large cluster analysis
        :param xref: Reference X coordinate (sensor center)
        :param yref: Reference Y coordinate (sensor center)
        Note: ROOT plot colors are set equal to plane number
        """
        if planes is None:
            planes = [1]
        self.largeSize = largeSize
        self.xref = xref
        self.yref = yref
        self.planes = planes
        self.cSize = TCanvas("cSize")
        self.cLarge = TCanvas("cLarge")
        
        # Initialize histogram dictionaries
        self.hSize = {}
        self.hSizeVsX = {}
        self.hSizeVsY = {}
        self.hSizeVsR = {}
        self.hTheta = {}
        self.hIxp = {}
        self.hIyp = {}
        self.hLength = {}
        
        for plane in planes:
            # Size histograms
            self.hSize[plane] = TH1F(
                f"hSize_{plane}",
                f"Cluster size plane {plane}",
                30, 0, 30
            )
            
            # Position-dependent profiles
            self.hSizeVsX[plane] = TProfile(
                f"hSizeVsX_{plane}",
                f"Cluster size vs X plane {plane}",
                100, 0, 500
            )
            self.hSizeVsY[plane] = TProfile(
                f"hSizeVsY_{plane}",
                f"Cluster size vs Y plane {plane}",
                100, 0, 500
            )
            self.hSizeVsR[plane] = TProfile(
                f"hSizeVsR_{plane}",
                f"Cluster size vs R plane {plane}",
                100, 0, 450
            )
            
            # Large cluster properties
            self.hTheta[plane] = TH1F(
                f"hTheta_{plane}",
                f"Orientation plane {plane} (>{largeSize}px)",
                20, -m.pi/4, m.pi/4
            )
            self.hIxp[plane] = TH1F(
                f"hIxp_{plane}",
                f"Moment X plane {plane} (>{largeSize}px)",
                50, 0, 200
            )
            self.hIyp[plane] = TH1F(
                f"hIyp_{plane}",
                f"Moment Y plane {plane} (>{largeSize}px)",
                50, 0, 200
            )
            self.hLength[plane] = TH1F(
                f"hLength_{plane}",
                f"Length plane {plane} (>{largeSize}px)",
                50, 0, 20
            )
            
            # Set line color by plane number
            for hist in [self.hSize, self.hSizeVsX, self.hSizeVsY, self.hSizeVsR,
                       self.hTheta, self.hIxp, self.hIyp, self.hLength]:
                hist[plane].SetLineColor(plane)

    def fill(self, plane, cluster):
        """
        Fill histogram with single cluster data.
        
        :param plane: Detector plane number (1-4)
        :param cluster: Cluster object to analyze
        :returns: True if successful, False if plane invalid
        """
        if not self.check(plane):
            return False
        
        # Basic size info
        self.hSize[plane].Fill(cluster.size())
        
        # Position-dependent size
        bc = cluster.getBarycenter()
        self.hSizeVsX[plane].Fill(bc[0], cluster.size())
        self.hSizeVsY[plane].Fill(bc[1], cluster.size())
        self.hSizeVsR[plane].Fill(distance(bc, (self.xref, self.yref)), cluster.size())
        
        # Large cluster properties
        if cluster.size() >= self.largeSize:
            self.hTheta[plane].Fill(cluster.Theta)
            self.hIxp[plane].Fill(cluster.Ixp)
            self.hIyp[plane].Fill(cluster.Iyp)
            self.hLength[plane].Fill(cluster.length)
        
        return True

    def fillMany(self, plane, clusters):
        """
        Fill histograms with multiple clusters.
        
        :param plane: Detector plane number
        :param clusters: List of Cluster objects
        :returns: True if successful, False if plane invalid
        """
        if not self.check(plane):
            return False
        for cluster in clusters:
            self.fill(plane, cluster)
        return True

    def draw(self, export=False):
        """
        Draw histograms to ROOT canvases.
        
        :param export: If True, save as PNG files
        :returns: Tuple of (size_canvas, large_canvas)
        """
        self.cSize.Divide(2, 2)
        self.cLarge.Divide(2, 2)
       
        drawOption = ""
        for plane in self.planes:
            # Size distribution canvas
            self.cSize.cd(1)
            self.hSize[plane].Draw(drawOption)
            self.cSize.cd(2)
            self.hSizeVsR[plane].Draw(drawOption)
            self.cSize.cd(3)
            self.hSizeVsX[plane].Draw(drawOption)
            self.cSize.cd(4)
            self.hSizeVsY[plane].Draw(drawOption)
            self.cSize.Update()
            self.cSize.Draw(drawOption)

            # Large cluster canvas
            self.cLarge.cd(1)
            self.hTheta[plane].Draw(drawOption)
            self.cLarge.cd(2)
            self.hLength[plane].Draw(drawOption)
            self.cLarge.cd(3)
            self.hIxp[plane].Draw(drawOption)
            self.cLarge.cd(4)
            self.hIyp[plane].Draw(drawOption)
            self.cLarge.Draw(drawOption)
            
            drawOption = "same"
    
        if export:
            self.cSize.SaveAs("ClusterSize.png")
            self.cLarge.SaveAs("LargeClusterProperties.png")
        
        return self.cSize, self.cLarge

    def write(self, ofilename="clusterAna.root"):
        """
        Save histograms to ROOT file.
        
        :param ofilename: Output file path
        """
        rfile = TFile(ofilename, "RECREATE")
        rfile.cd()
        for plane in self.planes:
            self.hSize[plane].Write()
            self.hSizeVsX[plane].Write()
            self.hSizeVsY[plane].Write()
            self.hSizeVsR[plane].Write()
            self.hTheta[plane].Write()
            self.hIxp[plane].Write()
            self.hIyp[plane].Write()
            self.hLength[plane].Write()
        self.cLarge.Write()
        self.cSize.Write()
        rfile.Close()

    def check(self, plane):
        """
        Validate plane number.
        
        :param plane: Plane number to check
        :returns: True if valid, False otherwise
        """
        if plane not in self.planes:
            print(f"Plane {plane} not in configured planes: {self.planes}")
            return False
        return True
