import re

TAGNAME = "geo:place"


def make_openspace_tag(place):
    place_tag = f'"{TAGNAME}={place}"'
    return place_tag


def match_openspace_tag(tag):
    return True if re.match(f'^"?{TAGNAME}=', tag) else False
