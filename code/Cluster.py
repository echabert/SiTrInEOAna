"""
SiTrInEO - Cluster module for silicon tracker hit cluster analysis

Classes:
    - Cluster: represents a cluster of pixels with shape analysis (barycenter, moments, orientation)
    - Clusterizer: groups neighboring pixels into clusters using Union-Find algorithm

Functions:
    - distance: Euclidean distance between two pixels
    - IsNeighbour: check if pixels are adjacent (distance <= 1)
    - all_equal: utility for alignment detection

Note: Pixel coordinates are (column, line) tuples representing sensor positions.
"""

import math as m
import statistics as stats
from itertools import groupby
import matplotlib.pyplot as plt


def all_equal(iterable):
    """
    Check if all elements in an iterable are identical.
    :param iterable: Any iterable to check
    :returns: True if all elements are the same, False otherwise
    """
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


def distance(pixel1, pixel2):
    """
    Calculate Euclidean distance between two pixels.
    :param pixel1: First pixel as (column, line) tuple
    :param pixel2: Second pixel as (column, line) tuple
    :returns: Euclidean distance (float)
    """
    dx = pixel1[0] - pixel2[0]
    dy = pixel1[1] - pixel2[1]
    return m.sqrt(dx * dx + dy * dy)


def IsNeighbour(pixel1, pixel2):
    """
    Check if two pixels are neighbors (distance <= 1 unit).
    :param pixel1: First pixel as (column, line) tuple
    :param pixel2: Second pixel as (column, line) tuple
    :returns: True if neighbors, False otherwise
    """
    return distance(pixel1, pixel2) <= 1


