class ColorRange:

	def __init__(self, nVariations=16):
		self.scale = (-20, 200)
		self.nVariations = nVariations 
		self.n = self.nVariations * 6 + 1 # number of possibilities per base (including base)
		# self.nColors = (256-self.nVariations) * (6*self.nVariations+1)

	def rgbFromScaledHeight(self, scaledheight):
		# Determine the base
		base = int(scaledheight/self.n) 
		# Correct the base, so that it end in white
		base = base + self.nVariations-1
		# Determine the n (in the base) of the possibility
		nPossibility = scaledheight % self.n
		# Determine the variation (zero-based)
		variation = int((nPossibility-1)/6)
		# Het gaat dus om het invullen van getal 'grondgetal' + 'targetVariation' + 1
		variationNumber = base + variation + 1

		# Welke manier? (1,0,0), (0,1,0), etc
		manner = int((nPossibility) % 6)
		if manner == 1:
			return (variationNumber, base, base)
		elif manner == 2:
			return (base, variationNumber, base)
		elif manner == 3:
			return (base, base, variationNumber)
		elif manner == 4:
			return (variationNumber, variationNumber, base)
		elif manner == 5:
			return (variationNumber, base, variationNumber)
		elif manner == 0:
			return (base, variationNumber, variationNumber)


class HeightImageFactory:
	"""docstring for HeightImageFactory"""
	
	def __init__(self):
		self.IMAGE_WIDTH = 4000 #px
		self.IMAGE_HEIGHT = 4000 #px
		self.MAX_HEIGHT = 200.0
		self.MIN_HEIGHT = -20.0

	def createImages():
		columns = math.ceil(float(88101) / IMAGE_WIDTH)
		rows = math.ceil(float(16068) / IMAGE_HEIGHT)

		for ci in range(int(columns)):
			
			# We open the file with heights and skip the first
			# six lines, because they contain header info.
			f = open('/media/Media/huf.txt')
			for a in range(6):
				f.readline()

			for ri in range(int(rows)):
				# init new image and load it's pixels
				img = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT))
				pixels = img.load()

				for li, line in enumerate(f):
					if ci == columns: # last column might not be even wide as the others
						heights = line.replace(',', '.').split()[ci*IMAGE_WIDTH:]
					else:
						heights = line.replace(',', '.').split()[ci*IMAGE_WIDTH:(ci+1)*IMAGE_WIDTH]
					heights = map(float, heights)

					# change every single pixel color, according to it's height
					for pi, height in enumerate(heights):
						if(height > MAX_HEIGHT or height < MIN_HEIGHT):
							pixels[pi, li] = 0	# NO DATA
						else:
							pixels[pi, li] = cR.rgbFromScaledHeight(scale(MAX_HEIGHT, MIN_HEIGHT, 0, 22000, height))

					# Image has reached it's height, so break and start a new image
					if (li == IMAGE_HEIGHT -1):
						break 

				img.save('afbeelding-' + str(ci) + '-' + str(ri) + '.png')

			# Close the file
			f.close()
