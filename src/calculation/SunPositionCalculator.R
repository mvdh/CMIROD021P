library(data.table)

sunPosition <- function(year, month, day, hour=12, min=0, sec=0, lat=51.923, long=4.482) { # default lat lon to Rotterdam
    
    #################################################################################################################
    #################################################################################################################
    # Source: http://stackoverflow.com/questions/8708048/position-of-the-sun-given-time-of-day-latitude-and-longitude
    #################################################################################################################
    #################################################################################################################

    twopi <- 2 * pi
    deg2rad <- pi / 180

    # Get day of the year, e.g. Feb 1 = 32, Mar 1 = 61 on leap years
    month.days <- c(0,31,28,31,30,31,30,31,31,30,31,30)
    day <- day + cumsum(month.days)[month]
    leapdays <- year %% 4 == 0 & (year %% 400 == 0 | year %% 100 != 0) & 
                day >= 60 & !(month==2 & day==60)
    day[leapdays] <- day[leapdays] + 1

    # Get Julian date - 2400000
    hour <- hour + min / 60 + sec / 3600 # hour plus fraction
    delta <- year - 1949
    leap <- trunc(delta / 4) # former leapyears
    jd <- 32916.5 + delta * 365 + leap + day + hour / 24

    # The input to the Atronomer's almanach is the difference between
    # the Julian date and JD 2451545.0 (noon, 1 January 2000)
    time <- jd - 51545.

    # Ecliptic coordinates

    # Mean longitude
    mnlong <- 280.460 + .9856474 * time
    mnlong <- mnlong %% 360
    mnlong[mnlong < 0] <- mnlong[mnlong < 0] + 360

    # Mean anomaly
    mnanom <- 357.528 + .9856003 * time
    mnanom <- mnanom %% 360
    mnanom[mnanom < 0] <- mnanom[mnanom < 0] + 360
    mnanom <- mnanom * deg2rad

    # Ecliptic longitude and obliquity of ecliptic
    eclong <- mnlong + 1.915 * sin(mnanom) + 0.020 * sin(2 * mnanom)
    eclong <- eclong %% 360
    eclong[eclong < 0] <- eclong[eclong < 0] + 360
    oblqec <- 23.439 - 0.0000004 * time
    eclong <- eclong * deg2rad
    oblqec <- oblqec * deg2rad

    # Celestial coordinates
    # Right ascension and declination
    num <- cos(oblqec) * sin(eclong)
    den <- cos(eclong)
    ra <- atan(num / den)
    ra[den < 0] <- ra[den < 0] + pi
    ra[den >= 0 & num < 0] <- ra[den >= 0 & num < 0] + twopi
    dec <- asin(sin(oblqec) * sin(eclong))

    # Local coordinates
    # Greenwich mean sidereal time
    gmst <- 6.697375 + .0657098242 * time + hour
    gmst <- gmst %% 24
    gmst[gmst < 0] <- gmst[gmst < 0] + 24.

    # Local mean sidereal time
    lmst <- gmst + long / 15.
    lmst <- lmst %% 24.
    lmst[lmst < 0] <- lmst[lmst < 0] + 24.
    lmst <- lmst * 15. * deg2rad

    # Hour angle
    ha <- lmst - ra
    ha[ha < -pi] <- ha[ha < -pi] + twopi
    ha[ha > pi] <- ha[ha > pi] - twopi

    # Latitude to radians
    lat <- lat * deg2rad

    # Azimuth and elevation
    el <- asin(sin(dec) * sin(lat) + cos(dec) * cos(lat) * cos(ha))
    az <- asin(-cos(dec) * sin(ha) / cos(el))

    # For logic and names, see Spencer, J.W. 1989. Solar Energy. 42(4):353
    cosAzPos <- (0 <= sin(dec) - sin(el) * sin(lat))
    sinAzNeg <- (sin(az) < 0)
    az[cosAzPos & sinAzNeg] <- az[cosAzPos & sinAzNeg] + twopi
    az[!cosAzPos] <- pi - az[!cosAzPos]

    # if (0 < sin(dec) - sin(el) * sin(lat)) {
    #     if(sin(az) < 0) az <- az + twopi
    # } else {
    #     az <- pi - az
    # }


    el <- el / deg2rad
    az <- az / deg2rad
    lat <- lat / deg2rad

    return(list(elevation=el, azimuth=az))
}

# Calulate the sun positions over a time period
sunPositionsFromDateRange <- function (startDate, endDate, lat=51.923, long=4.482) {
    # N <- 1e4
    # sunPositions <- data.frame(row.names=c('jaar', 'maand', 'dag', 'uur', 'kwartier_nr', 'azimuth', 'elevation'))
    days <- seq(from=as.Date(startDate), to=as.Date(endDate), by='days')    

    n <- 35136
    sunPositions <- data.table(y=rep(0,n), m=rep(0,n), d=rep(0,n), h=rep(0,n), q=rep(0,n), azimuth=rep(0,n), elevation=rep(0.0,n))

    qTot = 0
    # for each day in year
    for(i in 1:length(days)) {

        curr_day= days[i]
        year = as.numeric(format(curr_day, "%Y"))
        month = as.numeric(format(curr_day, "%m"))
        date = as.numeric(format(curr_day, "%d"))

        # for each hour in day
        for (hour in 0:23) {

            #for each quarter in hour
            for (quarter in 0:3) {
                qTot <- qTot + 1
                minute <- quarter * 15
                position <- sunPosition(year, month, date, hour, min=minute, lat=lat, long=long)
                
                sunPositions[qTot, y := year]
                sunPositions[qTot, m := month]
                sunPositions[qTot, d := date]
                sunPositions[qTot, h := hour]
                sunPositions[qTot, q := quarter]
                sunPositions[qTot, azimuth := position$azimuth]
                sunPositions[qTot, elevation:= position$elevation]
            }
        }
    }
    return (sunPositions)
}


# All Sun positions
sunPositionsDateRange <-sunPositionsFromDateRange('2012-01-01', '2012-12-31', 51.9, 4.5)
# Only store the elevation which >= 4.0
sunPositionsDateRangeReduced <- sunPositionsDateRange[sunPositionsDateRange$elevation >= 4.0,]
# Save to csv file
write.table(sunPositionsDateRangeReduced, "/media/Sandbox/hr/CMIROD021P/out.csv", sep=",", col.names=NA)








