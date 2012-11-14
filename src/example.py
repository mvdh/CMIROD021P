from preparation.model import Point, SunPosition
from preparation.height import RDHeightHandler
from preparation.sun_position import SunPositionHandler
from preparation.shadow import ShadowHandler
import datetime



sw = Point(92314, 437137)
ne = Point(93013, 437489)

start   = datetime.datetime(2012, 9, 23, 9, 45)     # tussen 12
end     = datetime.datetime(2012, 9, 23, 11, 15)    # en 13 uur onze tijd (zomertijd)



##########################
# 1. Store heights in MongoDB

# We only store the heights of a small predefined area with the following coordinates:
# SW: 51.91918506831074, 4.47599932551384   => Rijkdriehoekscoordinaten: x = 92314, y = 437137
# NE: 51.9224257492039, 4.48610320687294    => Rijkdriehoekscoordinaten: x = 93013, y = 437489
##########################

# UNCOMMENT TO RUN:
# height_storage = RDHeightHandler('/media/Orange/rotterdamopendata_hoogtebestandtotaal_oost.csv')
# height_storage.store_heights([[90500, 434250], [95250, 438000]])



###############################################################
# 2. Store elevations and azimuths for a period of time in MongoDB

# We store the elevations and azimuths. It automatically adds 
# steps of 15 minutes.
###############################################################

# UNCOMMENT TO RUN:
# sp      = SunPositionHandler()
# sp.store_sun_positions(start, end)



###############################################################
# 3. Store shadows for 23 September 2012 (10 - 11 uur UTC 0)
###############################################################

# UNCOMMENT TO RUN:
box = [sw, ne]
sh = ShadowHandler()
sh.store_shadows(start, end, box)

