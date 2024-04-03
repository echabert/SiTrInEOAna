from code.Reader import *
from code.Maps import *
from code.ClusterAna import *
from code.NoiseAna import *
import ROOT

#app = ROOT.TApplication("app", ROOT.nullptr, ROOT.nullptr)


# list of planes to be read
planes = [1,2,3,4]


# name of the input file (csv format)
#ifilename = 'pixels.csv'
#ifilename = 'newfiles/pixels_run104_source.csv'
#ifilename = 'newfiles/pixels_run107_source_scattering.csv'
#ifilename = 'newfiles/pixels_run106_source_45.csv'
#ifilename = 'newfiles/pixels_run105_source_45.csv'
#ifilename = 'newfiles/pixels_noise.csv'
ifilename = 'data/pixels_run1805_beam.csv'
ifilename = 'data/pixels_run106_source_45.csv'

# read the file using the class CSVReader
reader = CSVReader(ifilename,0,True)

# create instance of analysis classes
#rawMap = RawMap()
clusterAna = ClusterAna(planes)
noiseAna = NoiseAna(planes)


# read the file (loop over the events up to the end of the file)
while reader.readEvent():
    # loop over the planes
    for plane in planes:
        #retrive the pixels and clusters
        pixels = reader.getPixels(plane)
        clusters = reader.getClusters(plane)
        #fill the analysis objects
        clusterAna.fillMany(plane,clusters)
        noiseAna.fillMany(plane,pixels)
        #rawMap.fillMany(pixels)

    #analysis of large clusters
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

#post treatment for drawing - saving and print info
clusterAna.draw(True)
clusterAna.write()
noiseAna.compute()
noiseAna.draw()
noiseAna.getStats()
noiseAna.write()
noiseAna.writeNoisy()
reader.reportErrors()
#rawMap.plot()

