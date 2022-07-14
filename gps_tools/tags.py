import re

PLACE_TAG = "geo:place"
LANDS_TAG = "geo:native_territory"


def make_openspace_tag(place) -> str:
    place_tag = f'"{PLACE_TAG}={place}"'
    return place_tag


def match_openspace_tag(tag) -> bool:
    return True if re.match(f'^"?{PLACE_TAG}=', tag) else False


def make_lands_tag(place) -> str:
    place_tag = f'"{LANDS_TAG}={place}"'
    return place_tag


def match_lands_tag(tag) -> bool:
    return True if re.match(f'^"?{LANDS_TAG}=', tag) else False
