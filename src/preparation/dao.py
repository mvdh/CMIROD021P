from model import Point, SunPosition, Shadow
from pymongo import Connection, GEO2D
import math

class DaoHeight():

    def __init__(self, scale=1):
        self.col = Connection()['rdam']['height']
        self.bulk = []
        # Py(mongo) can't handle large x and y values,
        # so you can use to create smaller xs and ys.
        # Scale is the power of 10. So scale = 3 would
        # mean scale by 1000
        self.scale = scale

    def create_geo_index(self, min=0, max=1000):
        self.col.create_index([('loc', GEO2D)], min=min , max=max)

    def persist(self, point):
        bson = self.point_to_bson(point)
        self.bulk.append(bson)
        if(len(self.bulk) >= 50000):            
            self.flush()

    def flush(self):
        if(len(self.bulk) > 0):
            self.col.insert(self.bulk)
            print len(self.bulk)
            self.bulk = []

    def find_within_box(self, points):
        box = self.points_to_box(points)
        result = []
        for bson in self.col.find({'loc': {'$within': {'$box': box}}}):
            point = self.bson_to_point(bson)
            result.append(point)
        return result

    def find_within_polygon(self, points):
        polygon = self.points_to_polygon_bson(points)
        result = []
        for bson in self.col.find({'loc': {'$within': {'$polygon': polygon}}}):
            point = self.bson_to_point(bson)
            result.append(point)
        return result

    def points_to_box(self, points):
        p1x = points[0].x / math.pow(10, self.scale)
        p1y = points[0].y / math.pow(10, self.scale)
        p2x = points[1].x / math.pow(10, self.scale)
        p2y = points[1].y / math.pow(10, self.scale)
        box = {
            'a': {'x':p1x, 'y':p1y},
            'b': {'x':p2x, 'y':p2y}
        }
        return box

    def points_to_polygon_bson(self, points):
        result = []
        for point in points:
            bson = self.point_to_polygon_bson(point)
            result.append(bson)
        return result

    def point_to_polygon_bson(self, point):
        x = point.x / math.pow(10, self.scale)
        y = point.y / math.pow(10, self.scale)
        return {'x': x, 'y': y}

    def points_to_bson(self, points):
        result = []
        for point in points:
            bson = self.point_to_bson(point)
            result.append(bson)
        return result     

    def point_to_bson(self, point):
        x = point.x / math.pow(10, self.scale)
        y = point.y / math.pow(10, self.scale)
        z = point.z
        return {'loc': {'x': x, 'y': y}, 'z': z}

    def bson_to_point(self, bson):
        x = bson['loc']['x'] * math.pow(10, self.scale)
        y = bson['loc']['y'] * math.pow(10, self.scale)
        z = bson['z']
        return Point(x, y, z)


class DaoSunPosition():

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

    def find_within_time(self, start_date, end_date):
        result = []
        for bson in self.col.find({ '$and': [
                { 'datetime' : { '$gt': start_date }}, 
                { 'datetime' : { '$lt': end_date }}
            ]}):
            sunpos = SunPosition(bson['az'], bson['el'], bson['datetime'])
            result.append(sunpos)
        return result

class DaoShadow():

    def __init__(self):
        self.col = Connection()['rdam']['shadow']
        self.bulk = []

    def create_index(self):
        self.col.create_index([('loc', GEO2D), ('date_time', 1)])

    def persist(self, shadow):
        bson = self.shadow_to_bson(shadow)
        self.bulk.append(bson)
        if(len(self.bulk) >= 10):            
            self.flush()

    def flush(self):
        self.col.insert(self.bulk)
        self.bulk = []     

    def shadow_to_bson(self, shadow):
        bson = {'loc': {'lat':shadow.lat, 'lon':shadow.lon}, 
                'date_time': shadow.date_time}
        return bson