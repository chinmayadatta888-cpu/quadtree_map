# Delete a place, and shrink the tree back when a region becomes sparse.

from node import CAPACITY


def try_merge(node):
    # If all 4 children are leaves and together they hold CAPACITY places or
    # fewer, pull the places back up and make this node a leaf again.
    total = 0
    for child in node.children:
        if not child.is_leaf():
            return
        total = total + len(child.places)
    if total <= CAPACITY:
        for child in node.children:
            for place in child.places:
                node.places.append(place)
        node.children = []


def delete(node, place):
    # Returns True if the place was removed, False if it was not found.
    # We know the exact coordinates, so we walk straight down to the leaf that
    # holds it instead of searching the whole tree.
    if node.is_leaf():
        for i in range(len(node.places)):
            if node.places[i].place_id == place.place_id:
                node.places.pop(i)
                return True
        return False
    i = node.child_index(place.x, place.y)
    removed = delete(node.children[i], place)
    if removed:
        try_merge(node)     # runs on the way back up, deepest node first
    return removed
