import geopy
from geopy.geocoders import Nominatim
# from geopy.extra.rate_limiter import RateLimiter

def get_loc(coords):
    locator = Nominatim(user_agent="UCHS")
    # coords = "22.516085,88.388869"
    location = locator.reverse(coords, timeout=10)
    if "error" in location.raw.keys():
        print("Geocoding error")
        location = None
    return location