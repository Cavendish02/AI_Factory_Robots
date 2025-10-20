"""
AI Hospital Robot Management System - Main Module
Orchestrates the complete autonomous robot system for hospital logistics
"""

import pygame
import sys
import time
from typing import List, Optional, Tuple, Dict
from datetime import datetime

from hospital_config import get_map_positions, ROBOT_CONFIGS, TASK_TYPES
from robot_system import Robot, Task, TaskUrgency, RobotStatus, TaskStatus
from algorithms import (
    find_optimal_robot, 
    a_star_pathfinding, 
    PathfindingAlgorithms,
    PathOptimizer,
    CollisionAvoidance
)
from fuzzy_logic import FuzzyChargingSystem, simple_charging_check, BatteryManager
from visualization import HospitalVisualization


class SystemStatistics:
    """System-wide performance statistics"""
    
    def __init__(self):
        self.total_tasks_completed = 0
        self.total_tasks_failed = 0
        self.total_distance_traveled = 0.0
        self.total_battery_consumed = 0.0
        self.average_task_time = 0.0
        self.system_uptime = 0.0
        self.start_time = time.time()
        
        # Performance metrics
        self.tasks_by_urgency = {
            TaskUrgency.NORMAL: 0,
            TaskUrgency.URGENT: 0,
            TaskUrgency.EMERGENCY: 0
        }
        
        self.robot_utilization = {}
    
    def update(self, robots: List[Robot], tasks: List[Task]):
        """Update all statistics"""
        self.system_uptime = time.time() - self.start_time
        
        # Task statistics
        completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED.value]
        failed_tasks = [t for t in tasks if t.status == TaskStatus.CANCELLED.value]
        
        self.total_tasks_completed = len(completed_tasks)
        self.total_tasks_failed = len(failed_tasks)
        
        # Calculate average task time
        if completed_tasks:
            total_time = sum(t.get_duration() for t in completed_tasks)
            self.average_task_time = total_time / len(completed_tasks)
        
        # Robot statistics
        self.total_distance_traveled = sum(r.total_distance for r in robots)
        self.total_battery_consumed = sum(r.metrics.battery_consumed for r in robots)
        
        # Robot utilization
        for robot in robots:
            self.robot_utilization[robot.name] = {
                'tasks_completed': robot.completed_tasks,
                'distance_traveled': robot.total_distance,
                'battery_remaining': robot.charge_percentage,
                'utilization_rate': (robot.completed_tasks / max(1, self.total_tasks_completed)) * 100
            }
    
    def get_efficiency_score(self, total_tasks: int) -> float:
        """Calculate system efficiency (0-100)"""
        if total_tasks == 0:
            return 0.0
        return (self.total_tasks_completed / total_tasks) * 100
    
    def print_summary(self):
        """Print statistical summary"""
        print("\n" + "=" * 80)
        print("📊 SYSTEM PERFORMANCE SUMMARY")
        print("=" * 80)
        
        print(f"\n⏱️  System Uptime: {self.system_uptime:.1f} seconds")
        print(f"✅ Tasks Completed: {self.total_tasks_completed}")
        print(f"❌ Tasks Failed: {self.total_tasks_failed}")
        print(f"📏 Total Distance: {self.total_distance_traveled:.0f} units")
        print(f"🔋 Battery Consumed: {self.total_battery_consumed:.1f}%")
        print(f"⏱️  Average Task Time: {self.average_task_time:.2f}s")
        
        print("\n🤖 Robot Utilization:")
        for robot_name, stats in self.robot_utilization.items():
            print(f"   {robot_name}:")
            print(f"      Tasks: {stats['tasks_completed']}")
            print(f"      Distance: {stats['distance_traveled']:.0f}")
            print(f"      Battery: {stats['battery_remaining']:.1f}%")
            print(f"      Utilization: {stats['utilization_rate']:.1f}%")
        
        print("=" * 80)


