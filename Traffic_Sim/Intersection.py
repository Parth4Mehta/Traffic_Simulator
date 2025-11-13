import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import random
import logging
from collections import deque
from typing import List, Dict, Optional, Tuple, Any

from Road import Road
from TrafficLight import TrafficLight
from Vehicle import Vehicle
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Intersection:
    """Represents an intersection with traffic lights and queues."""
    
    def __init__(self, node_id: int):
        self.node_id = node_id
        self.incoming_roads: Dict[int, Road] = {} 
        self.queues: Dict[int, deque] = {} 
        self.traffic_light: Optional[TrafficLight] = None
        self.green_duration = 15
        self.yellow_duration = 3
    
    # Call the below one after all incoming roads are added to the traffic light
    def finalize_setup(self):
        incoming_road_count = len(self.incoming_roads)
        # sorting to maintain stability in index-to-road mapping
        self.incoming_road_keys = sorted(self.incoming_roads.keys())
        self.traffic_light = TrafficLight(self.node_id, incoming_road_count, green_duration=self.green_duration, yellow_duration=self.yellow_duration)
        for start_node in self.incoming_road_keys:
             self.queues[start_node] = deque()

    def add_incoming_road(self, road: Road):
        if self.traffic_light is not None:
             raise Exception("Cannot add road after traffic light setup is finalized.")
        self.incoming_roads[road.start_node] = road

    # To get the index of a given road on this intersection
    def get_direction_index(self, road_start_node: int) -> int:
        return self.incoming_road_keys.index(road_start_node)

    def enqueue_vehicle(self, vehicle_id: int, from_road: Road):
        at_node = from_road.start_node
        if at_node in self.queues:
            self.queues[at_node].append(vehicle_id)
            return True
        else:
            logging.error(f"Intersection {self.node_id}: Road from {at_node} karke koi node incoming mein hai hi nai")
            return False
            
    def update(self, dt: float):
        if self.traffic_light:
            self.traffic_light.update(dt)
            
    def process_queue(self, simulator, dt: float):
        if not self.traffic_light or self.traffic_light.is_green_phase is False:
            return 

        current_phase_index = self.traffic_light.current_phase_index
        
        if current_phase_index >= len(self.incoming_road_keys):
            return # Nai hoga ye hopefully kabhi bhi

        # The road that is currently green
        green_road_start_node = self.incoming_road_keys[current_phase_index]
        if green_road_start_node not in self.queues:
            return

        queue = self.queues[green_road_start_node]
        
        # Simple flow rate limit: allow max 1 vehicle per time step * 0.75 flow factor
        # This maybe WRONG
        # todo Check this part
        max_releases = max(1, int(1 * dt)) 
        released = 0
        
        while queue and released < max_releases:
            vehicle_id = queue[0]
            vehicle = simulator.vehicles.get(vehicle_id)
            
            if vehicle and self._try_release_vehicle(vehicle, simulator):
                queue.popleft()
                released += 1
            else:
                break 
                
    def _try_release_vehicle(self, vehicle: Vehicle, simulator) -> bool:
        if vehicle.is_at_destination():
            vehicle.status = 'arrived'
            return True
            
        next_node = vehicle.get_next_node()
        if next_node is None:
            print("Wtf just happened - do NULL check yaar")
            vehicle.status = 'arrived' 
            return True 
            
        current_node = vehicle.path[vehicle.path_index]
        next_road = simulator.get_road(current_node, next_node)
        
        if next_road and next_road.can_enter():
            next_road.add_vehicle(vehicle.vehicle_id)
            vehicle.current_road = next_road
            vehicle.path_index += 1 
            vehicle.position_on_road = 0.0
            vehicle.status = 'traveling'
            return True
        else:
            # todo This is happening a lot omre than it should
            # todo Why is the car not able to enter next road in so many scenarios? Is the next road genuinely so full of traffic? Or is it an error in code? Need to check
            # print(f"Can't enter next road... Road full or something")
            return False