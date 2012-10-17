from pymongo import Connection, GEO2D
import datetime

class HeightStorage():

	def storeHeights(self):
		height_file = "/media/Media/huf.txt"

		db = Connection()['rotterdam']
		db.places.create_index([("loc", GEO2D)], min=0 , max=88101)


		f = open(height_file)
		for a in range(6):
			print f.readline().replace(',', '.').split()

		for y, line in enumerate(f):
			heights = map(float, line.replace(',', '.').split())

			bulk = []
			for x, height in enumerate(heights):
				if (height != -9999):
					bulk.append({'loc': { 'x': x, 'y': y }, 'h' : height })
			db.places.insert(bulk)	

			if y == 5:
				break


class SunPositionStorage():

	def storeSunPositions(self):
		pos_file = "../../out.csv"

		db = Connection()['sun_positions']
		db.positions.create_index('datetime')

		f = open(pos_file)
		f.readline() # skip first line
		for line in f:	
			row = line.split(',')
			year = int(row[1])
			month = int(row[2])
			day = int(row[3])
			hour = int(row[4])
			minute = int(row[5])*15
			az = float(row[6])
			el = float(row[7])

			db.positions.insert({'datetime': datetime.datetime(year, month, day, hour, minute), 'el': el, 'az': az})

		# print db.positions.find({ 'datetime': datetime.datetime(2012, 1, 1, 12, 15)})[0]


a = SunPositionStorage()
a.storeSunPositions()

