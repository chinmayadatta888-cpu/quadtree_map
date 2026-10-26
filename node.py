# Place, Node, insert (with splitting), and helpers for STATS and PRINT.

CAPACITY = 4     # a leaf holds at most this many places before it splits
MAX_DEPTH = 20   # a node at this depth never splits (stops endless splitting
                 # when many places have exactly the same coordinates).
                 # 20 levels cut the map into cells about a millionth of its width.


class Place:
    def __init__(self, place_id, name, x, y):
        self.place_id = place_id
        self.name = name
        self.x = x
        self.y = y


class Node:
    # One node = one rectangular region of the map.
    def __init__(self, x0, y0, x1, y1, depth):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.depth = depth
        self.places = []      # places stored here (only used by a leaf)
        self.children = []    # empty list = leaf, otherwise 4 child nodes

    def is_leaf(self):
        return len(self.children) == 0

    def child_index(self, x, y):
        # Which of the 4 quadrants does the point belong to?
        #   2 = top-left     | 3 = top-right
        #   -----------------+----------------
        #   0 = bottom-left  | 1 = bottom-right
        # A point exactly on a dividing line goes right / top,
        # so every point belongs to exactly ONE quadrant.
        mid_x = (self.x0 + self.x1) / 2
        mid_y = (self.y0 + self.y1) / 2
        if x < mid_x:
            if y < mid_y:
                return 0
            return 2
        if y < mid_y:
            return 1
        return 3

    def make_children(self):
        mid_x = (self.x0 + self.x1) / 2
        mid_y = (self.y0 + self.y1) / 2
        d = self.depth + 1
        self.children.append(Node(self.x0, self.y0, mid_x, mid_y, d))   # 0
        self.children.append(Node(mid_x, self.y0, self.x1, mid_y, d))   # 1
        self.children.append(Node(self.x0, mid_y, mid_x, self.y1, d))   # 2
        self.children.append(Node(mid_x, mid_y, self.x1, self.y1, d))   # 3


def insert(node, place):
    # The caller (main.py) has already checked the place is inside the map.
    if not node.is_leaf():
        i = node.child_index(place.x, place.y)
        insert(node.children[i], place)
        return
    node.places.append(place)
    if len(node.places) > CAPACITY and node.depth < MAX_DEPTH:
        split(node)


def split(node):
    # Turn a full leaf into an internal node: make 4 children, then insert the
    # old places again. They move down into the children. If they all land in
    # the same child, that child is over capacity and splits too (insert calls
    # split again), so the repeated splitting happens by itself.
    old_places = node.places
    node.places = []
    node.make_children()
    for place in old_places:
        insert(node, place)


def height(node):
    if node.is_leaf():
        return 0
    tallest = 0
    for child in node.children:
        h = height(child)
        if h > tallest:
            tallest = h
    return tallest + 1


def count_nodes(node):
    total = 1
    for child in node.children:
        total = total + count_nodes(child)
    return total


def show_tree(node, indent):
    # Prints the tree as indented text (used by the PRINT command).
    space = "  " * indent
    region = "(" + str(node.x0) + ", " + str(node.y0) + ") to (" + str(node.x1) + ", " + str(node.y1) + ")"
    if node.is_leaf():
        if len(node.places) == 0:
            print(space + "leaf " + region + "  empty")
        else:
            ids = ""
            for place in node.places:
                ids = ids + " " + str(place.place_id)
            print(space + "leaf " + region + "  places:" + ids)
    else:
        print(space + "split " + region)
        for child in node.children:
            show_tree(child, indent + 1)
