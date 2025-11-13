# Traffic Simulator

A comprehensive Python-based traffic simulation system that models vehicle movement, traffic lights, and intersection management on a grid network.

## Overview

This project simulates realistic traffic flow through a network of intersections connected by roads. Vehicles follow shortest paths to their destinations, obey traffic lights, and interact with each other using simple car-following models.

## Features

- **Dynamic Traffic Network**: Create customizable grid-based road networks with bidirectional roads
- **Intelligent Vehicle Routing**: Vehicles use Dijkstra's algorithm to find shortest paths to destinations
- **Traffic Light Management**: Synchronized traffic lights with configurable green/yellow (and thus, red) durations
- **Queue Management**: Vehicles queue at intersections and are released based on traffic light states
- **Collision Avoidance**: Simple car-following model to maintain safe distances between vehicles
- **Real-time Metrics**: Track vehicle counts, travel times, wait times, and network congestion
- **Visualization**: Network visualization with congestion-based edge coloring

## Project Structure

- **main.py** - Entry point; sets up the simulation and grid network
- **Simulator.py** - Core simulation engine managing the overall flow
- **Intersection.py** - Intersection class with queue management and traffic light coordination
- **Road.py** - Road segment class tracking vehicles and congestion
- **Vehicle.py** - Vehicle class with pathfinding and movement logic
- **TrafficLight.py** - Traffic light state management

## Installation

### Requirements
- Python 3.7+
- numpy
- networkx
- matplotlib

### Setup

```bash
pip install -r requirements.txt
```

## Usage

Run the simulation:

```bash
python main.py
```

### Configuration

Edit parameters in `main.py`:

```python
# Simulation duration and time step
sim = Simulator(total_time=2000, dt=1.0)

# Grid dimensions
create_grid_network(sim, rows=3, cols=3)

# Vehicle spawning
sim.run(spawn_rate=10, spawn_interval=1)
```

**Parameters:**
- `total_time`: Total simulation duration in seconds
- `dt`: Time step per simulation update
- `rows`, `cols`: Grid network dimensions
- `spawn_rate`: Number of vehicles to spawn per interval
- `spawn_interval`: Steps between spawn events

## How It Works

### Simulation Loop

1. **Spawn Phase**: Vehicles randomly spawn at intersections with random destinations
2. **Movement Phase**: Active vehicles move along their current road based on:
   - Maximum speed
   - Distance to vehicle ahead
   - Distance to road end
3. **Intersection Phase**: Vehicles reaching road ends are removed and queued at intersections
4. **Traffic Light Phase**: Lights update; queued vehicles are released when their direction turns green
5. **Metrics Collection**: System tracks congestion, travel times, and wait times

### Vehicle Logic

- Vehicles use shortest path routing via NetworkX's Dijkstra algorithm
- Simple car-following: maintain safe distance from front vehicle
- Speed calculation: `distance_moved / dt`
- Vehicles transition through states: spawned → traveling → waiting_at_light → arrived

### Traffic Light Coordination

- Each intersection has a traffic light managing incoming roads
- Phases cycle through: GREEN → YELLOW → RED for each direction
- Configurable durations (default: 20s green, 5s yellow)
- Vehicles queue while waiting for green signal

### Congestion Calculation

Road congestion is calculated as:

```
Congestion = Number of vehicles on road / Road capacity
```

Network average congestion: Average across all roads in the network

## Metrics

The simulation tracks and reports:

- **Active Vehicles**: Currently traveling or waiting
- **Completed Vehicles**: Vehicles that reached their destination
- **Average Travel Time**: Mean time from spawn to destination
- **Average Wait Time**: Mean time spent waiting at traffic lights
- **Average Network Congestion**: Mean congestion across all roads (0.0 = empty, 1.0 = full)

## Visualization

The simulation generates a network graph showing:
- **Nodes**: Intersections
- **Edges**: Roads with:
  - Color gradient (green = low congestion, red = high congestion)
  - Width proportional to congestion
  - Labels showing vehicle count / road capacity

## Known Limitations & TODOs

- Road capacity calculation based on length (TODO: refine metric)
- Vehicle size representation simplified (TODO: improve physics model)
- Congestion calculation could account for spatial gaps between vehicles (TODO: enhancement)
- Queue release rate limited to prevent unrealistic flow (TODO: fine-tune)
- Large networks may have visualization performance issues

## Output Enhancements: 
## todo : 
- Algorithms for traffic lights to turn red/green based on incoming traffic
- Immediately turn lights to red once traffic on current greened lane is cleared
- Reinforcement learning techniques to synchronize traffic lights to create 'green-waves' for traffic clusters to reduce expected waiting times

## Model Enhancements: 

- Multiple vehicle types with different speeds
- Real-time visualization with animation
- Statistical analysis and performance reports


## License

This project is open source and available for educational and research purposes.