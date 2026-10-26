
# Run:  python experiments.py
# These are experiments, not tests: they print tables of numbers that back up
# the claims in the README (the speed-up grows with n, and capacity 4 is a
# sensible choice). Times depend on your computer.

import random
import time
import node
from search import search_with_cost


def pad(text, width):
    return str(text) + " " * (width - len(str(text)))


def make_places(n, seed):
    random.seed(seed)
    places = []
    for i in range(n):
        places.append(node.Place(i, "P", random.random() * 1000, random.random() * 1000))
    return places


def make_windows(how_many, seed):
    # small 20 x 20 windows, like a phone screen on a big map
    random.seed(seed)
    windows = []
    for i in range(how_many):
        x = random.random() * 980
        y = random.random() * 980
        windows.append([x, y, x + 20, y + 20])
    return windows


def build(places):
    root = node.Node(0, 0, 1000, 1000, 0)
    for p in places:
        node.insert(root, p)
    return root


def scaling():
    print("EXPERIMENT 1: does the quadtree keep up as the number of places grows?")
    print("100 searches with a 20 x 20 window on a 1000 x 1000 map")
    print("")
    print(pad("places", 9) + pad("plain loop", 13) + pad("quadtree", 11) + pad("speed-up", 10) +
          pad("found per search", 18) + "nodes looked at per search")
    windows = make_windows(100, 2)
    for n in [10000, 20000, 40000, 80000, 160000]:
        places = make_places(n, 1)
        root = build(places)

        start = time.time()
        found_total = 0
        nodes_total = 0
        for w in windows:
            result, nodes_looked_at, places_checked = search_with_cost(root, w[0], w[1], w[2], w[3])
            found_total = found_total + len(result)
            nodes_total = nodes_total + nodes_looked_at
        quad_time = time.time() - start

        start = time.time()
        loop_total = 0
        for w in windows:
            for p in places:
                if w[0] <= p.x and p.x <= w[2] and w[1] <= p.y and p.y <= w[3]:
                    loop_total = loop_total + 1
        loop_time = time.time() - start

        if loop_total != found_total:
            print("ERROR: the two methods disagree")
            return
        print(pad(n, 9) + pad(str(round(loop_time, 3)) + " s", 13) + pad(str(round(quad_time, 3)) + " s", 11) +
              pad(str(round(loop_time / quad_time)) + "x", 10) + pad(round(found_total / 100, 1), 18) +
              str(round(nodes_total / 100)))
    print("")
    print("The plain loop's time grows in step with n (it checks every place).")
    print("The quadtree's time grows far more slowly: it follows the places it finds")
    print("plus a slowly growing number of nodes looked at.")


def capacity():
    print("EXPERIMENT 2: why capacity 4?")
    print("50,000 places, 100 searches with a 20 x 20 window")
    print("")
    print(pad("capacity", 10) + pad("height", 8) + pad("nodes", 9) + pad("build", 9) + pad("search", 10) +
          pad("nodes looked at", 17) + "places checked")
    places = make_places(50000, 1)
    windows = make_windows(100, 2)
    for c in [1, 2, 4, 16, 64]:
        node.CAPACITY = c           # insert and split read this value every time they run
        start = time.time()
        root = build(places)
        build_time = time.time() - start

        start = time.time()
        nodes_total = 0
        checked_total = 0
        for w in windows:
            result, nodes_looked_at, places_checked = search_with_cost(root, w[0], w[1], w[2], w[3])
            nodes_total = nodes_total + nodes_looked_at
            checked_total = checked_total + places_checked
        search_time = time.time() - start

        print(pad(c, 10) + pad(node.height(root), 8) + pad(node.count_nodes(root), 9) +
              pad(str(round(build_time, 2)) + " s", 9) + pad(str(round(search_time, 3)) + " s", 10) +
              pad(round(nodes_total / 100), 17) + str(round(checked_total / 100)))
    node.CAPACITY = 4               # put it back
    print("")
    print("Capacity 1 or 2: a huge tree (many nodes, lots of memory). Capacity 64: few nodes,")
    print("but every leaf is long to scan (many places checked). Anything from about")
    print("4 to 16 works well. We use 4 because it keeps diagrams and demos small.")


scaling()
print("")
capacity()
