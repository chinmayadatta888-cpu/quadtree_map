# Quadtree Map Search

A Python implementation of a **point-region quadtree** for storing places on a two-dimensional map. The project supports inserting, deleting, moving, and finding places by rectangular area, radius, or nearest distance.

It includes an interactive command-line demo, correctness checks, and experiments that compare quadtree searches with a plain scan.

## What is a quadtree?

A quadtree divides a two-dimensional region into four quadrants. When a leaf contains more than four places, it splits into four smaller regions. A spatial query can skip regions that do not overlap the requested area.

                 y increases
                     ^

       2: top-left  |  3: top-right
                    |
       --------------+--------------> x increases
                    |
       0: bottom-left | 1: bottom-right

A point on a dividing line is assigned to the right or upper quadrant, so it belongs to exactly one child.

## Features

- Insert places using a unique integer ID, name, and (x, y) coordinates.
- Search for places inside an inclusive rectangular area.
- Count places inside a rectangle.
- Find places within a radius using Euclidean distance.
- Find the nearest place to a coordinate.
- Delete places and merge sparse regions after deletion.
- Move places to new coordinates.
- Print tree statistics and a text view of small trees.
- Generate random places for larger demonstrations.
- Run correctness checks and performance experiments.

## Requirements

- Python 3
- No third-party packages

## Run the interactive demo

From the project folder, run:

    python main.py

Create a map first, then enter one command per line:

    MAP 0 0 100 100
    INSERT 1 Cafe_A 10 20
    INSERT 2 Pizza_B 80 90
    INSERT 3 Dosa_C 15 25
    SEARCH 0 0 30 30
    COUNT 0 0 100 100
    RADIUS 10 20 10
    NEAREST 50 50
    STATS
    EXIT

SEARCH 0 0 30 30 finds Cafe_A and Dosa_C. Rectangle edges are included. Place names must be one word; use underscores instead of spaces.

Type HELP in the program to see all available commands.

| Command | What it does |
|---|---|
| MAP x_min y_min x_max y_max | Creates the map. Must be the first command. Creating another map resets the stored places. |
| INSERT id name x y | Adds a place inside the map. IDs must be unique. |
| DELETE id | Removes the place with that ID. |
| MOVE id x y | Moves an existing place to new coordinates inside the map. |
| SEARCH x1 y1 x2 y2 | Lists places in the rectangle, including its edges. |
| COUNT x1 y1 x2 y2 | Counts places in the rectangle. |
| RADIUS x y r | Lists places whose Euclidean distance from (x, y) is at most r. |
| NEAREST x y | Finds the closest stored place. |
| FILL n | Adds n random places to the map. |
| STATS | Shows the number of places, tree height, and total nodes. |
| PRINT | Prints the tree structure when it has at most 100 nodes. |
| HELP | Lists commands. |
| EXIT | Quits the program. |

## Python interface

The data structure can also be used directly from Python:

    from node import Node, Place, insert
    from search import search, count, within_radius, nearest
    from delete import delete

    root = Node(0, 0, 100, 100, 0)

    cafe = Place(1, "Cafe_A", 10, 20)
    insert(root, cafe)

    places = search(root, 0, 0, 30, 30)
    number_of_places = count(root, 0, 0, 100, 100)
    nearby_places = within_radius(root, 10, 20, 5)
    closest_place = nearest(root, 50, 50)

    removed = delete(root, cafe)

search returns a list of matching Place objects. nearest returns a Place, or None if the tree is empty. delete returns True if it removed the place and False if it did not find it.

## How the implementation works

- **node.py** defines Place and Node, inserts places, splits full leaves, and provides tree height, node count, and text-printing helpers.
- **search.py** implements rectangle search, counting, search-cost measurement, radius search, and nearest-place search.
- **delete.py** removes places and merges a region's children back into a leaf when their combined contents fit.
- **main.py** provides the interactive command-line interface.
- **test.py** checks correctness and important edge cases.
- **experiments.py** compares quadtree search with a plain scan and explores different leaf capacities.

The default leaf capacity is **4** places. A leaf splits when an insertion exceeds that capacity. Splitting stops at **maximum depth 20**, which prevents endless subdivision when many places share the same coordinates.

Rectangle searches skip quadtree regions that do not overlap the requested rectangle. Radius search first checks the enclosing square, then filters candidates by exact distance. Nearest search expands its search area until it can determine the closest result.

Search performance depends on the data and query area. A small rectangle can avoid checking many places, while a query covering most of the map may need to inspect much of the tree.

## Run the tests

    python test.py

The test script checks insertion, deletion, rectangle searches, boundaries, repeated coordinates, radius and nearest searches, tree splitting and merging, and comparison with a plain scan. It prints ALL TESTS PASSED if all checks succeed.

## Run the experiments

    python experiments.py

The experiments print timing and search-cost tables for different numbers of places and leaf capacities. Results vary by computer; timings are for comparison, not fixed performance guarantees.
