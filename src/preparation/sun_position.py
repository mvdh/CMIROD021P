from pymongo import Connection, GEO2D
from dao import DaoSunPosition
import datetime
import math

class SunPosition():

    def store_sun_positions(self, start_date, end_date):
        db = DaoSunPosition()
        db.create_datetime_index()

        step = datetime.timedelta(minutes=15)
        while start_date < end_date:
            sp = self.sun_position(start_date)
            if sp['el'] >= 5:
                db.persist({'datetime': start_date, 'el': sp['el'], 'az': sp['az']})
            
            start_date += step
        
        db.flush()


    def sun_position(self, dtime=datetime.datetime.utcnow(), lat=51.923, lon=4.482):
        year    = dtime.year
        month   = dtime.month
        day     = dtime.day
        hour    = dtime.hour
        minute  = dtime.minute
        sec     = dtime.second

        twopi   = 2 * math.pi
        deg2rad = math.pi / 180

        month_days = [0,31,28,31,30,31,30,31,31,30,31,30]
        day = day + self.cumsum(month_days)[month-1]
        if year % 4 == 0 and (year % 400 == 0 or year % 100 != 0) and day >= 60 and not(month == 2 and day == 60): 
            day = day + 1

        # Get Julian date - 2400000
        hour    = hour + minute / 60.0 + sec / 3600.0 # hour plus fraction
        delta   = year - 1949
        leap    = math.trunc(delta / 4) # former leapyears
        jd      = 32916.5 + delta * 365 + leap + day + hour / 24.0
        # print hour, delta, leap, jd

        # The input to the Atronomer's almanach is the difference between
        # the Julian date and JD 2451545.0 (noon, 1 January 2000)
        time = jd - 51545.0

        # Ecliptic coordinates  

        # Mean longitude
        mnlong = 280.460 + 0.9856474 * time
        mnlong = mnlong % 360
        if mnlong < 0:
            mnlong = mnlong + 360
        # print mnlong

        # Mean anomaly
        mnanom = 357.528 + 0.9856003 * time
        mnanom = mnanom % 360
        if mnanom < 0:
            mnanom = mnanom + 360
        mnanom = mnanom * deg2rad
        # print mnanom

        # Ecliptic longitude and obliquity of ecliptic
        eclong = mnlong + 1.915 * math.sin(mnanom) + 0.020 * math.sin(2 * mnanom)
        eclong = eclong % 360
        if eclong < 0:
            eclong = eclong + 360
        oblqec = 23.439 - 0.0000004 * time
        eclong = eclong * deg2rad
        oblqec = oblqec * deg2rad
        # print eclong, oblqec

        # Celestial coordinates
        # Right ascension and declination
        num = math.cos(oblqec) * math.sin(eclong)
        den = math.cos(eclong)
        ra  = math.atan(num / den)
        if den < 0:
            ra = ra + math.pi
        if den >= 0 and num < 0:
            ra = ra + twopi
        dec = math.asin(math.sin(oblqec) * math.sin(eclong))
        # print dec

        # Local coordinates
        # Greenwich mean sidereal time
        gmst = 6.697375 + 0.0657098242 * time + hour
        gmst = gmst % 24.0
        if gmst < 0:
            gmst = gmst + 24.0
        # print gmst

        # Local mean sidereal time
        lmst = gmst + lon / 15.0
        lmst = lmst % 24.0
        if lmst < 0:
            lmst = lmst + 24.0
        lmst = lmst * 15.0 * deg2rad

        # Hour angle
        ha = lmst - ra
        if ha < -math.pi:
            ha = ha + twopi
        if ha > math.pi:
            ha = ha - twopi
        # print ha

        # Latitude to radians
        lat = lat * deg2rad

        # Azimuth and elevation
        el = math.asin(math.sin(dec) * math.sin(lat) + math.cos(dec) * math.cos(lat) * math.cos(ha))
        az = math.asin(-math.cos(dec) * math.sin(ha) / math.cos(el))        
        # print el, az

        # For logic and names, see Spencer, J.W. 1989. Solar Energy. 42(4):353
        cosAzPos = (0 <= math.sin(dec) - math.sin(el) * math.sin(lat))
        sinAzNeg = (math.sin(az) < 0)
        if cosAzPos and sinAzNeg:
            az = az + twopi
        if not cosAzPos:
            az = math.pi - az

        el  = el / deg2rad
        az  = az / deg2rad
        lat = lat / deg2rad

        return dict(el=round(el, 4), az=round(az, 4))

    def cumsum(self, it):
        r = []
        total = 0
        for x in it:
            total += x
            r.append(total)
        return r