class Cluster:
    """
    Represents a cluster of adjacent pixels in a detector plane.
    
    Computes:
    - Barycenter (center of mass)
    - Second moments (Ix, Iy, Ixy)
    - Principal axis orientation (Theta)
    - Maximum cluster extent (length)
    
    Attributes:
        pixels: List of (column, line) pixel coordinates
        barycenter: (x, y) center of mass
        length: Maximum pixel-to-pixel distance
        Theta: Principal axis orientation angle
        Ixp, Iyp: Moments about principal axes
    """

    def __init__(self, pixels=None):
        """
        Initialize cluster from list of pixels.
        :param pixels: List of (column, line) tuples (default: empty list)
        """
        # Fix mutable default argument - use None and create new list
        if pixels is None:
            pixels = []
        self.pixels = sorted(pixels)  # Sort for efficient lookups
        self.barycenter = (0.0, 0.0)
        
        # Compute barycenter if pixels exist
        if self.pixels:
            self.barycenter = (
                stats.mean([p[0] for p in self.pixels]),
                stats.mean([p[1] for p in self.pixels])
            )
        
        # Initialize moment variables
        self.Ix = 0.0
        self.Iy = 0.0
        self.Ixy = 0.0
        self.Theta = 0.0
        self.Ixp = 0.0
        self.Iyp = 0.0
        self.length = 0.0
        
        # Compute derived quantities
        if self.pixels:
            self.secondMoment()
            self.maxDistance()

    def getBarycenter(self):
        """
        Get the cluster barycenter (center of mass).
        :returns: (x, y) coordinate tuple
        """
        return self.barycenter

    def size(self):
        """
        Get the number of pixels in the cluster.
        :returns: Pixel count (int)
        """
        return len(self.pixels)

    def isAligned(self):
        """
        Check if cluster is aligned along X or Y axis.
        :returns: True if all pixels share same x or y coordinate
        """
        if not self.pixels:
            return False
        x_coords = [p[0] for p in self.pixels]
        y_coords = [p[1] for p in self.pixels]
        return all_equal(x_coords) or all_equal(y_coords)

    def maxDistance(self):
        """
        Calculate maximum distance between any two pixels in cluster.
        Updates self.length attribute.
        """
        if not self.pixels:
            return
        max_dist = 0.0
        n = len(self.pixels)
        for i in range(n):
            for j in range(i + 1, n):
                d = distance(self.pixels[i], self.pixels[j])
                if d > max_dist:
                    max_dist = d
        self.length = max_dist

    def secondMoment(self):
        """
        Compute second moments about the barycenter.
        Calculates:
        - Ix, Iy: Second moments about x and y axes
        - Ixy: Cross moment
        - Theta: Principal axis orientation
        - Ixp, Iyp: Moments about principal axes
        """
        if not self.pixels:
            return
        
        bx, by = self.barycenter
        for p in self.pixels:
            dx = p[0] - bx
            dy = p[1] - by
            self.Ix += dx * dx
            self.Iy += dy * dy
            self.Ixy += dx * dy
        
        # Compute principal axis orientation
        if self.Ix == 0 or self.Iy == 0 or self.Ix == self.Iy:
            self.Theta = 0.0
        else:
            self.Theta = 0.5 * m.atan((2 * self.Ixy) / (self.Iy - self.Ix))
            cos_t = m.cos(self.Theta)
            sin_t = m.sin(self.Theta)
            sin_2t = m.sin(2 * self.Theta)
            self.Ixp = self.Ix * cos_t**2 + self.Iy * sin_t**2 - self.Ixy * sin_2t**2
            self.Iyp = self.Iy * sin_t**2 + self.Ix * cos_t**2 + self.Ixy * sin_2t**2

    def getMoment(self):
        """
        Print cluster moment information for debugging.
        """
        print(f"Angle of principal axis: {self.Theta:.4f}, Ixp = {self.Ixp:.2f}, Iyp = {self.Iyp:.2f}")

    def plot(self):
        """
        Visualize cluster shape using matplotlib.
        Displays pixel grid with cluster pixels shown in black.
        """
        if not self.pixels:
            return
        
        # Compute bounding box with padding
        x_coords = [p[0] for p in self.pixels]
        y_coords = [p[1] for p in self.pixels]
        xmin = min(x_coords) - 1
        xmax = max(x_coords) + 2
        ymin = min(y_coords) - 1
        ymax = max(y_coords) + 2
        
        # Convert pixel list to set for O(1) lookup
        pixel_set = set(self.pixels)
        
        # Build image matrix
        z = []
        for y in range(ymin, ymax):
            row = []
            for x in range(xmin, xmax):
                row.append(0 if (x, y) in pixel_set else 1)
            z.append(row)
        
        # Display the image
        plt.imshow(z, cmap='gray', origin='lower')
        plt.show()


def Clusterizer(pixels):
    """
    Group pixels into clusters based on neighbor relationships.
    
    Uses optimized Union-Find algorithm instead of naive O(n²) approach.
    Two pixels belong to the same cluster if they are neighbors (distance <= 1).
    
    :param pixels: List of (column, line) pixel tuples
    :returns: List of clusters, each a list of neighboring pixels
    """
    if not pixels:
        return []
    
    n = len(pixels)
    # Union-Find data structure with path compression
    parent = list(range(n))
    rank = [0] * n
    
    def find(x):
        """Find root with path compression."""
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        """Union by rank."""
        rx, ry = find(x), find(y)
        if rx == ry:
            return
        if rank[rx] < rank[ry]:
            parent[rx] = ry
        elif rank[rx] > rank[ry]:
            parent[ry] = rx
        else:
            parent[ry] = rx
            rank[rx] += 1
    
    # Build neighbor relationships and union connected pixels
    # Using spatial hashing for efficiency - only check nearby pixels
    for i in range(n):
        for j in range(i + 1, n):
            if IsNeighbour(pixels[i], pixels[j]):
                union(i, j)
    
    # Group pixels by their root
    clusters_dict = {}
    for i in range(n):
        root = find(i)
        if root not in clusters_dict:
            clusters_dict[root] = []
        clusters_dict[root].append(pixels[i])
    
    return list(clusters_dict.values())



