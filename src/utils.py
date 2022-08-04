from math import radians, cos, sin, atan2, sqrt
from datetime import date

def distance(lat1, lat2, lon1, lon2):
     
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
      
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
 
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    # Radius of earth in kilometers. Use 3956 for miles
    # r = 6371
    r = 3956
      
    # calculate the result
    return(c * r)

def str_to_date(s: str):
    return date(year=int(s[0:4]), month=int(s[4:6]), day=int(s[6:8]))

def date_to_str(date_param):
    return date_param.strftime('%Y%m%d')