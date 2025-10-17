# 🏥 AI Hospital Robot Management System

An intelligent autonomous robot management system for hospital logistics, featuring AI-driven task allocation, fuzzy logic battery management, and real-time visualization.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.5.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Technologies](#technologies)
- [Algorithms](#algorithms)
- [Screenshots](#screenshots)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### 🤖 Robot Management
- **4 Autonomous Robots** with unique capabilities
- Real-time position tracking and visualization
- Battery level monitoring with smart charging
- Collision avoidance system
- Performance metrics and analytics

### 📦 Task System
- **7 Task Types**: Medicine, Blood Samples, Supplies, Equipment, Food, Documents, Lab Samples
- **3 Urgency Levels**: Normal, Urgent, Emergency
- Priority-based task assignment
- Automatic retry mechanism for failed tasks
- Comprehensive task tracking

### 🧠 Intelligent Algorithms
- **RRA (Robot Ranking Algorithm)**: Optimal robot selection
- **A* Pathfinding**: Efficient route planning
- **Fuzzy Logic**: Intelligent battery management
- **Collision Avoidance**: Safe multi-robot coordination
- **Path Optimization**: Smooth path generation

### 🎨 Advanced Visualization
- Real-time hospital map rendering
- Animated robot movements
- Dynamic path visualization
- Interactive control dashboard
- Performance statistics display
- Legend and instructions overlay

### 📊 Analytics & Reporting
- Real-time performance metrics
- Robot utilization statistics
- Task completion rates
- Battery consumption tracking
- Comprehensive final reports

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────┐
│           AI Hospital System Core               │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐    ┌──────────────┐          │
│  │   Robots     │◄──►│    Tasks     │          │
│  └──────────────┘    └──────────────┘          │
│         │                    │                  │
│         ▼                    ▼                  │
│  ┌──────────────────────────────────┐          │
│  │    Algorithms & Optimization     │          │
│  │  • RRA  • A*  • Fuzzy Logic     │          │
│  └──────────────────────────────────┘          │
│         │                    │                  │
│         ▼                    ▼                  │
│  ┌──────────────┐    ┌──────────────┐          │
│  │ Visualization│    │  Statistics  │          │
│  └──────────────┘    └──────────────┘          │
└─────────────────────────────────────────────────┘
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/ai-hospital-robots.git
cd ai-hospital-robots
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Optional: Install Development Dependencies

```bash
pip install pytest black flake8
```

## 🎮 Usage

### Running the System

```bash
python main.py
```

### Controls

| Key | Action |
|-----|--------|
| `SPACE` | Assign next task to optimal robot |
| `P` | Pause/Resume simulation |
| `R` | Reset simulation |
| `ESC` | Exit system |

### Basic Workflow

1. **Start System**: Run `python main.py`
2. **Observe**: Watch robots automatically receive and execute tasks
3. **Interact**: Press `SPACE` to manually assign next task
4. **Monitor**: Check dashboard for real-time statistics
5. **Analyze**: Review final performance report on exit

## 📁 Project Structure

```
AI_Hospital_Robots/
│
├── main.py                    # Main entry point
├── hospital_config.py         # Hospital map and configuration
├── robot_system.py           # Robot and Task classes
├── algorithms.py             # Pathfinding and optimization
├── fuzzy_logic.py            # Battery management system
├── visualization.py          # Pygame visualization
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

### File Descriptions

#### `main.py`
Main orchestrator managing the entire system, event loop, and coordination between components.

#### `hospital_config.py`
- Hospital map layout (15x15 grid)
- Color schemes and visual settings
- Robot configurations
- Task type definitions
- Utility functions (pathfinding helpers, distance calculations)

#### `robot_system.py`
- `Robot` class: Autonomous robot with movement, battery, and task execution
- `Task` class: Task definitions with urgency, weight, and tracking
- Performance metrics tracking
- Status management (Available, Busy, Charging, etc.)

#### `algorithms.py`
- `PathfindingAlgorithms`: A*, Dijkstra, BFS implementations
- `RobotRankingAlgorithm`: RRA for optimal robot selection
- `PathOptimizer`: Path smoothing and optimization
- `CollisionAvoidance`: Multi-robot coordination

#### `fuzzy_logic.py`
- `FuzzyChargingSystem`: Intelligent battery management using fuzzy logic
- `BatteryManager`: Battery monitoring and estimation utilities
- Charging priority determination (Critical, High, Medium, Low)
- Fallback rule-based system when fuzzy library unavailable

#### `visualization.py`
- `HospitalVisualization`: Pygame-based rendering system
- Real-time map drawing with grid, walls, obstacles
- Robot visualization with animations and battery indicators
- Path rendering with animated effects
- Interactive dashboard and statistics display

## 🔬 Technologies

### Core Technologies
- **Python 3.8+**: Main programming language
- **Pygame 2.5.0+**: Graphics and visualization
- **NumPy**: Numerical computations and array operations

### AI & Algorithms
- **A* Algorithm**: Optimal pathfinding
- **Fuzzy Logic**: Intelligent decision-making (scikit-fuzzy)
- **Robot Ranking Algorithm (RRA)**: Custom optimization algorithm

### Design Patterns
- Object-Oriented Programming (OOP)
- Component-Based Architecture
- Observer Pattern for event handling
- Strategy Pattern for algorithm selection

## 🧮 Algorithms

### 1. Robot Ranking Algorithm (RRA)

Selects the optimal robot for each task based on multiple factors:

```
Rank = ((Speed_Factor × α) + (Energy_Factor × β)) / Total_Distance × Weight_OK × Urgency_Multiplier

where:
- Speed_Factor = (robot_velocity / 30) × α
- Energy_Factor = (battery_percentage / 100) × β
- Total_Distance = D1 + D2 (Manhattan distance)
- Weight_OK = 1 if robot can carry load, else 0
- Urgency_Multiplier = {Normal: 1.0, Urgent: 1.5, Emergency: 2.0}
- α = 0.6, β = 0.4 (configurable weights)
```

### 2. A* Pathfinding

Finds the shortest path avoiding obstacles:

```
f(n) = g(n) + h(n)

where:
- g(n) = actual cost from start to node n
- h(n) = heuristic (Manhattan distance to goal)
- f(n) = estimated total cost
```

**Features:**
- Guaranteed optimal path
- Efficient with heuristic guidance
- Obstacle avoidance
- 4-directional movement (up, down, left, right)

### 3. Fuzzy Logic Battery Management

Determines charging priority using fuzzy inference:

**Inputs:**
- Battery charge level (0-100%)
- Robot velocity (0-30 units/s)
- Workload (0-20 tasks)
- Distance to charging station (0-50 units)

**Output:**
- Charging priority score (0-10)

**Membership Functions:**
- Charge: Critical, Low, Medium, High, Full
- Velocity: Slow, Medium, Fast
- Workload: Light, Moderate, Heavy

**Rules (Sample):**
```
IF charge is critical THEN priority is critical
IF charge is low AND distance is far THEN priority is critical
IF charge is high AND workload is light THEN priority is low
```

### 4. Path Optimization

Smooths paths by removing unnecessary waypoints:

```python
# Original path with many turns
path = [(1,1), (2,1), (2,2), (2,3), (3,3), (4,3)]

# Optimized path (straight segments)
optimized = [(1,1), (2,1), (2,3), (4,3)]
```

### 5. Collision Avoidance

Prevents robot collisions through path reservation:

- Each robot reserves cells along its path with timestamps
- System checks for conflicts before assignment
- Dynamic obstacle tracking for real-time avoidance

## 📸 Screenshots

### Main Interface
```
┌─────────────────────────────────────────────────┐
│  Hospital Map (15x15 Grid)                      │
│  ┌─────────────────────────────────────┐        │
│  │  🏥 Walls  🚧 Obstacles             │        │
│  │  🤖 Robots  📍 Source  🎯 Destination│        │
│  │  ═══ Paths  💫 Animations           │        │
│  └─────────────────────────────────────┘        │
│                                                  │
│  📊 Control Dashboard                           │
│  ┌─────────────────────────────────────┐        │
│  │ 🤖 Robots:                           │        │
│  │   MediBot-1: 🟢 ████████░ 85%       │        │
│  │   MediBot-2: 🔴 ████████░ 78%       │        │
│  │                                      │        │
│  │ 📦 Tasks: Completed: 4/6            │        │
│  │ 🤖 MediBot-1 → 💊 Medicine Delivery │        │
│  └─────────────────────────────────────┘        │
└─────────────────────────────────────────────────┘
```

## ⚙️ Configuration

### Customizing Hospital Map

Edit `hospital_config.py`:

```python
HOSPITAL_MAP = [
    "###############",
    "#R1  #     #  #",
    "#    #  O  #  #",
    # ... customize layout
]
```

**Legend:**
- `#` = Wall
- ` ` = Floor (walkable)
- `O` = Obstacle
- `R1-R4` = Robot starting positions
- `S` = Source point
- `D` = Destination point

### Adjusting Robot Parameters

Modify in `main.py` → `initialize_robots()`:

```python
robot.velocity = 25           # Speed (units/second)
robot.charge_percentage = 75  # Initial battery (%)
robot.weight_threshold = 8    # Max load capacity (kg)
robot.battery_drain_rate = 0.08  # Drain per movement
```

### Changing RRA Weights

Adjust in `algorithms.py`:

```python
rra = RobotRankingAlgorithm(
    alpha=0.6,  # Speed factor weight
    beta=0.4    # Energy factor weight
)
```

### Creating Custom Tasks

Add tasks in `main.py` → `create_sample_tasks()`:

```python
{
    'source': (1, 13),
    'destination': (10, 10),
    'urgency': TaskUrgency.URGENT,
    'weight': 5,
    'type': 'medicine',
    'description': 'Custom task description'
}
```

## 🎯 Use Cases

### 1. Hospital Logistics
- Medicine and supply delivery
- Lab sample transportation
- Equipment distribution
- Meal delivery to patients

### 2. Research & Education
- Algorithm comparison and benchmarking
- Fuzzy logic demonstration
- Multi-agent system studies
- Path planning visualization

### 3. Simulation & Testing
- Robot fleet optimization
- Task scheduling strategies
- Battery management evaluation
- Performance analysis

## 📈 Performance Metrics

The system tracks and reports:

- **Task Metrics**
  - Completion rate (%)
  - Average completion time
  - Failed task count
  - Task distribution by urgency

- **Robot Metrics**
  - Individual robot utilization
  - Distance traveled per robot
  - Battery consumption
  - Tasks completed per robot

- **System Metrics**
  - Overall efficiency score
  - Total system uptime
  - Average response time
  - Resource utilization

## 🔧 Troubleshooting

### Issue: Fuzzy logic not working

**Solution:**
```bash
pip install scikit-fuzzy
```

If installation fails, the system will use fallback rule-based charging.

### Issue: Pygame display issues

**Solution:**
```bash
# Try updating pygame
pip install --upgrade pygame

# Or reinstall
pip uninstall pygame
pip install pygame
```

### Issue: Robots not moving

**Check:**
1. Verify map configuration is valid
2. Ensure paths exist between source and destination
3. Check for obstacles blocking all routes
4. Confirm robots have sufficient battery

### Issue: Performance lag

**Solutions:**
- Reduce FPS in `main.py`: `clock.tick(30)`
- Simplify hospital map
- Reduce number of simultaneous tasks
- Disable path animations

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/ai-hospital-robots.git
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Make Changes**
   - Write clean, documented code
   - Follow PEP 8 style guidelines
   - Add tests if applicable

4. **Commit Changes**
   ```bash
   git commit -m "Add: Your feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/YourFeature
   ```

### Development Guidelines

- Use type hints for all functions
- Document classes and methods with docstrings
- Follow existing code structure
- Test thoroughly before submitting
- Update README if adding features

## 📚 Further Reading

### Academic References

1. **Robot Ranking Algorithm (RRA)**
   - Multi-criteria decision making in robotics
   - Task allocation in multi-robot systems

2. **A* Pathfinding**
   - Hart, P. E.; Nilsson, N. J.; Raphael, B. (1968)
   - "A Formal Basis for the Heuristic Determination of Minimum Cost Paths"

3. **Fuzzy Logic Control**
   - Zadeh, L. A. (1965)
   - "Fuzzy Sets", Information and Control

### Related Technologies

- **ROS (Robot Operating System)**: Industrial robot framework
- **SLAM**: Simultaneous Localization and Mapping
- **Multi-Agent Systems**: Distributed AI coordination
- **Swarm Robotics**: Collective behavior systems

## 📝 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2024 AI Hospital Robot Management System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
