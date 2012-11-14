class Point():
    
    def __init__(self, x, y, z=None):
        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._z = value            

class SunPosition():
    
    def __init__(self, azimuth, elevation, date_time):
        self._az = azimuth
        self._el = elevation
        self._dt = date_time

    @property
    def az(self):
        return self._az

    @az.setter
    def az(self, value):
        self._az = value

    @property
    def el(self):
        return self._el

    @el.setter
    def el(self, value):
        self._el = value

    @property
    def date_time(self):
        return self._dt

    @date_time.setter
    def date_time(self, value):
        self._dt = value


class Shadow():

    def __init__(self, date_time, lat, lon):
        self._dt = date_time
        self._lat = lat
        self._lon = lon

    @property
    def date_time(self):
        return self._dt

    @date_time.setter
    def date_time(self, value):
        self._dt = value
        
    @property
    def lat(self):
        return self._lat

    @lat.setter
    def lat(self, value):
        self._lat = value

    @property
    def lon(self):
        return self._lon

    @lon.setter
    def lon(self, value):
        self._lon = value        





