# Shobhit 
# Imports for basic math functions and regular expressions
import sys
import math
import re

# Defining the data classes for Points and Loads that I used later in the program
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Load:
    def __init__(self, load_id, pickup, dropoff):
        self.id = load_id
        self.pickup = pickup
        self.dropoff = dropoff

# Calculating the Euclidean distance between two points using the hypotenuse function
def distance(a: Point, b: Point):
    return math.hypot(a.x - b.x, a.y - b.y)

# This is to parse through input files and extract the loadID, I used regex
# to extract the pickup and dropff coordinates and convert to point objects and then loads.append
# to add to the loads list.

def load_problem(file_path):
    loads = []
    with open(file_path, 'r') as file:
        next(file)  # Skip the first line of the text file as it is just text
        for line in file:
            parts = line.strip().split()
            load_id = parts[0]
            pickup_coords = re.findall(r'-?\d+\.?\d*', parts[1])
            dropoff_coords = re.findall(r'-?\d+\.?\d*', parts[2])
            pickup = Point(float(pickup_coords[0]), float(pickup_coords[1]))
            dropoff = Point(float(dropoff_coords[0]), float(dropoff_coords[1]))
            loads.append(Load(load_id, pickup, dropoff))
    return loads

# This initializes routes for each load, the total distance from depot to pickup to dropoff
# and back to depot is calculated and stored

def initialize_routes(loads):
    routes = {}
    for load in loads:
        route = {
            'loads': [load.id],
            'start': load.pickup,
            'end': load.dropoff,
            'distance': (
                distance(Point(0, 0), load.pickup) +
                distance(load.pickup, load.dropoff) +
                distance(load.dropoff, Point(0, 0))
            )
        }
        routes[load.id] = route
    return routes

# Built a dictionary of loads for quicker access where the loadID is the key and value corresponding
# is the load object.

def build_loads_dict(loads):
    return {load.id: load for load in loads}

# Calculating the savings for routes that merge as in how much can be saved by connecting the end
# of one route and start of another one. 

def calculate_savings(loads):
    savings = []
    depot = Point(0, 0)
    n = len(loads)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue # skip as load should'nt be compare to itself
            load_i = loads[i]
            load_j = loads[j]
            # Savings if we connect load_i's route end to load_j's route start
            saving = (
                distance(load_i.dropoff, depot) +
                distance(depot, load_j.pickup) -
                distance(load_i.dropoff, load_j.pickup)
            )
            savings.append({
                'from': load_i.id,
                'to': load_j.id,
                'saving': saving
            })
    savings.sort(key=lambda x: x['saving'], reverse=True) #The savings are stored in descending order to prioritize the savings
    return savings

# Merging routes based on the savings
def merge_routes(routes, savings, loads_dict):
    max_drive_time = 12 * 60  # 12 hours to minutes which is the max for each driver
    # This is to keep track of which loads are in which routes
    load_route_map = {load_id: load_id for load_id in routes.keys()}
    for s in savings:
        from_route_id = load_route_map.get(s['from'])
        to_route_id = load_route_map.get(s['to'])
        if from_route_id is None or to_route_id is None:
            continue
        if from_route_id == to_route_id:
            continue
        from_route = routes[from_route_id]
        to_route = routes[to_route_id]
        # Check if we can merge from the route's end to the route's start and replace the separtae routes with one merged route
        if from_route['loads'][-1] == s['from'] and to_route['loads'][0] == s['to']:
            # Ensure no loops are created
            # Calculating the new distance that the truck goes through
            new_distance = (
                from_route['distance'] +
                to_route['distance'] -
                distance(from_route['end'], Point(0, 0)) -
                distance(Point(0, 0), to_route['start']) +
                distance(from_route['end'], to_route['start'])
            )
            if new_distance <= max_drive_time:
                # Merging of the routes
                merged_loads = from_route['loads'] + to_route['loads']
                routes[from_route_id] = {
                    'loads': merged_loads,
                    'start': from_route['start'],
                    'end': to_route['end'],
                    'distance': new_distance
                }
                # Updating load_route_map
                for load_id in to_route['loads']:
                    load_route_map[load_id] = from_route_id
                # Remove the old to_route
                del routes[to_route_id]
    return routes

# The main function that loads in all the results and uses the values of the previous functions
def main():
    if len(sys.argv) != 2:
        return
    file_path = sys.argv[1]
    loads = load_problem(file_path)
    loads_dict = build_loads_dict(loads)
    routes = initialize_routes(loads)
    savings = calculate_savings(loads)
    routes = merge_routes(routes, savings, loads_dict)
    # Output of the routes
    for route in routes.values():
        print(f"[{','.join(route['loads'])}]")

if __name__ == "__main__":
    main()