import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import random
import logging
from collections import deque
from typing import List, Dict, Optional, Tuple, Any
from Road import Road

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Vehicle:
    def __init__(self, vehicle_id: int, start_node: int, destination: int, graph: nx.DiGraph):
        self.vehicle_id = vehicle_id
        self.vehicle_length = 1.0 # needed?
        self.start_node = start_node
        self.destination = destination
        self.graph = graph
        self.path = self._plan_path(graph)
        self.path_index = 0  # Why is this 0? Need to understand
        self.current_road: Optional[Road] = None
        self.position_on_road = 0.0  # in meters
        self.max_speed = 20.0
        self.vehicle_length = 1.0
        self.current_speed = 0.0
        self.total_travel_time = 0.0
        self.total_wait_time = 0.0
        self.status = 'spawned' # spawned, traveling, waiting_at_light, arrived, finished
        
    # Plans path using Dijkstra's algorithm
    def _plan_path(self, graph: nx.DiGraph) -> List[int]:
        try:
            path = nx.shortest_path(graph, source=self.start_node, target=self.destination, weight='length')
            return path
        except nx.NetworkXNoPath:
            logging.warning(f"No path found from {self.start_node} to {self.destination}")
            return []
            
    def calculate_movement(self, dt: float) -> float:
        if self.current_road is None or self.status != 'traveling':
            self.current_speed = 0.0
            return 0.0

        # Max distance if unobstructed
        max_dist = self.max_speed * dt
        
        # Look ahead for traffic
        vehicle_in_front = self.current_road.get_vehicle_in_front(self.vehicle_id)
        
        # Simple car following model
        if vehicle_in_front:
            _, pos_in_front = vehicle_in_front
            distance_to_front = pos_in_front - self.position_on_road - 5.0 # 5.0 is minimum safe distance/vehicle length
            
            # If too close, slow down or stop
            if distance_to_front <= 0:
                self.current_speed = 0.0
                return 0.0
            
            # The distance we can move is limited by the distance to the vehicle in front
            max_dist = min(max_dist, distance_to_front)
        
        # Check distance to end of road
        remaining_road = self.current_road.length - self.position_on_road
        
        # The distance moved is limited by the distance to the end of the road
        move_distance = min(max_dist, remaining_road)

        # Update current speed for reporting/metrics (simple model: speed = distance / dt)
        self.current_speed = move_distance / dt if dt > 0 else 0.0
        if self.current_speed != self.max_speed :
            # todo This is also happening a lot more than it shd, to confirm: change logging.debug to logging.info, and idk why this is happening so many times
            # todo changes in main logic required ig? hopefully not
            logging.debug(f"Complex scenario occurred lol ")
        return move_distance
            
    def move(self, dt: float):
        if self.status == 'traveling':
            move_distance = self.calculate_movement(dt)
            self.position_on_road += move_distance
        
    def at_end_of_road(self) -> bool:
        tolerance = 0.1
        if self.current_road:
            return self.position_on_road >= self.current_road.length - tolerance
        return False
            
    def get_next_node(self) -> Optional[int]:
        if self.path_index + 1 < len(self.path):
            return self.path[self.path_index + 1]
        return None
    
    def is_at_destination(self) -> bool:
        if self.path_index == len(self.path) - 1:
            # todo Again a very useful logging statement, uncomment to see logs
            # logging.info(f"Vehicle {self.vehicle_id} has reached its destination {self.destination}.")
            return True
        return False