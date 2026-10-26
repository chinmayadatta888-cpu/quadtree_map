# MEMBER 3
# Checks the whole project. Run:  python test.py
# Every line starts with PASS or FAIL. The last line tells you the result.

import random
import time
from node import Node, Place, insert, height, count_nodes, CAPACITY, MAX_DEPTH
from search import search, count, search_with_cost, within_radius, nearest, squared_distance
from delete import delete

problems = []


def check(condition, message):
    if condition:
        print("PASS: " + message)
    else:
        print("FAIL: " + message)
        problems.append(message)


def ids_of(places):
    ids = []
    for p in places:
        ids.append(p.place_id)
    ids.sort()
    return ids


def brute_search(all_places, x1, y1, x2, y2):
    # the slow, obviously correct way: look at every place
    result = []
    for p in all_places:
        if x1 <= p.x and p.x <= x2 and y1 <= p.y and p.y <= y2:
            result.append(p)
    return result


def leaves_are_valid(node):
    # Every leaf must hold at most CAPACITY places (unless it is at MAX_DEPTH),
    # and every place must lie inside its leaf's region.
    if node.is_leaf():
        if node.depth < MAX_DEPTH and len(node.places) > CAPACITY:
            return False
        for p in node.places:
            if p.x < node.x0 or p.x > node.x1 or p.y < node.y0 or p.y > node.y1:
                return False
        return True
    if len(node.places) != 0:
        return False
    for child in node.children:
        if not leaves_are_valid(child):
            return False
    return True


def fully_merged(node):
    # After deletions, no internal node may be left whose 4 children are all
    # leaves holding CAPACITY places or fewer in total (it should have merged).
    if node.is_leaf():
        return True
    all_leaves = True
    total = 0
    for child in node.children:
        if child.is_leaf():
            total = total + len(child.places)
        else:
            all_leaves = False
    if all_leaves and total <= CAPACITY:
        return False
    for child in node.children:
        if not fully_merged(child):
            return False
    return True


# ---- 1. the example from the problem statement ----
root = Node(0, 0, 100, 100, 0)
insert(root, Place(1, "Cafe_A", 10, 20))
insert(root, Place(2, "Pizza_B", 80, 90))
insert(root, Place(3, "Dosa_C", 15, 25))
p4 = Place(4, "Biryani_D", 60, 40)
insert(root, p4)
check(ids_of(search(root, 0, 0, 30, 30)) == [1, 3], "search (0,0)-(30,30) finds Cafe_A and Dosa_C")
check(count(root, 50, 30, 100, 100) == 2, "count (50,30)-(100,100) is 2")
check(delete(root, Place(3, "Dosa_C", 15, 25)) == True, "delete Dosa_C")
check(ids_of(search(root, 0, 0, 30, 30)) == [1], "search again finds only Cafe_A")

# ---- 2. corners and dividing lines ----
root = Node(0, 0, 100, 100, 0)
spots = [[0, 0], [100, 0], [0, 100], [100, 100], [50, 50], [50, 0], [0, 50], [100, 50], [50, 100]]
for i in range(len(spots)):
    insert(root, Place(i, "C", spots[i][0], spots[i][1]))
check(count(root, 0, 0, 100, 100) == 9, "all 9 corner and dividing-line places are found")
found_all = True
for i in range(len(spots)):
    if ids_of(search(root, spots[i][0], spots[i][1], spots[i][0], spots[i][1])) != [i]:
        found_all = False
check(found_all, "each corner / dividing-line place can be found on its own")
check(leaves_are_valid(root), "tree structure is valid")

# ---- 3. 60 places with exactly the same coordinates ----
root = Node(0, 0, 100, 100, 0)
for i in range(60):
    insert(root, Place(i, "Same", 33.3, 66.6))
check(count(root, 33.3, 66.6, 33.3, 66.6) == 60, "60 identical places are all found")
check(height(root) <= MAX_DEPTH, "tree height stays within MAX_DEPTH (no endless splitting)")
check(leaves_are_valid(root), "tree structure is valid")

