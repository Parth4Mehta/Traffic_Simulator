import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import random
import logging
from collections import deque
from typing import List, Dict, Optional, Tuple, Any
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Represents an edge, or a segment between two intersections
class Road:
    def __init__(self, start_node: int, end_node: int, length: float = 100.0, max_speed: float = 20.0):
        self.start_node = start_node
        self.end_node = end_node
        self.length = length
        self.max_speed = max_speed
        self.capacity = max(1, int(length // 7)) # todo not sure abt this metric
        self.vehicles_on_road: List[Tuple[int, float]] = [] 
        self.vehicle_size = 1.0 # todo not sure abt this metric too
        
    # Checks if the road has capacity, and the start of the road is clear to accommodate a new vehicle
    def can_enter(self) -> bool:
        if len(self.vehicles_on_road) >= self.capacity:
            return False
        if self.vehicles_on_road:
            closest_vehicle_pos = self.vehicles_on_road[-1][1] 
            # Require at least some space for a new vehicle to enter
            if closest_vehicle_pos < self.vehicle_size:
                return False
        return True
        
    # Just adds vehicle if possible and appends to list
    def add_vehicle(self, vehicle_id: int):
        if not self.can_enter():
            raise Exception("Road is at capacity or too close to another vehicle")
        
        self.vehicles_on_road.append((vehicle_id, 0.0))
        self.vehicles_on_road.sort(key=lambda x: x[1], reverse=True)

    # Removes vehicle by ID, returns True if removed, False if not found
    def remove_vehicle(self, vehicle_id: int) -> bool:
        initial_length = len(self.vehicles_on_road)
        self.vehicles_on_road = [v for v in self.vehicles_on_road if v[0] != vehicle_id]
        # log a warning if vehicle was not found
        # This if statement seems redundant... isnt it?
        if len(self.vehicles_on_road) == initial_length:
            print(f"Warning: Vehicle ID {vehicle_id} not found on road from {self.start_node} to {self.end_node}")
        return len(self.vehicles_on_road) < initial_length
        
    # Updates the position of a given vehicle by ID, given a new position
    def update_vehicle_position(self, vehicle_id: int, new_position: float):
        for i, (vid, pos) in enumerate(self.vehicles_on_road):
            if vid == vehicle_id:
                if new_position < 0 or new_position > self.length:
                    raise ValueError("New position out of road bounds")
                self.vehicles_on_road[i] = (vid, new_position)
                self.vehicles_on_road.sort(key=lambda x: x[1], reverse=True)
                return
        raise ValueError("Vehicle ID not found on this road")
        
    # Returns the ID and position of the vehicle directly in front of the given vehicle ID, if any
    # Where is this used? In Vehicle to determine distance to vehicle in front for acceleration/braking -> May not be useful in my case
    # Can be used in visualization/debugging or can be ignored
    def get_vehicle_in_front(self, vehicle_id: int) -> Optional[Tuple[int, float]]:
        is_next = False
        for v_id, pos in self.vehicles_on_road:
            if is_next:
                return (v_id, pos)
            if v_id == vehicle_id:
                is_next = True
        return None

    # Returns what percentage of the road is occupied by vehicles [0.0 to 1.0]
    # todo Issue (maybe): I am doing number_of_vehicles / capacity, but maybe say there are 5 vehicles on road with capacity 6 but they are placed in a way there is is space wasted in between but just not enough to fit another vehicle, so what i must do is, take the position of the start of the first vehicle and the end of the last vehicle, calculate this length, then in case there are empty spaces in this length where new cars can accommodate - reduce len by vehicle_size for each empty space, then divide by road length?
    # todo Which way would be more optimal to calculate congestion practically? I think the way I am doing it is basic and should be fine for now
    def get_congestion(self) -> float:
        if self.capacity <= 0:
            raise Exception("Road capacity is zero, cannot compute congestion")
        return len(self.vehicles_on_road) / self.capacity