from ROOT import TH1F, TProfile, TCanvas, TFile, TLegend
import math as m
from code.Cluster import *

class ClusterAna:
    """
    Class ClusterAna produced ROOT histograms for cluster analysis
    """

    def __init__(self, planes = [1], largeSize = 20, xref = 464, yref = 480):
        """ Constructor
        :param list[int] planes: list of planes (1,2,3 or 4)
        :param int largeSize: threshold to define what is a large cluster
        :param int xref: x-center of sensor plane
        :param int yref: y-center of the sensor plane
        Remark: assume that root color plots = plane number
        """
        self.largeSize = largeSize
        self.xref = xref
        self.yref = yref
        self.planes = planes
        self.cSize = TCanvas("cSize")
        self.cLarge = TCanvas("cLarge")
        self.hSize = {}
        self.hSizeVsX = {}
        self.hSizeVsY = {}
        self.hSizeVsR = {}
        self.hTheta = {}
        self.hIxp = {}
        self.hIyp = {}
        self.hLength = {}
        for plane in planes:
            self.hSize[plane] = TH1F("hSize"+"_"+str(plane),"Cluster size",30,0,30)
            self.hSizeVsX[plane] = TProfile("hSizeVsX"+"_"+str(plane),"Cluster size as function of x",100,0,500)
            self.hSizeVsY[plane] = TProfile("hSizeVsY"+"_"+str(plane),"Cluster size as function of y",100,0,500)
            self.hSizeVsR[plane] = TProfile("hSizeVsR"+"_"+str(plane),"Cluster size as function of r",100,0,450)
            self.hTheta[plane] = TH1F("hTheta"+"_"+str(plane),"Orientation for clusters >"+str(largeSize)+" pixels",20,-m.pi/4,m.pi/4)
            self.hIxp[plane] = TH1F("hIxp"+"_"+str(plane),"Moment - x-axis for clusters >"+str(largeSize)+" pixels",50,0,200)
            self.hIyp[plane] = TH1F("hIyp"+"_"+str(plane),"Moment - y-axis for clusters >"+str(largeSize)+" pixels",50,0,200)
            self.hLength[plane] = TH1F("hLength"+"_"+str(plane),"Length for clusters >"+str(largeSize)+" pixels",50,0,20)

            #set line color
            self.hSize[plane].SetLineColor(plane)
            self.hSizeVsX[plane].SetLineColor(plane)
            self.hSizeVsY[plane].SetLineColor(plane)
            self.hSizeVsR[plane].SetLineColor(plane)
            self.hTheta[plane].SetLineColor(plane)
            self.hIxp[plane].SetLineColor(plane)
            self.hIyp[plane].SetLineColor(plane)
            self.hLength[plane].SetLineColor(plane)

    def fill(self,plane, cluster):
        """
        Fill one cluster for a givne plane
        :param int plane: value of 1,2,3 or 4
        :param Cluster cluster: fill a given cluster
        """
        if not self.check(plane): return False
        self.hSize[plane].Fill(cluster.size())
        #print(self.hSize[plane].GetEntries(),plane)
        self.hSizeVsX[plane].Fill(cluster.barycenter[0],cluster.size())
        self.hSizeVsY[plane].Fill(cluster.barycenter[1],cluster.size())
        self.hSizeVsR[plane].Fill(distance(cluster.barycenter,(self.xref,self.yref)),cluster.size())
        #treatment for large clusters
        if cluster.size()>=self.largeSize:
            self.hTheta[plane].Fill(cluster.Theta)
            self.hIxp[plane].Fill(cluster.Ixp)
            self.hIyp[plane].Fill(cluster.Iyp)
            self.hLength[plane].Fill(cluster.length)
        return True

    def fillMany(self, plane, clusters):
        """
        Fill many clusters for a givne plane
        :param int plane: value of 1,2,3 or 4
        :param list[Clusters] clusters: fill a list of cluster
        """
        if not self.check(plane): return False
        for cluster in clusters:
            self.fill(plane,cluster)
        return True


    def draw(self, export=False):
        """
        Draw TCanvas
        :param bool export: if export is True, create 2 png file (ClusterSize.png and LargeClusterProperties.png")
        """
        self.cSize.Divide(2,2)
        self.cLarge.Divide(2,2)
       
        drawOption = ""
        for plane in self.planes:
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
            self.cLarge.SaveAs("LargeCluserProperties.png")
        
        return self.cSize, self.cLarge


    def write(self,ofilename="clusterAna.root"):
        """
        Save info in a root file
        :param str ofilename: name of the exported root file
        """
        rfile = TFile(ofilename,"RECREATE")
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

    def check(self,plane):
        """
        Function of internal use. Check if the plane is found
        """
        if plane not in self.planes:
            print("this plane number is not found:", plane)
            return False
        return True
