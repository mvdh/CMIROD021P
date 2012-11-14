from dao import DaoHeight, DaoSunPosition, DaoShadow
from model import Point, Shadow
from pymongo import Connection
from util import rd2wgs
import math
import datetime


class ShadowHandler():

	def __init__(self):
		self._az 		= None		# Azimuth
		self._el 		= None		# Elevation
		self._p 		= None		# Location to calculate shadow for
		self.dao_height	= DaoHeight(scale=3)
		self.dao_sunpos	= DaoSunPosition()
		self.dao_shadow	= DaoShadow()

	def store_shadows(self, start_date, end_date, box):
		self.dao_shadow.create_index()
		sun_positions = self.dao_sunpos.find_within_time(start_date, end_date)
		points = self.dao_height.find_within_box(box)


		for i, point in enumerate(points):
			self.p = point
			
			for sun_pos in sun_positions:
				self.az = sun_pos.az
				self.el = sun_pos.el
			
				if self.has_shadow():		
					latlon = rd2wgs.rd2wgs(point.x, point.y)

					shadow = Shadow(sun_pos.date_time, latlon[0], latlon[1])
					self.dao_shadow.persist(shadow)

			print 'remaining points: ',
			print len(points) - i

	def has_shadow(self):
		# Maximum distance a place can give shadow
		# whith a maximum building height in mind.
		max_dist 	= self.max_distance()
		# Furthest point
		end_point 	= self.point_by_angle(self.az, max_dist, self.p)
		# Endpoints of linepolygon
		line 		= self.line_polygon(0.75, end_point)
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