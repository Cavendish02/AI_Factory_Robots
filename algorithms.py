"""
Algorithms Module
Implements RRA (Robot Ranking Algorithm), A* pathfinding, and optimization algorithms
"""

import numpy as np
import heapq
from typing import List, Tuple, Optional, Dict
from hospital_config import HOSPITAL_MAP, get_neighbors, manhattan_distance, euclidean_distance

class PathfindingAlgorithms:
    """Collection of pathfinding algorithms"""
    
    @staticmethod
    def a_star(start: Tuple[int, int], end: Tuple[int, int], 
               obstacles: List[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        """
        A* pathfinding algorithm - finds optimal path
        
        Args:
            start: Starting position (x, y)
            end: Goal position (x, y)
            obstacles: List of obstacle positions to avoid
        
        Returns:
            List of positions representing the path, or empty list if no path found
        """
        if obstacles is None:
            obstacles = []
        
        def heuristic(pos1, pos2):
            """Manhattan distance heuristic"""
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
        # Priority queue: (f_score, counter, position)
        open_set = []
        counter = 0
        heapq.heappush(open_set, (0, counter, start))
        
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, end)}
        open_set_hash = {start}
        
        while open_set:
            current = heapq.heappop(open_set)[2]
            open_set_hash.remove(current)
            
            if current == end:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path
            
            # Explore neighbors
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # Check if neighbor is valid
                if (0 <= neighbor[0] < len(HOSPITAL_MAP[0]) and 
                    0 <= neighbor[1] < len(HOSPITAL_MAP) and
                    HOSPITAL_MAP[neighbor[1]][neighbor[0]] not in ['#', 'O'] and
                    neighbor not in obstacles):
                    
                    tentative_g_score = g_score[current] + 1
                    
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                        
                        if neighbor not in open_set_hash:
                            counter += 1
                            heapq.heappush(open_set, (f_score[neighbor], counter, neighbor))
                            open_set_hash.add(neighbor)
        
        return []  # No path found
    
    @staticmethod
    def dijkstra(start: Tuple[int, int], end: Tuple[int, int], 
                 obstacles: List[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        """
        Dijkstra's algorithm - guaranteed shortest path
        
        Args:
            start: Starting position (x, y)
            end: Goal position (x, y)
            obstacles: List of obstacle positions to avoid
        
        Returns:
            List of positions representing the path
        """
        if obstacles is None:
            obstacles = []
        
        # Priority queue: (distance, counter, position)
        pq = []
        counter = 0
        heapq.heappush(pq, (0, counter, start))
        
        distances = {start: 0}
        came_from = {}
        visited = set()
        
        while pq:
            dist, _, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            if current == end:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path
            
            # Explore neighbors
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                if (0 <= neighbor[0] < len(HOSPITAL_MAP[0]) and 
                    0 <= neighbor[1] < len(HOSPITAL_MAP) and
                    HOSPITAL_MAP[neighbor[1]][neighbor[0]] not in ['#', 'O'] and
                    neighbor not in obstacles and
                    neighbor not in visited):
                    
                    new_dist = dist + 1
                    
                    if neighbor not in distances or new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        came_from[neighbor] = current
                        counter += 1
                        heapq.heappush(pq, (new_dist, counter, neighbor))
        
        return []
    
    @staticmethod
    def bfs(start: Tuple[int, int], end: Tuple[int, int], 
            obstacles: List[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        """
        Breadth-First Search - simple pathfinding
        
        Args:
            start: Starting position (x, y)
            end: Goal position (x, y)
            obstacles: List of obstacle positions to avoid
        
        Returns:
            List of positions representing the path
        """
        if obstacles is None:
            obstacles = []
        
        from collections import deque
        
        queue = deque([start])
        came_from = {start: None}
        
        while queue:
            current = queue.popleft()
            
            if current == end:
                # Reconstruct path
                path = [current]
                while came_from[current] is not None:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                if (0 <= neighbor[0] < len(HOSPITAL_MAP[0]) and 
                    0 <= neighbor[1] < len(HOSPITAL_MAP) and
                    HOSPITAL_MAP[neighbor[1]][neighbor[0]] not in ['#', 'O'] and
                    neighbor not in obstacles and
                    neighbor not in came_from):
                    
                    queue.append(neighbor)
                    came_from[neighbor] = current
        
        return []


class RobotRankingAlgorithm:
    """Robot Ranking Algorithm (RRA) for optimal robot selection"""
    
    def __init__(self, alpha: float = 0.6, beta: float = 0.4):
        """
        Initialize RRA with weight parameters
        
        Args:
            alpha: Weight for speed factor (default: 0.6)
            beta: Weight for energy factor (default: 0.4)
        """
        self.alpha = alpha
        self.beta = beta
    
    def calculate_robot_rank(self, robot, task) -> float:
        """
        Calculate robot ranking score for a task
        
        Args:
            robot: Robot object
            task: Task object
        
        Returns:
            float: Ranking score (higher is better)
        """
        # Only consider available robots
        if robot.status.value != "Available":
            return 0.0
        
        # Calculate distances
        D1 = manhattan_distance((robot.x, robot.y), (task.source_x, task.source_y))
        D2 = manhattan_distance((task.source_x, task.source_y), (task.dest_x, task.dest_y))
        
        # Avoid division by zero
        total_distance = D1 + D2 + 0.1
        
        # Normalize factors
        speed_factor = (robot.velocity / 30.0) * self.alpha
        energy_factor = (robot.charge_percentage / 100.0) * self.beta
        
        # Weight capacity check
        weight_ok = 1.0 if robot.weight_threshold >= task.item_weight else 0.0
        
        # Urgency multiplier
        urgency_map = {
            "Normal": 1.0,
            "Urgent": 1.5,
            "Emergency": 2.0
        }
        urgency_multiplier = urgency_map.get(task.urgency.value, 1.0)
        
        # Calculate final rank
        rank = ((speed_factor + energy_factor) / total_distance) * weight_ok * urgency_multiplier
        
        return rank
    
    def find_optimal_robot(self, robots: List, task) -> Tuple[Optional[object], float]:
        """
        Find the best robot for a task using RRA
        
        Args:
            robots: List of robot objects
            task: Task object
        
        Returns:
            Tuple of (best_robot, best_score)
        """
        best_robot = None
        best_score = -1.0
        
        print(f"\n🔍 Finding optimal robot for Task {task.id} ({task.get_task_name()})")
        print("=" * 70)
        
        scores = []
        for robot in robots:
            score = self.calculate_robot_rank(robot, task)
            status_icon = "✅" if robot.status.value == "Available" else "❌"
            
            scores.append((robot, score))
            
            print(f"{robot.name}: {status_icon} | "
                  f"Speed: {robot.velocity:>2} | "
                  f"Charge: {robot.charge_percentage:>5.1f}% | "
                  f"Score: {score:>6.3f}")
            
            if score > best_score and robot.status.value == "Available":
                best_score = score
                best_robot = robot
        
        if best_robot:
            print(f"\n🎯 Selected Robot: {best_robot.name} (Score: {best_score:.3f})")
        else:
            print("\n❌ No available robots")
        
        print("=" * 70)
        
        return best_robot, best_score


class PathOptimizer:
    """Optimization utilities for paths"""
    
    @staticmethod
    def calculate_path_cost(path: List[Tuple[int, int]]) -> float:
        """
        Calculate total cost of a path
        
        Args:
            path: List of positions
        
        Returns:
            float: Path cost (distance)
        """
        if not path:
            return float('inf')
        return len(path) - 1
    
    @staticmethod
    def smooth_path(path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Smooth path by removing unnecessary waypoints
        
        Args:
            path: Original path
        
        Returns:
            Smoothed path
        """
        if len(path) <= 2:
            return path
        
        smoothed = [path[0]]
        
        for i in range(1, len(path) - 1):
            prev = path[i - 1]
            curr = path[i]
            next_pos = path[i + 1]
            
            # Check if direction changes
            dir1 = (curr[0] - prev[0], curr[1] - prev[1])
            dir2 = (next_pos[0] - curr[0], next_pos[1] - curr[1])
            
            if dir1 != dir2:
                smoothed.append(curr)
        
        smoothed.append(path[-1])
        return smoothed
    
    @staticmethod
    def calculate_path_metrics(path: List[Tuple[int, int]]) -> Dict:
        """
        Calculate various metrics for a path
        
        Args:
            path: List of positions
        
        Returns:
            Dictionary with metrics
        """
        if not path:
            return {
                'length': 0,
                'cost': float('inf'),
                'turns': 0,
                'straight_segments': 0
            }
        
        metrics = {
            'length': len(path),
            'cost': len(path) - 1,
            'turns': 0,
            'straight_segments': 0
        }
        
        if len(path) > 2:
            current_direction = None
            segment_length = 0
            
            for i in range(1, len(path)):
                direction = (path[i][0] - path[i-1][0], path[i][1] - path[i-1][1])
                
                if current_direction is None:
                    current_direction = direction
                    segment_length = 1
                elif direction == current_direction:
                    segment_length += 1
                else:
                    metrics['turns'] += 1
                    metrics['straight_segments'] += 1
                    current_direction = direction
                    segment_length = 1
            
            metrics['straight_segments'] += 1  # Last segment
        
        return metrics


class CollisionAvoidance:
    """Collision avoidance and path coordination"""
    
    def __init__(self):
        self.reserved_positions = {}  # {position: (robot_id, time)}
        self.robot_paths = {}  # {robot_id: path}
    
    def reserve_path(self, robot_id: str, path: List[Tuple[int, int]], 
                    start_time: int = 0) -> bool:
        """
        Reserve positions along a path for a robot
        
        Args:
            robot_id: Robot identifier
            path: Path to reserve
            start_time: Starting time
        
        Returns:
            bool: True if reservation successful
        """
        # Check for conflicts
        for i, pos in enumerate(path):
            time = start_time + i
            if pos in self.reserved_positions:
                other_robot, other_time = self.reserved_positions[pos]
                if other_robot != robot_id and abs(time - other_time) < 2:
                    return False
        
        # Reserve positions
        for i, pos in enumerate(path):
            time = start_time + i
            self.reserved_positions[pos] = (robot_id, time)
        
        self.robot_paths[robot_id] = path
        return True
    
    def release_path(self, robot_id: str):
        """Release reserved path for a robot"""
        if robot_id in self.robot_paths:
            path = self.robot_paths[robot_id]
            for pos in path:
                if pos in self.reserved_positions:
                    if self.reserved_positions[pos][0] == robot_id:
                        del self.reserved_positions[pos]
            del self.robot_paths[robot_id]
    
    def get_dynamic_obstacles(self, current_time: int, 
                             exclude_robot: str = None) -> List[Tuple[int, int]]:
        """
        Get current dynamic obstacles (other robot positions)
        
        Args:
            current_time: Current simulation time
            exclude_robot: Robot ID to exclude
        
        Returns:
            List of obstacle positions
        """
        obstacles = []
        for pos, (robot_id, time) in self.reserved_positions.items():
            if robot_id != exclude_robot and abs(time - current_time) < 2:
                obstacles.append(pos)
        return obstacles


# Convenience functions for backward compatibility
def calculate_robot_rank(robot, task, alpha=0.6, beta=0.4) -> float:
    """Legacy function - calculate robot rank"""
    rra = RobotRankingAlgorithm(alpha, beta)
    return rra.calculate_robot_rank(robot, task)


def find_optimal_robot(robots: List, task) -> Tuple[Optional[object], float]:
    """Legacy function - find optimal robot"""
    rra = RobotRankingAlgorithm()
    return rra.find_optimal_robot(robots, task)


def a_star_pathfinding(start: Tuple[int, int], end: Tuple[int, int], 
                       obstacles: List[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
    """Legacy function - A* pathfinding"""
    return PathfindingAlgorithms.a_star(start, end, obstacles)


def calculate_path_cost(path: List[Tuple[int, int]]) -> float:
    """Legacy function - calculate path cost"""
    return PathOptimizer.calculate_path_cost(path)