# This class represents a traffic light at an intersection
# What it does? Manages states of light for multiple incoming roads
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import random
import logging
from collections import deque
from typing import List, Dict, Optional, Tuple, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TrafficLight:
    def __init__(self, node_id: int, incoming_road_count: int, green_duration: int = 20, yellow_duration: int = 5):
        # For red it is just not current_phase_index
        self.node_id = node_id
        self.incoming_road_count = incoming_road_count
        self.green_duration = green_duration
        self.yellow_duration = yellow_duration
        self.cycle_length = (green_duration + yellow_duration) * incoming_road_count
        self.current_phase_index = 0 # 0 to incoming_road_count - 1
        self.time_in_phase = 0.0
        self.is_green_phase = True
    
    # Updates the traffic light state based on elapsed time
    # To be called every simulation step with dt (time step)
    def update(self, dt: float = 1.0):
        self.time_in_phase += dt
        if self.is_green_phase:
            if self.time_in_phase >= self.green_duration:
                self.is_green_phase = False
                self.time_in_phase = 0.0
        else:
            if self.time_in_phase >= self.yellow_duration:
                self.current_phase_index = (self.current_phase_index + 1) % self.incoming_road_count
                self.is_green_phase = True
                self.time_in_phase = 0.0
                
    # Checks if the traffic light is green for a given lane index
    def is_green(self, incoming_road_index: int) -> bool:
        return self.is_green_phase and (self.current_phase_index == incoming_road_index)
                
    # Returns the current signal state for a given lane index
    def get_signal_state(self, direction_index: int) -> str:
        if direction_index == self.current_phase_index:
            return "GREEN" if self.is_green_phase else "YELLOW"
        else:
            return "RED"