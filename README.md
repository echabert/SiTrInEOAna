# SiTrInEOAna

Python package to analysis SiTrInEO data produced by the DAQ
It assumes that they are preprocessed by basic TAF functionnalities (in python) to get CSV files

## Requirements
 - ROOT ( tested with 6.30/04)
 - numpy
 - matplotlib

## Functionalities:
 - Read CSV file  - structure: evtNb, plane, pixelx, pixely
 - Create clusters: class Cluster and algo Cluterized
 - Perform a noise analysis - create a list of masked pixels
 - Perform a cluster analysis

## Extensions:
 - Export (selected) clusters [or pixels] in CSV file or in a TTree
 - Fit of maps
 - Alignment
 - Track reconstruction
