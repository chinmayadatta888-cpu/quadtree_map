
# The program you run:  python main.py
# Type one command per line (type HELP to see them).

import random
from node import Node, Place, insert, height, count_nodes, show_tree
from search import search_with_cost, count, within_radius, nearest, squared_distance
from delete import delete


def show_help():
    print("Commands (a place name is ONE word, use _ instead of spaces):")
    print("  MAP x_min y_min x_max y_max   create the map (must be first)")
    print("  INSERT id name x y            add a place")
    print("  DELETE id                     remove a place")
    print("  MOVE id x y                   move a place to a new position")
    print("  SEARCH x1 y1 x2 y2            list places inside the rectangle")
    print("  COUNT x1 y1 x2 y2             count places inside the rectangle")
    print("  RADIUS x y r                  list places within distance r of (x, y)")
    print("  NEAREST x y                   find the place closest to (x, y)")
    print("  FILL n                        add n random places (for big demos)")
    print("  STATS                         size of the tree")
    print("  PRINT                         draw the tree as text (small trees only)")
    print("  HELP                          show this list")
    print("  EXIT                          quit")


def is_whole_number(text):
    # True for things like 7 or 120 (digits only).
    if text == "":
        return False
    for c in text:
        if c < "0" or c > "9":
            return False
    return True


def is_number(text):
    # True for things like 5, -3, 2.5, -0.75
    start = 0
    if text != "" and text[0] == "-":
        start = 1
    digits = 0
    dots = 0
    for i in range(start, len(text)):
        c = text[i]
        if c == ".":
            dots = dots + 1
        elif c >= "0" and c <= "9":
            digits = digits + 1
        else:
            return False
    return digits >= 1 and dots <= 1


def all_numbers(parts, first):
    # True if parts[first], parts[first + 1], ... are all numbers.
    for i in range(first, len(parts)):
        if not is_number(parts[i]):
            return False
    return True


def to_number(text):
    if "." in text:
        return float(text)
    return int(text)


def inside_map(root, x, y):
    return x >= root.x0 and x <= root.x1 and y >= root.y0 and y <= root.y1


def show_places(places, by_id):
    # Print the places in order of id so the output is easy to read.
    ids = []
    for place in places:
        ids.append(place.place_id)
    ids.sort()
    for place_id in ids:
        p = by_id[place_id]
        print("  " + str(p.place_id) + " " + p.name + " (" + str(p.x) + ", " + str(p.y) + ")")
    print("Found " + str(len(ids)) + " place(s)")


def read_rectangle(parts, usage):
    # Checks a SEARCH / COUNT command. Returns [x1, y1, x2, y2],
    # or an empty list (after printing the problem) if something is wrong.
    if len(parts) != 5:
        print("Usage: " + usage)
        return []
    if not all_numbers(parts, 1):
        print("Error: all four values must be numbers")
        return []
    x1 = to_number(parts[1])
    y1 = to_number(parts[2])
    x2 = to_number(parts[3])
    y2 = to_number(parts[4])
    if x1 > x2 or y1 > y2:
        print("Error: need x1 <= x2 and y1 <= y2")
        return []
    return [x1, y1, x2, y2]


# ---------- one function per command ----------

def do_map(parts):
    # Returns the new root node, or None if the command was wrong.
    if len(parts) != 5:
        print("Usage: MAP x_min y_min x_max y_max")
        return None
    if not all_numbers(parts, 1):
        print("Error: all four values must be numbers")
        return None
    x_min = to_number(parts[1])
    y_min = to_number(parts[2])
    x_max = to_number(parts[3])
    y_max = to_number(parts[4])
    if x_min >= x_max or y_min >= y_max:
        print("Error: need x_min < x_max and y_min < y_max")
        return None
    print("Map created")
    return Node(x_min, y_min, x_max, y_max, 0)


def do_insert(parts, root, by_id):
    if len(parts) != 5:
        print("Usage: INSERT id name x y")
    elif not is_whole_number(parts[1]):
        print("Error: id must be a whole number like 1, 2, 3")
    elif not all_numbers(parts, 3):
        print("Error: x and y must be numbers")
    else:
        place_id = int(parts[1])
        x = to_number(parts[3])
        y = to_number(parts[4])
        if place_id in by_id:
            print("Error: id " + str(place_id) + " already exists")
        elif not inside_map(root, x, y):
            print("Error: (" + str(x) + ", " + str(y) + ") is outside the map")
        else:
            place = Place(place_id, parts[2], x, y)
            by_id[place_id] = place
            insert(root, place)
            print("Inserted " + str(place_id) + " " + parts[2])


def do_delete(parts, root, by_id):
    if len(parts) != 2:
        print("Usage: DELETE id")
    elif not is_whole_number(parts[1]):
        print("Error: id must be a whole number like 1, 2, 3")
    else:
        place_id = int(parts[1])
        if place_id not in by_id:
            print("Error: no place with id " + str(place_id))
        else:
            delete(root, by_id[place_id])
            del by_id[place_id]
            print("Deleted " + str(place_id))


