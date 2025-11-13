import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import random
import logging
from collections import deque
from typing import List, Dict, Optional, Tuple, Any

from TrafficLight import TrafficLight
from Road import Road
from Vehicle import Vehicle
from Intersection import Intersection
from Simulator import Simulator
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_grid_network(sim: Simulator, rows: int = 3, cols: int = 3):
    """Create a grid network of intersections."""
    # Add intersections
    for i in range(rows):
        for j in range(cols):
            node_id = i * cols + j
            # Only add the intersection, the road logic will handle the degree later
            sim.add_intersection(node_id)
    
    # Add roads (bidirectional)
    for i in range(rows):
        for j in range(cols):
            node_id = i * cols + j
            length = random.randint(80, 120) 

            # Horizontal roads
            if j < cols - 1:
                # Node A -> Node B
                sim.add_road(node_id, node_id + 1, length=length)
                # Node B -> Node A (opposite direction)
                sim.add_road(node_id + 1, node_id, length=length)
            
            # Vertical roads
            if i < rows - 1:
                # Node A -> Node C
                sim.add_road(node_id, node_id + cols, length=length)
                # Node C -> Node A (opposite direction)
                sim.add_road(node_id + cols, node_id, length=length)


# --- Deliverables ---

if __name__ == "__main__":
    # Ensure info-level logging is active to see simulation progress
    logging.getLogger().setLevel(logging.INFO) 
    
    print("\n" + "="*50)
    print("      🚦 Perfect Traffic Simulation 🚗")
    print("="*50 + "\n")
    
    # 1. Create and setup simulation
    # Total time: 2000 steps (~33 minutes of simulation time)
    # dt: 1.0 second per step
    sim = Simulator(total_time=2000, dt=1.0)
    
    # Create a 3x3 grid network
    create_grid_network(sim, rows=3, cols=3)
    
    # 2. Run simulation
    # Spawn Rate: 0.05 (Spawn ~4-5 vehicles total per spawn interval)
    # Spawn Interval: Every 10 steps (10 seconds)
    sim.run(spawn_rate=10, spawn_interval=1)
    
    # 3. Collect Final Metrics
    final_metrics = sim.collect_metrics()
    
    print("\n" + "="*50)
    print("          Simulation Results")
    print("="*50)
    print(f"Total Simulation Time: {sim.total_time:.0f}s")
    print(f"Total Vehicles Spawned: {sim.next_vehicle_id - 1}")
    print(f"Vehicles Completed Trip: {final_metrics['completed_vehicles']}")
    
    print("\n--- Key Metrics ---")
    print(f"Average Travel Time: {final_metrics['avg_travel_time']:.2f}s")
    print(f"Average Wait Time (at lights): {final_metrics['avg_wait_time']:.2f}s")
    print(f"Average Network Congestion: {final_metrics['avg_congestion']:.2f} (0.0=Empty, 1.0=Full)")
    print("="*50 + "\n")
    
    # 4. Visualize final state
    sim.visualize()
    #