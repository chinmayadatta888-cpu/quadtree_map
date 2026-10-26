# Rectangle search, count, the cost of a search, radius search, nearest place.
# The rectangle is (x1, y1) bottom-left to (x2, y2) top-right, edges INCLUDED.

def overlaps(node, x1, y1, x2, y2):
    # False only if the node's region is clearly away from the rectangle.
    # If they just touch along an edge we say True (visiting one extra node is
    # better than missing a place).
    if x2 < node.x0 or x1 > node.x1:
        return False
    if y2 < node.y0 or y1 > node.y1:
        return False
    return True


def collect(node, x1, y1, x2, y2, result, stats):
    # stats is a list of two numbers: stats[0] = nodes looked at,
    # stats[1] = places checked one by one.
    stats[0] = stats[0] + 1
    if not overlaps(node, x1, y1, x2, y2):
        return                          # skip this whole region
    if node.is_leaf():
        for place in node.places:
            stats[1] = stats[1] + 1
            if x1 <= place.x and place.x <= x2 and y1 <= place.y and place.y <= y2:
                result.append(place)
    else:
        for child in node.children:
            collect(child, x1, y1, x2, y2, result, stats)


def search_with_cost(node, x1, y1, x2, y2):
    # Returns three things: the list of places found, how many nodes were
    # looked at, and how many places were checked one by one.
    result = []
    stats = [0, 0]
    collect(node, x1, y1, x2, y2, result, stats)
    return result, stats[0], stats[1]


def search(node, x1, y1, x2, y2):
    # Returns a list of all places inside the rectangle.
    result, nodes_looked_at, places_checked = search_with_cost(node, x1, y1, x2, y2)
    return result


def count(node, x1, y1, x2, y2):
    return len(search(node, x1, y1, x2, y2))


def squared_distance(place, x, y):
    dx = place.x - x
    dy = place.y - y
    return dx * dx + dy * dy


def within_radius(node, cx, cy, r):
    # All places within distance r of the point (cx, cy).
    # Step 1: search the square around the circle (fast, uses the tree).
    # Step 2: keep only the places that are really inside the circle.
    candidates = search(node, cx - r, cy - r, cx + r, cy + r)
    result = []
    for place in candidates:
        if squared_distance(place, cx, cy) <= r * r:
            result.append(place)
    return result


def closest(places, x, y):
    # The place in a non-empty list that is closest to (x, y).
    best = places[0]
    best_d = squared_distance(best, x, y)
    for place in places:
        d = squared_distance(place, x, y)
        if d < best_d:
            best = place
            best_d = d
    return best


def nearest(node, x, y):
    # The place closest to (x, y), or None if the tree is empty.
    # Search a small square around the point and double it until something is
    # found. The closest place INSIDE the square is not always the true
    # closest (a place just outside a corner can be nearer), so we search once
    # more with a square as wide as the distance we found.
    h = (node.x1 - node.x0) / 100
    limit = abs(x - node.x0) + abs(x - node.x1) + abs(y - node.y0) + abs(y - node.y1)
    while True:
        found = search(node, x - h, y - h, x + h, y + h)
        if len(found) > 0:
            best = closest(found, x, y)
            d = squared_distance(best, x, y) ** 0.5
            if d <= h:
                return best             # the circle of radius d fits in the square
            e = d * 1.001               # a hair wider, so rounding cannot drop the place
            found = search(node, x - e, y - e, x + e, y + e)
            return closest(found, x, y)
        if h > limit:
            return None                 # the whole map was searched: nothing stored
        h = h * 2