class HospitalAISystem:
    """
    Main hospital AI system coordinating robots, tasks, and operations
    """
    
    def __init__(self):
        print("Initializing AI Factory Management System...")
        
        # Core components
        self.visualization = HospitalVisualization()
        self.robots: List[Robot] = []
        self.tasks: List[Task] = []
        self.statistics = SystemStatistics()
        
        # Subsystems
        self.fuzzy_system = FuzzyChargingSystem()
        self.pathfinding = PathfindingAlgorithms()
        self.collision_avoidance = CollisionAvoidance()
        
        # Control variables
        self.current_task_index = 0
        self.active_assignments = {}  # {task_id: (task, robot, path)}
        self.simulation_speed = 1.0
        self.paused = False
        
        # Initialize system
        self.initialize_robots()
        self.create_sample_tasks()
        
        print("✅ System initialized successfully!\n")
    
    def initialize_robots(self):
        """Initialize robots from map configuration"""
        positions = get_map_positions()
        
        # Use default positions if map doesn't specify
        if not positions['robots']:
            default_positions = {
                'R1': (1, 1), 
                'R2': (1, 5), 
                'R3': (6, 11), 
                'R4': (12, 6)
            }
        else:
            default_positions = positions['robots']
        
        print("🤖 Initializing Robots:")
        
        for robot_id, pos in default_positions.items():
            config = ROBOT_CONFIGS.get(robot_id, {})
            name = config.get('name', robot_id)
            color = config.get('color', None)
            
            robot = Robot(robot_id, pos[0], pos[1], name, color)
            
            # Apply configuration
            robot.velocity = config.get('speed', 1.0) * 20  # Scale to appropriate range
            robot.charge_percentage = config.get('initial_charge', 100)
            
            # Vary robot capabilities for diversity
            if robot_id == 'R1':
                robot.velocity = 25  # Fastest
                robot.charge_percentage = 75
                robot.weight_threshold = 8
            elif robot_id == 'R2':
                robot.velocity = 18  # Slowest but strongest
                robot.charge_percentage = 85
                robot.weight_threshold = 15
            elif robot_id == 'R3':
                robot.velocity = 22  # Balanced
                robot.charge_percentage = 90
                robot.weight_threshold = 10
            elif robot_id == 'R4':
                robot.velocity = 28  # Fast and efficient
                robot.charge_percentage = 80
                robot.weight_threshold = 6
            
            self.robots.append(robot)
            print(f"   ✓ {robot.name} ({robot.id}): Speed={robot.velocity}, "
                  f"Charge={robot.charge_percentage:.0f}%, Weight={robot.weight_threshold}kg")
        
        print(f"✅ {len(self.robots)} robots initialized\n")
    
    def create_sample_tasks(self):
        """Create sample tasks for demonstration"""
        sample_tasks = [
            {
                'source': (1, 13), 
                'destination': (12, 13),  # Changed to valid position
                'urgency': TaskUrgency.EMERGENCY, 
                'weight': 3, 
                'type': 'parts',
                'description': 'Emergency parts delivery to assembly line'
            },
            {
                'source': (1, 13), 
                'destination': (7, 7),  # Center position
                'urgency': TaskUrgency.NORMAL, 
                'weight': 8, 
                'type': 'materials',
                'description': 'Raw materials to production area'
            },
            {
                'source': (1, 13), 
                'destination': (12, 3),  # Top right area
                'urgency': TaskUrgency.URGENT, 
                'weight': 2, 
                'type': 'tools', 
                'description': 'Tools to maintenance station'
            },
            {
                'source': (1, 13), 
                'destination': (12, 8),  # Right middle
                'urgency': TaskUrgency.NORMAL, 
                'weight': 5, 
                'type': 'equipment',
                'description': 'Equipment to quality control'
            },
            {
                'source': (1, 13), 
                'destination': (7, 3),  # Top center
                'urgency': TaskUrgency.URGENT, 
                'weight': 1, 
                'type': 'documents',
                'description': 'Important records to administration'
            },
            {
                'source': (1, 13), 
                'destination': (7, 11),  # Bottom center
                'urgency': TaskUrgency.NORMAL, 
                'weight': 4, 
                'type': 'food',
                'description': 'Meal delivery to workers area'
            }
        ]
        
        print("📋 Creating Sample Tasks:")
        
        for i, task_data in enumerate(sample_tasks):
            task = Task(
                task_id=f"T{i+1:03d}",
                source=task_data['source'],
                destination=task_data['destination'],
                urgency=task_data['urgency'],
                item_weight=task_data['weight'],
                item_type=task_data['type']
            )
            self.tasks.append(task)
            print(f"   ✓ Task {task.id}: {task.get_task_name()} ({task.urgency.value})")
            print(f"      From {task_data['source']} → To {task_data['destination']}")
        
        print(f"✅ {len(self.tasks)} tasks created\n")
    
    def assign_next_task(self) -> Optional[Tuple]:
        """Assign the next pending task to an optimal robot"""
        # Find pending tasks
        pending_tasks = [t for t in self.tasks if t.status == TaskStatus.PENDING.value]
        
        if not pending_tasks:
            if self.current_task_index >= len(self.tasks):
                print("🎉 All tasks have been assigned!")
            return None
        
        # Get next pending task (prioritize by urgency)
        task = max(pending_tasks, key=lambda t: t.get_priority_score())
        
        print(f"\n{'=' * 80}")
        print(f"🎯 Assigning Task {task.id}: {task.get_task_name()}")
        print(f"   📍 From: ({task.source_x}, {task.source_y})")
        print(f"   🎯 To: ({task.dest_x}, {task.dest_y})")
        print(f"   ⚡ Urgency: {task.urgency.value}")
        print(f"   📦 Weight: {task.item_weight} kg")
        print(f"   🎖️  Priority Score: {task.get_priority_score()}")
        print(f"{'=' * 80}")
        
        # Find optimal robot using RRA
        best_robot, best_score = find_optimal_robot(self.robots, task)
        
        if not best_robot:
            print("   ⚠️  No available robots - will retry later")
            return None
        
        # Calculate path
        obstacles = self.visualization.obstacles
        
        # Path from robot to source
        path_to_source = self.pathfinding.a_star(
            (best_robot.x, best_robot.y), 
            (task.source_x, task.source_y), 
            obstacles
        )
        
        # Path from source to destination
        path_to_dest = self.pathfinding.a_star(
            (task.source_x, task.source_y), 
            (task.dest_x, task.dest_y), 
            obstacles
        )
        
        if not path_to_source:
            print(f"   ❌ No path from robot to source - marking as failed")
            task.cancel("No path from robot to source")
            return None
        
        if not path_to_dest:
            print(f"   ❌ No path from source to destination - marking as failed")
            task.cancel("No path from source to destination")
            return None
        
        # Combine paths
        full_path = path_to_source + path_to_dest[1:]  # Avoid duplicate source point
        
        if len(full_path) < 2:
            print(f"   ❌ Path too short - marking as failed")
            task.cancel("Invalid path")
            return None
        
        # Optimize path
        try:
            optimized_path = PathOptimizer.smooth_path(full_path)
            path_metrics = PathOptimizer.calculate_path_metrics(optimized_path)
        except Exception as e:
            print(f"   ⚠️  Path optimization failed: {e}, using original path")
            optimized_path = full_path
            path_metrics = {'turns': 0, 'straight_segments': 0}
        
        # Assign task to robot
        best_robot.assign_task(task, optimized_path)
        
        # Register with collision avoidance
        try:
            self.collision_avoidance.reserve_path(best_robot.id, optimized_path)
        except Exception as e:
            print(f"   ⚠️  Collision avoidance registration failed: {e}")
        
        # Store active assignment
        self.active_assignments[task.id] = (task, best_robot, optimized_path)
        
        print(f"   🛣️  Path calculated: {len(optimized_path)} steps")
        print(f"   📊 Path metrics: {path_metrics.get('turns', 0)} turns, "
              f"{path_metrics.get('straight_segments', 0)} segments")
        print(f"   ⏱️  Estimated time: {len(optimized_path) / best_robot.velocity:.1f}s")
        print(f"   🔋 Battery cost: ~{len(optimized_path) * best_robot.battery_drain_rate:.1f}%")
        
        self.current_task_index += 1
        
        return task, best_robot, optimized_path
    
    def update_charging_system(self):
        """Update robot charging status using fuzzy logic"""
        available_robots = [r for r in self.robots 
                          if r.status == RobotStatus.AVAILABLE]
        
        print("\n🔋 Battery Status Check:")
        print("-" * 80)
        
        for robot in self.robots:
            # Get charging priority from fuzzy system
            priority, score, details = self.fuzzy_system.get_charging_priority(
                robot, 
                len(available_robots)
            )
            
            battery_status = robot.get_battery_status()
            
            print(f"   {battery_status['icon']} {robot.name}: "
                  f"{robot.charge_percentage:.1f}% - {battery_status['status']} "
                  f"(Priority: {priority}, Score: {score:.2f})")
            
            # Handle charging based on priority
            if priority == "CR1":  # Critical
                if robot.status != RobotStatus.CHARGING:
                    print(f"      ⚠️  CRITICAL! Initiating emergency charging...")
                    robot.status = RobotStatus.CHARGING
                    
                    # Cancel current task if any
                    if robot.current_task:
                        robot.cancel_task("Critical battery level")
            
            elif priority == "CR2":  # High
                if robot.status == RobotStatus.AVAILABLE:
                    print(f"      🔶 Scheduling charging soon...")
            
            # Simulate charging for demo purposes
            if robot.status == RobotStatus.CHARGING:
                robot.charge_battery()
                if robot.charge_percentage >= 80:
                    print(f"      ✅ {robot.name} fully charged!")
        
        print("-" * 80)
    
    def check_completed_tasks(self):
        """Check for completed tasks and clean up"""
        completed_ids = []
        
        for task_id, (task, robot, path) in self.active_assignments.items():
            if task.status == TaskStatus.COMPLETED.value:
                completed_ids.append(task_id)
                self.collision_avoidance.release_path(robot.id)
                
                print(f"✅ Task {task.id} completed by {robot.name}")
                print(f"   Duration: {task.get_duration():.1f}s")
                print(f"   Distance: {len(path)} steps")
        
        # Remove completed assignments
        for task_id in completed_ids:
            del self.active_assignments[task_id]
    
    def update_system(self, delta_time: float):
        """Update all system components"""
        # Update robots
        for robot in self.robots:
            robot.update(delta_time)
        
        # Check for completed tasks
        self.check_completed_tasks()
        
        # Update statistics
        self.statistics.update(self.robots, self.tasks)
    
    def draw_scene(self):
        """Draw complete scene"""
        # Prepare dashboard info
        current_task_info = ""
        if self.active_assignments:
            # Show info for first active task
            task, robot, _ = list(self.active_assignments.values())[0]
            current_task_info = f"{robot.name} transporting {task.get_task_name()}"
        
        # Draw main dashboard (includes everything)
        self.visualization.draw_dashboard(self.robots, self.tasks, current_task_info)
        
        # Draw all active paths and animations on the map
        for task_id, (task, robot, path) in self.active_assignments.items():
            if task.status == TaskStatus.IN_PROGRESS.value:
                # Draw path with animation
                self.visualization.draw_path(path, animated=True)
                self.visualization.draw_task_animation(task, robot)
        
        # Draw robots on top
        self.visualization.draw_robots(self.robots)
        
        # Update display
        self.visualization.update()
    
    def print_final_report(self):
        """Print comprehensive final report"""
        print("\n" + "=" * 80)
        print("AI FACTORY SYSTEM - FINAL PERFORMANCE REPORT")
        print("=" * 80)
        
        # Task summary
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED.value)
        cancelled = sum(1 for t in self.tasks if t.status == TaskStatus.CANCELLED.value)
        pending = sum(1 for t in self.tasks if t.status == TaskStatus.PENDING.value)
        
        print(f"\n📋 Task Summary:")
        print(f"   ✅ Completed: {completed}/{len(self.tasks)}")
        print(f"   ❌ Cancelled: {cancelled}")
        print(f"   ⏳ Pending: {pending}")
        
        # Robot performance
        print(f"\n🤖 Robot Performance:")
        for robot in self.robots:
            efficiency = (robot.completed_tasks / max(1, completed)) * 100
            print(f"   {robot.name}:")
            print(f"      Tasks: {robot.completed_tasks}")
            print(f"      Distance: {robot.total_distance:.0f} units")
            print(f"      Battery: {robot.charge_percentage:.0f}%")
            print(f"      Efficiency: {efficiency:.1f}%")
        
        # System statistics
        self.statistics.print_summary()
        
        # Overall assessment
        efficiency = self.statistics.get_efficiency_score(len(self.tasks))
        
        print(f"\n🎯 Overall System Efficiency: {efficiency:.1f}%")
        
        if efficiency >= 90:
            print("   ⭐⭐⭐⭐⭐ EXCELLENT! System performing at peak efficiency!")
        elif efficiency >= 75:
            print("   ⭐⭐⭐⭐ VERY GOOD! System is highly efficient!")
        elif efficiency >= 60:
            print("   ⭐⭐⭐ GOOD! System is performing well with room for improvement!")
        elif efficiency >= 40:
            print("   ⭐⭐ FAIR! System needs optimization!")
        else:
            print("   ⭐ NEEDS IMPROVEMENT! System requires significant optimization!")
        
        print("\n" + "=" * 80)
        print("Thank you for using the AI Factory Management System!")
        print("=" * 80 + "\n")
    
    def run(self):
        """Main simulation loop"""
        print("🚀 Starting AI Factory Management System...")
        print("=" * 80)
        print("💡 Controls:")
        print("   SPACE - Assign next task")
        print("   P     - Pause/Resume")
        print("   R     - Reset simulation")
        print("   ESC   - Exit system")
        print("=" * 80 + "\n")
        
        auto_assign_timer = 0
        charging_check_timer = 0
        
        AUTO_ASSIGN_INTERVAL = 3000  # 3 seconds
        CHARGING_CHECK_INTERVAL = 10000  # 10 seconds
        
        while self.visualization.running:
            delta_time = self.visualization.clock.get_time() / 1000.0  # Convert to seconds
            
            # Handle events
            event_result = self.visualization.handle_events()
            
            if event_result == "quit":
                break
            elif event_result == "next_task":
                self.assign_next_task()
            elif event_result == "pause":
                self.paused = not self.paused
                status = "PAUSED" if self.paused else "RESUMED"
                print(f"\n⏸️  System {status}")
            elif event_result == "reset":
                print("\n🔄 Resetting system...")
                self.__init__()
            
            if not self.paused:
                # Auto-assign tasks
                auto_assign_timer += self.visualization.clock.get_time()
                if auto_assign_timer > AUTO_ASSIGN_INTERVAL:
                    if not self.active_assignments and self.current_task_index < len(self.tasks):
                        self.assign_next_task()
                    auto_assign_timer = 0
                
                # Periodic charging check
                charging_check_timer += self.visualization.clock.get_time()
                if charging_check_timer > CHARGING_CHECK_INTERVAL:
                    self.update_charging_system()
                    charging_check_timer = 0
                
                # Update system
                self.update_system(delta_time)
            
            # Draw scene
            self.draw_scene()
            
            # Control frame rate
            self.visualization.clock.tick(60)  # 60 FPS
        
        # Print final report and cleanup
        self.print_final_report()
        pygame.quit()
        sys.exit()


def main():
    """Entry point for the application"""
    try:
        hospital_system = HospitalAISystem()
        hospital_system.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  System interrupted by user")
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ System error: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()