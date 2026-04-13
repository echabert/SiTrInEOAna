"""
SiTrInEO - Maps module for silicon tracker hit visualization

Provides 2D mapping classes for hit visualization using matplotlib.
Note: ROOT-based ClusterMap is commented out - use ClusterAna for ROOT histograms.
"""

import math as m
import statistics as stats
import matplotlib.pyplot as plt
import numpy as np

# MIMOSA-28 sensor dimensions
matrix_nc = 928  # columns
matrix_nl = 960  # lines


class ClusterMap:
    """
    Cluster position map (placeholder - ROOT version available via ClusterAna).
    """
    def __init__(self):
        self.data = []


class RawMap:
    """
    2D histogram of raw pixel hits using NumPy array.
    
    Uses efficient NumPy array for O(1) pixel filling.
    Provides matplotlib visualization via plot().
    
    Attributes:
        pixels: 2D array of hit counts (columns x lines)
        overflow: Count of pixels outside sensor bounds
    """

    def __init__(self):
        """
        Initialize empty hit map with sensor dimensions.
        """
        self.pixels = np.zeros((matrix_nc, matrix_nl), dtype=np.int32)
        self.overflow = 0

    def fill(self, pixel):
        """
        Record a single pixel hit.
        
        :param pixel: (column, line) coordinate tuple
        """
        col, line = pixel[0], pixel[1]
        if col >= matrix_nc or line >= matrix_nl:
            self.overflow += 1
            return
        self.pixels[col, line] += 1

    def fillMany(self, pixels):
        """
        Record multiple pixel hits.
        
        :param pixels: List of (column, line) tuples
        """
        for pixel in pixels:
            self.fill(pixel)

    def plot(self):
        """
        Display hit map using matplotlib.
        """
        c = plt.imshow(self.pixels.T, cmap='hot', origin='lower')
        plt.colorbar(c, label='Hit count')
        plt.xlabel('Column')
        plt.ylabel('Line')
        plt.title('Raw Hit Map')
        plt.show()