# ---- 4. different rectangles ----
root = Node(0, 0, 100, 100, 0)
insert(root, Place(1, "A", 10, 10))
insert(root, Place(2, "B", 90, 90))
check(count(root, 0, 0, 100, 100) == 2, "rectangle = whole map")
check(count(root, -500, -500, 500, 500) == 2, "rectangle bigger than the map")
check(count(root, 200, 200, 300, 300) == 0, "rectangle completely outside the map")
check(count(root, 100, 100, 150, 150) == 0, "rectangle touching only the map corner, nothing there")
check(ids_of(search(root, 10, 10, 10, 10)) == [1], "single-point rectangle")
check(count(root, 10.5, 10.5, 11, 11) == 0, "tiny empty rectangle")
check(count(root, 0, 0, 10, 10) == 1, "place exactly on the rectangle edge is included")
insert(root, Place(3, "C", 100, 100))
check(count(root, 100, 100, 150, 150) == 1, "place on the map corner is found by a rectangle starting at that corner")

# ---- 5. empty tree and deleting ----
root = Node(0, 0, 10, 10, 0)
check(count(root, 0, 0, 10, 10) == 0, "empty tree: count is 0")
check(search(root, 0, 0, 10, 10) == [], "empty tree: search gives an empty list")
p = Place(1, "A", 5, 5)
insert(root, p)
check(delete(root, p) == True, "delete an existing place")
check(delete(root, p) == False, "delete the same place twice gives False")
check(count(root, 0, 0, 10, 10) == 0, "tree is empty again")

# ---- 6. random test: tree and brute force must always agree ----
random.seed(5)
root = Node(0, 0, 100, 100, 0)
all_places = []
next_id = 0
same_answers = True
for step in range(6000):
    if random.randint(1, 10) <= 7 or len(all_places) == 0:
        # whole-number coordinates put many places on dividing lines
        p = Place(next_id, "P", random.randint(0, 100), random.randint(0, 100))
        next_id = next_id + 1
        insert(root, p)
        all_places.append(p)
    else:
        pos = random.randint(0, len(all_places) - 1)
        if delete(root, all_places[pos]) == False:
            same_answers = False
        all_places.pop(pos)
    if step % 50 == 0:
        a = random.randint(0, 100)
        b = random.randint(0, 100)
        c = random.randint(0, 100)
        d = random.randint(0, 100)
        x1 = a
        x2 = c
        if c < a:
            x1 = c
            x2 = a
        y1 = b
        y2 = d
        if d < b:
            y1 = d
            y2 = b
        if ids_of(search(root, x1, y1, x2, y2)) != ids_of(brute_search(all_places, x1, y1, x2, y2)):
            same_answers = False
        if count(root, x1, y1, x2, y2) != len(brute_search(all_places, x1, y1, x2, y2)):
            same_answers = False
check(same_answers, "6000 random inserts/deletes: quadtree always matches the plain loop")
check(leaves_are_valid(root), "tree structure is valid after the random test")
check(fully_merged(root), "no sparse region was left unmerged after the random deletes")

# ---- 7. deleting shrinks the tree back (merge) ----
root = Node(0, 0, 100, 100, 0)
batch = []
for i in range(40):
    p = Place(i, "M", (i * 7) % 100, (i * 13) % 100)
    insert(root, p)
    batch.append(p)
check(count_nodes(root) > 1, "40 places made the tree split")
for i in range(0, 40, 2):
    delete(root, batch[i])
check(fully_merged(root), "after deleting half, no sparse region is left unmerged")
check(leaves_are_valid(root), "tree structure is valid after deleting half")
for i in range(1, 40, 2):
    delete(root, batch[i])
check(root.is_leaf() and count_nodes(root) == 1, "after deleting everything the tree is a single leaf again")

