from code.Reader import *
from code.Maps import *
from code.ClusterAna import *
from code.NoiseAna import *
import ROOT

#app = ROOT.TApplication("app", ROOT.nullptr, ROOT.nullptr)

    
planes = [1,2,3,4]

ifilename = 'pixels.csv'
ifilename = 'newfiles/pixels_run104_source.csv'
ifilename = 'newfiles/pixels_run107_source_scattering.csv'
ifilename = 'newfiles/pixels_run106_source_45.csv'
ifilename = 'newfiles/pixels_run105_source_45.csv'
ifilename = 'newfiles/pixels_run1805_beam.csv'
ifilename = 'newfiles/pixels_noise.csv'

reader = CSVReader(ifilename,0,True)

#rawMap = RawMap()
clusterAna = ClusterAna(planes)
noiseAna = NoiseAna(planes)

while reader.readEvent():
    for plane in planes:
        pixels = reader.getPixels(plane)
        clusters = reader.getClusters(plane) 
        clusterAna.fillMany(plane,clusters)
        noiseAna.fillMany(plane,pixels)
        #rawMap.fillMany(pixels)
    """
    if len(reader.getClusters(1))>30:
        clusters = reader.getClusters(1)
        for c in clusters:
            #if c.size()>20:
            #    c.getMoment()
            #    print(c.length)
            #    c.plot()
        reader.getEventInfo()
    """
clusterAna.draw(True)
clusterAna.write()
#rawMap.plot()
noiseAna.compute()
noiseAna.draw()
noiseAna.getStats()
noiseAna.write()
noiseAna.writeNoisy()
reader.reportErrors()

