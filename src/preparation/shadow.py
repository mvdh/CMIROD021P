from model import Point
from dao import DaoHeight, DaoSunPosition
from pymongo import Connection
import math
import datetime


class Shadow():

	def __init__(self):
		self._az 		= None		# Azimuth
		self._el 		= None		# Elevation
		self._p 		= None		# Location to calculate shadow for
		self.dao_height	= DaoHeight(scale=3)
		self.dao_sunpos	= DaoSunPosition()

	def store_shadows(self, start_date, end_date, box):
		sun_positions = self.dao_sunpos.find_within_time(start_date, end_date)


		c = 0
		for point in self.dao_height.find_within_box(box):
			self.p = point
			
			for sunpos in sun_positions:
				self.az = sunpos['az']
				self.el = sunpos['el']
			
				print 'datetime: ' + str(sunpos['datetime'])
				if self.has_shadow():
					print 'shadow : yes'
				else:
					print 'shadow : no'

				c += 1
				if c > 100:
					break
			if c > 100:
				break


	def has_shadow(self):
		# Maximum distance a place can give shadow
		# whith a maximum building height in mind.
		max_dist 	= self.max_distance()
		# Furthest point
		end_point 	= self.point_by_angle(self.az, max_dist, self.p)
		# Endpoints of linepolygon
		line 		= self.line_polygon(0.99, end_point)
		# Points found in database within linepolygon

		points 		= self.dao_height.find_within_polygon(line)

		for point in points:
			# Don't use the point which is the same as the location
			if self.p.x == point.x and self.p.y == point.y:
				continue
			if self.prevents_sunlight(point):
				return True
		return False

	def prevents_sunlight(self, p):
		dz = float(p.z - self.p.z)	# Delta z
		distance = self.distance(p) # Distance between location and a point
		if dz <= 0.0 or distance == 0.0:
			return False

		angle = math.degrees(math.atan(dz/distance))

		if angle < self.el:
			return False
		return True

	def distance(self, p):
		'''	Calculate distance between a point and the location 
			class property.'''
		dx = abs(self.p.x - p.x)
		dy = abs(self.p.y - p.y)
		return math.sqrt(dx ** 2.0 + dx ** 2.0)


	def max_distance(self, z=190):
		'''	Returns the maximum distance at which a point can give
			shadow with the given elevation of the sun and the height
			of the heighest point (z).'''
		return z / math.tan(math.radians(self.el))


	def point_by_angle(self, angle, max_dist, p):
		''' Calculates the point with the given azimuth
			and the maximum distance to the location.
			Angle start with North and goes over East.'''
		x = p.x + max_dist * math.sin(math.radians(angle))
		y = p.y + max_dist * math.cos(math.radians(angle))
		return Point(x, y)

	def line_polygon(self, spread, p):
		''' Defines the endpoints of the linepolygon to query the points 
			on.'''
		points = []
		points.append(self.point_by_angle(self.az - 90, spread, self.p))
		points.append(self.point_by_angle(self.az - 90, spread, p))
		points.append(self.point_by_angle(self.az + 90, spread, p))
		points.append(self.point_by_angle(self.az + 90, spread, self.p))
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
	def p(self):
		return self._p

	@p.setter
	def p(self, value):
		self._p = value