# ---- 8. the cost counters ----
random.seed(3)
root = Node(0, 0, 1000, 1000, 0)
all_places = []
for i in range(20000):
    p = Place(i, "C", random.random() * 1000, random.random() * 1000)
    insert(root, p)
    all_places.append(p)
found, nodes_looked_at, places_checked = search_with_cost(root, 400, 400, 420, 420)
check(ids_of(found) == ids_of(search(root, 400, 400, 420, 420)), "search_with_cost finds the same places as search")
check(ids_of(found) == ids_of(brute_search(all_places, 400, 400, 420, 420)), "and they match the plain loop")
check(nodes_looked_at < count_nodes(root) / 20, "a small window looks at under 5 percent of the nodes (" + str(nodes_looked_at) + " of " + str(count_nodes(root)) + ")")
check(places_checked < 20000 / 20, "and checks under 5 percent of the places (" + str(places_checked) + " of 20000)")

# ---- 9. radius search and nearest place against the plain loop ----
random.seed(4)
radius_ok = True
nearest_ok = True
for trial in range(150):
    qx = random.random() * 1000
    qy = random.random() * 1000
    r = random.random() * 60
    expected = []
    for p in all_places:
        if squared_distance(p, qx, qy) <= r * r:
            expected.append(p)
    if ids_of(within_radius(root, qx, qy, r)) != ids_of(expected):
        radius_ok = False
    best = all_places[0]
    for p in all_places:
        if squared_distance(p, qx, qy) < squared_distance(best, qx, qy):
            best = p
    got = nearest(root, qx, qy)
    if squared_distance(got, qx, qy) != squared_distance(best, qx, qy):
        nearest_ok = False
check(radius_ok, "radius search matches the plain loop on 150 random circles")
check(nearest_ok, "nearest place matches the plain loop on 150 random points")

# nearest in awkward situations
empty = Node(0, 0, 100, 100, 0)
check(nearest(empty, 50, 50) is None, "nearest on an empty tree gives None")
one = Node(0, 0, 100, 100, 0)
only = Place(1, "Only", 99, 99)
insert(one, only)
check(nearest(one, 0, 0) is only, "nearest finds a place on the far side of the map")
check(nearest(one, 99, 99) is only, "nearest at the exact position of a place")
corner = Node(0, 0, 100, 100, 0)
insert(corner, Place(1, "Near", 10, 10))
insert(corner, Place(2, "Far", 100, 100))
check(nearest(corner, 11, 11).place_id == 1, "nearest picks the closer of two places")
check(len(within_radius(corner, 10, 10, 0)) == 1, "radius 0 finds only a place exactly at the centre")
check(len(within_radius(corner, 50, 50, 1)) == 0, "radius search with nothing nearby gives an empty list")

# ---- 10. speed: quadtree vs plain loop ----
random.seed(1)
root = Node(0, 0, 1000, 1000, 0)
all_places = []
for i in range(20000):
    p = Place(i, "P", random.random() * 1000, random.random() * 1000)
    insert(root, p)
    all_places.append(p)
windows = []
for i in range(100):
    x = random.random() * 980
    y = random.random() * 980
    windows.append([x, y, x + 20, y + 20])

start = time.time()
quad_total = 0
for w in windows:
    quad_total = quad_total + count(root, w[0], w[1], w[2], w[3])
quad_time = time.time() - start

start = time.time()
brute_total = 0
for w in windows:
    brute_total = brute_total + len(brute_search(all_places, w[0], w[1], w[2], w[3]))
brute_time = time.time() - start

check(quad_total == brute_total, "speed test: both methods found the same number of places")
print("Speed test (20000 places, 100 searches): quadtree " + str(round(quad_time, 3)) +
      " s, plain loop " + str(round(brute_time, 3)) + " s")

print("")
if len(problems) == 0:
    print("ALL TESTS PASSED")
else:
    print(str(len(problems)) + " TEST(S) FAILED")
