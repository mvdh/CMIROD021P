from dao import ColHeight
from model import Point
from pymongo import Connection, GEO2D
import math

class RDHeight():
    """ Class to deal with heights in Rijksdriehoekscoordinaten"""

    def __init__(self, zfile):
        self.zfile = zfile # File with x, y and z values

    def store_heights(self, box):
        db = ColHeight(scale=3)
        db.create_geo_index() 

        # Open file
        f = open(self.zfile)
        
        # Skip header
        f.readline()
        for i, line in enumerate(f):
            l = line.split(',')

            x = math.floor(float(l[0]))
            y = math.floor(float(l[1]))
            z = float(l[2].rstrip())
            
            # Only store the height if if it is within the
            # predifined box. 
            if(self.is_within_box(x, y, box)):
                point = Point(x, y, z)
                db.persist(point)

        # Save heights that are not saved yet
        db.flush()

        # Close file
        f.close()

    def is_within_box(self, x, y, box):
        if box[0][0] <= x <= box[1][0] and box[0][1] <= y <= box[1][1]:
            return True