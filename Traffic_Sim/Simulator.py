import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import random
import logging
from collections import deque
from typing import List, Dict, Optional, Tuple, Any

from Intersection import Intersection
from Road import Road
from Vehicle import Vehicle

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Simulator:
    def __init__(self, total_time: int = 1000, dt: float = 1.0):
        self.graph = nx.DiGraph() 
        self.intersections: Dict[int, Intersection] = {}
        self.roads: Dict[Tuple[int, int], Road] = {} 
        self.vehicles: Dict[int, Vehicle] = {}
        self.total_time = total_time
        self.current_time = 0.0
        self.dt = dt
        self.next_vehicle_id = 1
        self.completed_vehicles = []
        
    def add_intersection(self, node_id: int):
        if node_id not in self.intersections:
            intersection = Intersection(node_id)
            self.intersections[node_id] = intersection
            self.graph.add_node(node_id)
        else:
            logging.warning(f"Intersection {node_id} already exists.")
        
    def add_road(self, start_node: int, end_node: int, length: float = 100.0):
        road = Road(start_node, end_node, length)
        self.graph.add_edge(start_node, end_node, road=road, length=length) 
        self.roads[(start_node, end_node)] = road
        
        if end_node in self.intersections:
            self.intersections[end_node].add_incoming_road(road)
        else:
            
            logging.error(f"End node {end_node} for road from {start_node} does not exist as an intersection. woah?")


    def finalize_network_setup(self):
        """Finalize setup (e.g., traffic lights) after all roads are added."""
        for intersection in self.intersections.values():
            intersection.finalize_setup()
            logging.info(f"Intersection {intersection.node_id} finalized with {len(intersection.incoming_roads)} incoming roads.")
        
    def get_road(self, start_node: int, end_node: int) -> Optional[Road]:
        """Get road object between two nodes."""
        return self.roads.get((start_node, end_node))
        
    def add_vehicle(self, start_node: int, destination: int):
        vehicle = Vehicle(self.next_vehicle_id, start_node, destination, self.graph)
        
        if not vehicle.path or len(vehicle.path) < 2:
            logging.warning(f"Vehicle {self.next_vehicle_id} has no valid path from {start_node} to {destination}. Not adding to simulation.")
            return
        
        first_road_start = vehicle.path[0]
        first_road_end = vehicle.path[1]
        first_road = self.get_road(first_road_start, first_road_end)
        
        if first_road and first_road.can_enter():
            first_road.add_vehicle(vehicle.vehicle_id)
            vehicle.current_road = first_road
            vehicle.status = 'traveling'
            vehicle.position_on_road = 0.0
            vehicle.path_index = 0
            self.vehicles[self.next_vehicle_id] = vehicle
            logging.debug(f"Vehicle {self.next_vehicle_id} spawned: {start_node} -> {destination}")
            self.next_vehicle_id += 1
        else:
            # todo WARNING! : This is happening a lot more than it should, need to debug why
            logging.debug(f"Vehicle {self.next_vehicle_id} cannot enter the first road from {first_road_start} to {first_road_end}. Not adding to simulation.")
            
    def step(self):
        # Vehicle movements and end of road handling
        vehicles_to_process_at_intersection = []
        
        for vehicle in list(self.vehicles.values()):
            vehicle.total_travel_time += self.dt
            
            if vehicle.status == 'traveling':
                vehicle.move(self.dt)
                
                if vehicle.current_road:
                    vehicle.current_road.update_vehicle_position(vehicle.vehicle_id, vehicle.position_on_road)
                if vehicle.at_end_of_road():
                    vehicles_to_process_at_intersection.append(vehicle)
                    
            elif vehicle.status == 'arrived':
                logging.info(f"Vehicle {vehicle.vehicle_id} has already arrived at its destination.")
                continue
            
            # why only if waiting at light? what about waiting in queue?
            elif vehicle.status == 'waiting_at_light':
                vehicle.total_wait_time += self.dt
            
        # Process vehicles at intersections (queueing, arrival)
        for vehicle in vehicles_to_process_at_intersection:
            if vehicle.current_road:
                removed = vehicle.current_road.remove_vehicle(vehicle.vehicle_id)
                if not removed:
                    logging.error(f"Vehicle {vehicle.vehicle_id} could not be removed from road {vehicle.current_road.start_node} to {vehicle.current_road.end_node}. and idk whyyy")
            if vehicle.is_at_destination():
                vehicle.status = 'arrived'
                self.completed_vehicles.append(vehicle)
                del self.vehicles[vehicle.vehicle_id]
                # todo this is a useful logging command, uncomment to seelogs
                # logging.info(f"Vehicle {vehicle.vehicle_id} has arrived at its destination {vehicle.destination}. Total travel time: {vehicle.total_travel_time:.2f}s, Total wait time: {vehicle.total_wait_time:.2f}s")
                
            else:
                # enqueue at intersection
                current_node = vehicle.current_road.end_node if vehicle.current_road else vehicle.path[vehicle.path_index + 1]
                intersection = self.intersections.get(current_node)
                
                if intersection and vehicle.current_road:
                    intersection.enqueue_vehicle(vehicle.vehicle_id, vehicle.current_road)
                    vehicle.status = 'waiting_at_light'
                    vehicle.current_road = None
                    vehicle.position_on_road = 0.0
                    
                else:
                    logging.error(f"Vehicle {vehicle.vehicle_id} at node {current_node} has no valid intersection to enqueue at, and idgaf what this means")
                    vehicle.status = 'im broke'
                    
        # update traffic lights
        for intersection in self.intersections.values():
            intersection.update(self.dt)
            
        # process intersection queues
        for intersection in self.intersections.values():
            intersection.process_queue(self, self.dt)
            
        self.current_time += self.dt
        
    def run(self, spawn_rate: float = 0.01, spawn_interval: int = 10):
        """Run the simulation."""
        self.finalize_network_setup()
        logging.info("Starting simulation...")
        
        step_count = 0
        while self.current_time < self.total_time:
            # Spawn vehicles periodically
            if step_count % spawn_interval == 0:
                self.spawn_random_vehicles(spawn_rate)
                
            self.step()
            step_count += 1
            
            # Log metrics periodically
            if int(self.current_time) % 100 == 0 and self.current_time > 0:
                metrics = self.collect_metrics()
                log_msg = (f"Time: {self.current_time:.0f}s | Active: {metrics['active_vehicles']} | "
                           f"Completed: {metrics['completed_vehicles']} | Congestion: {metrics['avg_congestion']:.2f}")
                if metrics['completed_vehicles'] > 0:
                     log_msg += f" | Avg Travel Time: {metrics['avg_travel_time']:.1f}s"
                logging.info(log_msg)
            
        logging.info("Simulation complete!")
        
    def spawn_random_vehicles(self, spawn_rate: float):
        """Spawn vehicles randomly based on spawn rate."""
        # Only spawn if there are intersections (nodes)
        nodes = list(self.graph.nodes())
        if not nodes:
            return
            
        num_to_spawn = 0
        if spawn_rate < 1.0:
            # Use random choice based on probability
            if random.random() < spawn_rate * len(nodes):
                num_to_spawn = 1
        else:
            # Spawn a fixed number if rate is high
            num_to_spawn = int(spawn_rate)
            
        for _ in range(num_to_spawn):
            start = random.choice(nodes)
            dest = random.choice(nodes)
            while dest == start:
                dest = random.choice(nodes)
            self.add_vehicle(start, dest)
                
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect simulation metrics."""
        active_vehicles = len(self.vehicles)
        completed_vehicles = len(self.completed_vehicles)
        
        if completed_vehicles > 0:
            avg_travel_time = sum(v.total_travel_time for v in self.completed_vehicles) / completed_vehicles
            avg_wait_time = sum(v.total_wait_time for v in self.completed_vehicles) / completed_vehicles
        else:
            avg_travel_time = 0.0
            avg_wait_time = 0.0
            
        total_congestion = sum(road.get_congestion() for road in self.roads.values())
        avg_congestion = total_congestion / len(self.roads) if self.roads else 0.0
        
        return {
            'active_vehicles': active_vehicles,
            'completed_vehicles': completed_vehicles,
            'avg_travel_time': avg_travel_time,
            'avg_wait_time': avg_wait_time,
            'avg_congestion': avg_congestion
        }
        
    def visualize(self):
        """Since the graph is too huge, visualising the entire is impossible. So visualising a small part of it."""
    
        pos = nx.spring_layout(self.graph, seed=42)
        plt.figure(figsize=(10, 8))
        
        nx.draw(self.graph, pos, with_labels=True, node_size=500, node_color='lightblue', font_size=10, font_weight='bold', arrowsize=20)
        edge_labels = nx.get_edge_attributes(self.graph, 'length')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        plt.title("Traffic Network")
        plt.show()
        
        
    def visualize_orig(self):
        """Visualize the traffic network, roads, and congestion."""
        
        # Fallback to spring layout if no positions are set
        pos = nx.spring_layout(self.graph, seed=42) 
        
        plt.figure(figsize=(10, 8))
        
        # Draw nodes (Intersections)
        node_colors = ['#FFC300' for node in self.graph.nodes()] # Yellow/Orange for Intersections
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, node_size=600, alpha=0.8)
        nx.draw_networkx_labels(self.graph, pos, font_size=10, font_weight='bold')
        
        # Draw edges with congestion info
        edge_colors = []
        edge_widths = []
        edge_labels = {}
        for u, v, data in self.graph.edges(data=True):
            road = self.roads.get((u, v))
            if road:
                congestion = road.get_congestion()
                # Color gradient from green (0.0) to red (1.0)
                edge_colors.append(plt.cm.RdYlGn(1.0 - congestion))
                edge_widths.append(1.5 + congestion * 3.5)
                # Label with current vehicle count / total capacity
                edge_labels[(u, v)] = f"{len(road.vehicles_on_road)}/{road.capacity}" 
            else:
                edge_colors.append('gray')
                edge_widths.append(1)
        
        nx.draw_networkx_edges(self.graph, pos, edge_color=edge_colors, 
                                 width=edge_widths, arrows=True, arrowsize=15, alpha=0.7)
        
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels, font_size=7, label_pos=0.3)
        
        plt.title(f"Traffic Simulation (Time: {self.current_time:.0f}s | Active V: {len(self.vehicles)})", fontsize=14)
        plt.axis('off')
        plt.tight_layout()
        plt.show()