def do_move(parts, root, by_id):
    # A move is a delete followed by an insert at the new position.
    if len(parts) != 4:
        print("Usage: MOVE id x y")
    elif not is_whole_number(parts[1]):
        print("Error: id must be a whole number like 1, 2, 3")
    elif not all_numbers(parts, 2):
        print("Error: x and y must be numbers")
    else:
        place_id = int(parts[1])
        x = to_number(parts[2])
        y = to_number(parts[3])
        if place_id not in by_id:
            print("Error: no place with id " + str(place_id))
        elif not inside_map(root, x, y):
            print("Error: (" + str(x) + ", " + str(y) + ") is outside the map")
        else:
            old = by_id[place_id]
            delete(root, old)
            new_place = Place(place_id, old.name, x, y)
            by_id[place_id] = new_place
            insert(root, new_place)
            print("Moved " + str(place_id) + " " + old.name + " to (" + str(x) + ", " + str(y) + ")")


def do_search(parts, root, by_id):
    r = read_rectangle(parts, "SEARCH x1 y1 x2 y2")
    if len(r) == 0:
        return
    found, nodes_looked_at, places_checked = search_with_cost(root, r[0], r[1], r[2], r[3])
    show_places(found, by_id)
    print("Cost: looked at " + str(nodes_looked_at) + " of " + str(count_nodes(root)) +
          " nodes, checked " + str(places_checked) + " of " + str(len(by_id)) + " places")


def do_count(parts, root):
    r = read_rectangle(parts, "COUNT x1 y1 x2 y2")
    if len(r) == 0:
        return
    print("Count: " + str(count(root, r[0], r[1], r[2], r[3])))


def do_radius(parts, root, by_id):
    if len(parts) != 4:
        print("Usage: RADIUS x y r")
    elif not all_numbers(parts, 1):
        print("Error: x, y and r must be numbers")
    else:
        x = to_number(parts[1])
        y = to_number(parts[2])
        r = to_number(parts[3])
        if r < 0:
            print("Error: r cannot be negative")
        else:
            show_places(within_radius(root, x, y, r), by_id)


def do_nearest(parts, root, by_id):
    if len(parts) != 3:
        print("Usage: NEAREST x y")
    elif not all_numbers(parts, 1):
        print("Error: x and y must be numbers")
    elif len(by_id) == 0:
        print("No places stored yet")
    else:
        x = to_number(parts[1])
        y = to_number(parts[2])
        best = nearest(root, x, y)
        distance = squared_distance(best, x, y) ** 0.5
        print("Nearest: " + str(best.place_id) + " " + best.name + " (" + str(best.x) + ", " +
              str(best.y) + "), distance " + str(round(distance, 3)))


def do_fill(parts, root, by_id):
    # Adds n random places so you can try the tree on a big map.
    if len(parts) != 2:
        print("Usage: FILL n")
    elif not is_whole_number(parts[1]):
        print("Error: n must be a whole number like 1000")
    else:
        n = int(parts[1])
        if n > 500000:
            print("Error: n can be at most 500000")
        else:
            next_id = 0
            for place_id in by_id:
                if place_id >= next_id:
                    next_id = place_id + 1
            width = root.x1 - root.x0
            map_height = root.y1 - root.y0
            for i in range(n):
                x = root.x0 + random.random() * width
                y = root.y0 + random.random() * map_height
                place = Place(next_id, "R" + str(next_id), x, y)
                by_id[next_id] = place
                insert(root, place)
                next_id = next_id + 1
            print("Added " + str(n) + " random places, " + str(len(by_id)) + " stored in total")


def do_stats(root, by_id):
    print("Places stored : " + str(len(by_id)))
    print("Tree height   : " + str(height(root)))
    print("Total nodes   : " + str(count_nodes(root)))


def do_print(root):
    nodes = count_nodes(root)
    if nodes > 100:
        print("The tree has " + str(nodes) + " nodes, too many to print. Use STATS instead.")
    else:
        show_tree(root, 0)


def main():
    print("Quadtree Map Search. Type HELP for the commands.")
    root = None          # the top node, created by the MAP command
    by_id = {}           # id -> Place, so DELETE and MOVE can find the coordinates fast

    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            # EOF is a normal way for a piped command stream or console to end.
            print()
            break
        parts = line.split()
        if len(parts) == 0 or parts[0][0] == "#":
            continue
        cmd = parts[0].upper()

        if cmd == "EXIT":
            break
        elif cmd == "HELP":
            show_help()
        elif cmd == "MAP":
            new_root = do_map(parts)
            if new_root is not None:
                root = new_root
                by_id = {}
        elif root is None:
            print("Error: create the map first with MAP x_min y_min x_max y_max")
        elif cmd == "INSERT":
            do_insert(parts, root, by_id)
        elif cmd == "DELETE":
            do_delete(parts, root, by_id)
        elif cmd == "MOVE":
            do_move(parts, root, by_id)
        elif cmd == "SEARCH":
            do_search(parts, root, by_id)
        elif cmd == "COUNT":
            do_count(parts, root)
        elif cmd == "RADIUS":
            do_radius(parts, root, by_id)
        elif cmd == "NEAREST":
            do_nearest(parts, root, by_id)
        elif cmd == "FILL":
            do_fill(parts, root, by_id)
        elif cmd == "STATS":
            do_stats(root, by_id)
        elif cmd == "PRINT":
            do_print(root)
        else:
            print("Unknown command '" + cmd + "'. Type HELP")


if __name__ == "__main__":
    main()
