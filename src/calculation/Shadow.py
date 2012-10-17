import math
from pymongo import Connection

class GeoQuerier():

	def getElAz(self, datetime):
		# Get from database
		return (30, 225) # Dynamic

	def hasShadow(self):

		ElAz = self.getElAz(0)
		maxDist = self.maxDistance(ElAz[0], 10)

		pA = Point(10, 10) # Dynamic
		plA = Place(pA, 1)
		pB = self.pointByAzimuth(ElAz[1], maxDist, pA)

		line = self.linePolygon(ElAz[1], 0.49, pA, pB)

		db = Connection()['heights']
		pointsInLine = db.points.find({ "loc" : { "$within" : { "$polygon" : [
			{'x': line[0].x, 'y': line[0].y},
			{'x': line[1].x, 'y': line[1].y},
			{'x': line[2].x, 'y': line[2].y},
			{'x': line[3].x, 'y': line[3].y}
		]}}})

		for p in pointsInLine:
			if p['loc']['x'] == plA.p.x and p['loc']['y'] == plA.p.y:
				continue

			pl = Place(Point(p['loc']['x'], p['loc']['y']), p['h'])
			if self.preventsSunlight(plA, pl, ElAz[0]):
				return True
			
		return False

	def preventsSunlight(self, plA, plB, el):
		dH = float(plB.h - plA.h)
		if dH <= 0.0:
			return False

		dist = self.pointDist(plA.p, plB.p)
		angle = float(math.degrees(math.atan(dH/dist)))

		if angle < el:
			return False

		return True

	def pointDist(self, pA, pB):
		# Calculate distance between points
		dX = abs(pA.x - pB.x)
		dY = abs(pA.y - pB.y)

		return math.sqrt(dX ** 2.0 + dY ** 2.0)

	# Returns the maximum distance a point can give
	# shadow with the given elevation of the sun
	def maxDistance(self, el, height=180):
		return height / math.tan(math.radians(el))

	# Calculates the point with the given azimuth
	# and the maximum distance
	def pointByAzimuth(self, az, dist, p):
		x = p.x + dist * math.sin(math.radians(az))
		y = p.y + dist * math.cos(math.radians(az))
		return Point(x, y)

	def linePolygon(self, az, disp, pA, pB):
		points = []
		points.append(self.pointByAzimuth(az - 90, disp, pA))
		points.append(self.pointByAzimuth(az - 90, disp, pB))
		points.append(self.pointByAzimuth(az + 90, disp, pB))
		points.append(self.pointByAzimuth(az + 90, disp, pA))
		return points


class Place():

	def __init__(self, p, h):
		self._p = p
		self.h = h

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


gQ = GeoQuerier()
gQ.isShadow()	