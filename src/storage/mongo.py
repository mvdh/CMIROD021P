from pymongo import Connection, GEO2D


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