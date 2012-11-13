from pymongo import Connection, GEO2D
import math

class RDHeight():
    """ Class to deal with heights in Rijksdriehoekscoordinaten"""

    def __init__(self, zfile):
        self.zfile = zfile # File with x, y and z values

    def store_heights(self, box):
        db      = 'rdam'
        coll    = 'heights'

        # Make connection with the database
        db = Connection()[db]
        db[coll].create_index([("loc", GEO2D)], min=0 , max=1000)
        
        # Use bulk insert to insert a lot of heights at once.
        bulk = []

        # Open file
        f = open(self.zfile)
        
        # Skip header
        f.readline()
        for i, line in enumerate(f):
            l = line.split(',')

            # Py(mongo) can't handle large x and y values,
            # so divide by 1000 to get smaller values.
            x = math.floor(float(l[0]))/1000.0
            y = math.floor(float(l[1]))/1000.0
            z = float(l[2].rstrip())
            
            # Only store the height if if it is within the
            # predifined box. 
            if(self.is_within_box(x*1000, y*1000, box)):
                bulk.append({'loc': { 'x': x, 'y': y }, 'z' : z })
                if(len(bulk) >= 5000):
                    # Store x, y, z in mongo
                    db[coll].insert(bulk)
                    bulk = []

        # Save heights that are not saved yet
        if(len(bulk) > 0):
            db[coll].insert(bulk)

        # Close file
        f.close()

    def is_within_box(self, x, y, box):
        if box[0][0] <= x <= box[1][0] and box[0][1] <= y <= box[1][1]:
            return True