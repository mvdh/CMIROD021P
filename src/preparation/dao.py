from model import Point
from pymongo import Connection, GEO2D

class ColHeight():

    def __init__(self, scale=1):
        self.col = Connection()['rdam']['height']
        self.bulk = []
        # Py(mongo) can't handle large x and y values,
        # so you can use to create smaller xs and ys.
        self.scale = scale

    def create_geo_index(self, min=0, max=1000):
        col.create_index([('loc', GEO2D)], min=min , max=max)

    def persist(self, point):
        bson = self.point_to_bson(point)
        self.bulk.append(bson)
        if(len(self.bulk) >= 10000):
            self.flush()

    def flush(self):
        if(len(self.bulk) > 0):
            col.insert(self.bulk)
            self.bulk = []

    def find_within_box(self, points):
        box = self.points_to_bson(points)
        result = []
        for bson in col.find({'loc': {'$within': {'$box': box}}})):
            point = self.bson_to_point(bson)
            result.append(point)
        return result

    def find_whitin_polygon(self, points):
        polygon = self.points_to_bson(points)
        result = []
        for bson in col.find({'loc': {'$within': {'$polygon': polygon}}}):
            point = self.bson_to_point(bson)
            result.append(point)
        return result

    def points_to_bson(self, points):
        result = []
        for point in points:
            bson = self.point_to_bson(point)
            result.append(bson)
        return result     

    def point_to_bson(self, point):
        x = point.x * scale
        y = point.y * scale
        z = point.z
        return {'loc': {'x': x, 'y': y}, 'z': z}

    def bson_to_point(self, bson):
        x = bson['loc']['x'] / scale
        y = bson['loc']['y'] / scale
        z = bson['z']
        return Point(x, y, z)


class ColSunPos():

    def __init__(self):
        self.col = Connection()['rdam']['sunpos']
        self.bulk = []

    def create_datetime_index(self):
        self.col.create_index('datetime')

    def persist(self, sunpos):
        self.bulk.append(sunpos)

    def flush(self):
        self.col.insert(self.bulk)
        self.bulk = []