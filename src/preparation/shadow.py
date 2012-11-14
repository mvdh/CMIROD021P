import math
from pymongo import Connection
import datetime

class ShadowCalculator():

	def __init__(self):
		self._az = None		# Azimuth
		self._el = None		# Elevation
		self._loc = None	# Location to calculate shadow for

	def hasShadow(self):
		# Maximum distance a place can give shadow
		# whith a maximum building height in mind.
		mD = self.maxDistanceToLocation()
		# Furthest point
		pB = self.pointByAngle(self.az, mD, self.loc.p)
		# Endpoints of linepolygon
		lP = self.linePolygon(0.49, pB)


		db = Connection()['heights']
		points = db.points.find({ "loc" : { "$within" : { "$polygon" : [
			{'x': lP[0].x, 'y': lP[0].y},
			{'x': lP[1].x, 'y': lP[1].y},
			{'x': lP[2].x, 'y': lP[2].y},
			{'x': lP[3].x, 'y': lP[3].y}
		]}}})


		for doc in points:
			print doc['loc']['x'],
			print doc['loc']['y']
			pl = Place(Point(doc['loc']['x'], doc['loc']['y']), doc['h'])
			# Don't use the point which is the same as the location
			if self.loc.p.x == pl.p.x and self.loc.p.y == pl.p.y:
				continue
			if self.preventsSunlight(pl):
				return True
			
		return False

	def preventsSunlight(self, pl):
		dH = float(pl.h - self.loc.h)	# Delta h
		if dH <= 0.0:
			return False

		distance = self.distanceToLocation(pl.p) # Distance between location and a point
		angle = math.degrees(math.atan(dH/distance))

		if angle < self.el:
			return False
		return True

	def distanceToLocation(self, p):
		'''	Calculate distance between a point and the location 
			class property.'''
		dX = abs(self.loc.p.x - p.x)
		dY = abs(self.loc.p.y - p.y)
		return math.sqrt(dX ** 2.0 + dY ** 2.0)


	def maxDistanceToLocation(self, height=190):
		'''	Returns the maximum distance at which a point can give
			shadow with the given elevation of the sun and the height
			of the heighest building.'''
		return height / math.tan(math.radians(self.el))


	def pointByAngle(self, angle, distance, p):
		''' Calculates the point with the given azimuth
			and the maximum distance to the location.
			Angle start with North and goes over East.'''
		x = p.x + distance * math.sin(math.radians(angle))
		y = p.y + distance * math.cos(math.radians(angle))
		return Point(x, y)

	def linePolygon(self, disp, p):
		''' Defines the endpoints of the linepolygon to query the points 
			on.'''
		points = []
		points.append(self.pointByAngle(self.az - 90, disp, self.loc.p))
		points.append(self.pointByAngle(self.az - 90, disp, p))
		points.append(self.pointByAngle(self.az + 90, disp, p))
		points.append(self.pointByAngle(self.az + 90, disp, self.loc.p))
		return points


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
	def loc(self):
		return self._loc

	@loc.setter
	def loc(self, value):
		self._loc = value


class Place():

	def __init__(self, p, h):
		self._p = p
		self._h = h

	@property
	def p(self):
		return self._p

	@p.setter
	def p(self, value):
		self._p = value

	@property
	def h(self):
		return self._h

	@h.setter
	def h(self, value):
		self._h = value		


class Point():

	def __init__(self, x, y):
		self._x = x
		self._y = y

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



# Small Test for local testing
sC = ShadowCalculator()

dbsunpost = Connection()['sun_positions']
c = 0
sC.loc = Place(Point(10, 10), 3)
for doc in dbsunpost.positions.find(
	{ '$and': [
		{ 'datetime' : { '$gt': datetime.datetime(2012, 6, 21) } }, 
		{ 'datetime' : { '$lt': datetime.datetime(2012, 6, 24) } }
	]}):
	c = c + 1

	sC.az = doc['az']
	sC.el = doc['el']

	print 'datetime: ' + str(doc['datetime'])
	print 'el : ' + str(sC.el)
	print 'az : ' + str(sC.az)
	
	if sC.hasShadow():
		print 'shadow : yes'
	else:
		print 'shadow : no'
	print