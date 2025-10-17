"""
Robot System Module
Defines robot and task classes with comprehensive functionality
"""

import pygame
import numpy as np
from enum import Enum
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import time


class RobotStatus(Enum):
    """Robot operational status"""
    AVAILABLE = "Available"
    BUSY = "Busy"
    CHARGING = "Charging"
    MAINTENANCE = "Maintenance"
    IDLE = "Idle"


class TaskUrgency(Enum):
    """Task urgency levels"""
    NORMAL = "Normal"
    URGENT = "Urgent"
    EMERGENCY = "Emergency"


class TaskStatus(Enum):
    """Task completion status"""
    PENDING = "Pending"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""
    tasks_completed: int = 0
    total_distance: float = 0.0
    total_time: float = 0.0
    average_speed: float = 0.0
    battery_consumed: float = 0.0
    successful_deliveries: int = 0
    failed_deliveries: int = 0


class Robot:
    """
    Autonomous robot with navigation, task execution, and battery management
    """
    
    def __init__(self, robot_id: str, x: int, y: int, name: str, color: Tuple[int, int, int] = None):
        # Basic properties
        self.id = robot_id
        self.name = name
        self.x, self.y = x, y
        self.initial_position = (x, y)
        
        # Status and capabilities
        self.status = RobotStatus.AVAILABLE
        self.velocity = np.random.randint(15, 30)
        self.max_velocity = 30
        self.charge_percentage = np.random.uniform(70, 100)
        self.max_charge = 100.0
        self.weight_threshold = np.random.randint(8, 15)  # kg
        
        # Task management
        self.current_task = None
        self.path = []
        self.task_queue = []
        
        # Movement and animation
        self.target_x, self.target_y = x, y
        self.move_progress = 0.0
        self.movement_speed = 0.15  # Smooth animation speed
        
        # Battery management
        self.battery_drain_rate = 0.08  # Per movement step
        self.charging_rate = 2.0  # Per update when charging
        self.low_battery_threshold = 20.0
        self.critical_battery_threshold = 10.0
        
        # Performance tracking
        self.completed_tasks = 0
        self.total_distance = 0.0
        self.metrics = PerformanceMetrics()
        
        # Visual properties
        self.color = color or self._get_default_color()
        self.animation_frame = 0
        
        # Timing
        self.task_start_time = None
        self.last_update_time = time.time()
    
    def _get_default_color(self) -> Tuple[int, int, int]:
        """Get default color based on robot ID"""
        color_map = {
            'R1': (255, 70, 70),
            'R2': (70, 220, 70),
            'R3': (70, 150, 255),
            'R4': (255, 200, 50)
        }
        return color_map.get(self.id, (128, 128, 128))
    
    def update(self, delta_time: float = 0.016):
        """
        Update robot state each frame
        
        Args:
            delta_time: Time elapsed since last update
        """
        self.animation_frame = (self.animation_frame + 1) % 60
        
        if self.status == RobotStatus.BUSY and self.path:
            self.move_along_path()
            self.consume_battery()
        elif self.status == RobotStatus.CHARGING:
            self.charge_battery()
        
        # Update metrics
        current_time = time.time()
        if self.task_start_time:
            self.metrics.total_time = current_time - self.task_start_time
    
    def move_along_path(self):
        """Move robot smoothly along the planned path"""
        if not self.path:
            return
        
        next_x, next_y = self.path[0]
        
        # Smooth movement
        if (self.x, self.y) != (next_x, next_y):
            dx = next_x - self.x
            dy = next_y - self.y
            
            # Calculate movement direction
            if abs(dx) > abs(dy):
                self.x += 1 if dx > 0 else -1
            else:
                self.y += 1 if dy > 0 else -1
            
            self.total_distance += 1
            self.metrics.total_distance += 1
        else:
            # Reached waypoint, move to next
            self.path.pop(0)
            
            # Check if reached final destination
            if not self.path and self.current_task:
                self.complete_task()
    
    def consume_battery(self):
        """Consume battery during movement"""
        # Battery drain varies with velocity
        velocity_factor = self.velocity / self.max_velocity
        drain = self.battery_drain_rate * velocity_factor
        
        self.charge_percentage = max(0, self.charge_percentage - drain)
        self.metrics.battery_consumed += drain
        
        # Check for critical battery
        if self.charge_percentage <= self.critical_battery_threshold:
            print(f"⚠️  {self.name}: Critical battery level! ({self.charge_percentage:.1f}%)")
            if self.status == RobotStatus.BUSY:
                self.status = RobotStatus.CHARGING
    
    def charge_battery(self):
        """Charge robot battery"""
        if self.charge_percentage < self.max_charge:
            self.charge_percentage = min(self.max_charge, 
                                        self.charge_percentage + self.charging_rate)
        
        # Resume operation when sufficiently charged
        if self.charge_percentage >= 80.0:
            self.status = RobotStatus.AVAILABLE
            print(f"✅ {self.name}: Battery charged to {self.charge_percentage:.1f}%")
    
    def assign_task(self, task, path: List[Tuple[int, int]]):
        """
        Assign a task to the robot
        
        Args:
            task: Task object to assign
            path: Navigation path for the task
        """
        self.current_task = task
        self.path = path.copy()
        self.status = RobotStatus.BUSY
        self.task_start_time = time.time()
        
        task.status = TaskStatus.IN_PROGRESS.value
        task.assigned_robot = self
        task.assignment_time = time.time()
        
        print(f"📋 {self.name} assigned to Task {task.id}: {task.get_task_name()}")
    
    def complete_task(self):
        """Complete the current task"""
        if not self.current_task:
            return
        
        self.current_task.complete()
        self.completed_tasks += 1
        self.metrics.tasks_completed += 1
        self.metrics.successful_deliveries += 1
        
        # Calculate performance
        if self.metrics.total_time > 0:
            self.metrics.average_speed = self.metrics.total_distance / self.metrics.total_time
        
        print(f"✅ {self.name} completed Task {self.current_task.id}")
        
        self.current_task = None
        self.status = RobotStatus.AVAILABLE
        self.task_start_time = None
    
    def cancel_task(self, reason: str = "Unknown"):
        """Cancel current task"""
        if self.current_task:
            self.current_task.cancel(reason)
            self.metrics.failed_deliveries += 1
            print(f"❌ {self.name} cancelled Task {self.current_task.id}: {reason}")
            
            self.current_task = None
            self.path = []
            self.status = RobotStatus.AVAILABLE
    
    def return_to_base(self, base_position: Tuple[int, int]):
        """Return robot to base/charging station"""
        self.path = [base_position]
        self.status = RobotStatus.BUSY
    
    def get_battery_status(self) -> Dict:
        """Get detailed battery status"""
        if self.charge_percentage >= 60:
            status = "Good"
            icon = "🟢"
            color = (80, 220, 100)
        elif self.charge_percentage >= 30:
            status = "Medium"
            icon = "🟡"
            color = (255, 200, 50)
        elif self.charge_percentage >= 15:
            status = "Low"
            icon = "🟠"
            color = (255, 150, 50)
        else:
            status = "Critical"
            icon = "🔴"
            color = (255, 80, 80)
        
        return {
            'percentage': self.charge_percentage,
            'status': status,
            'icon': icon,
            'color': color,
            'needs_charging': self.charge_percentage < self.low_battery_threshold
        }
    
    def get_status_info(self) -> str:
        """Get formatted status information"""
        status_icons = {
            RobotStatus.AVAILABLE: "🟢",
            RobotStatus.BUSY: "🔴",
            RobotStatus.CHARGING: "🔋",
            RobotStatus.MAINTENANCE: "🔧",
            RobotStatus.IDLE: "🟡"
        }
        
        icon = status_icons.get(self.status, "❓")
        return f"{icon} {self.name} | {self.status.value} | Battery: {self.charge_percentage:.0f}%"
    
    def draw(self, screen, font):
        """
        Draw robot on screen with enhanced visuals
        
        Args:
            screen: Pygame screen surface
            font: Pygame font for text rendering
        """
        center_x = self.x * 40 + 20
        center_y = self.y * 40 + 20
        
        # Draw robot shadow
        shadow_offset = 3
        pygame.draw.circle(screen, (50, 50, 50, 100), 
                         (center_x + shadow_offset, center_y + shadow_offset), 16)
        
        # Draw robot body with pulsing animation if busy
        radius = 15
        if self.status == RobotStatus.BUSY:
            pulse = abs((self.animation_frame % 30) - 15) / 15.0
            radius = int(15 + pulse * 2)
        
        pygame.draw.circle(screen, self.color, (center_x, center_y), radius)
        
        # Draw inner circle
        inner_color = (255, 255, 255) if self.status == RobotStatus.AVAILABLE else (200, 200, 200)
        pygame.draw.circle(screen, inner_color, (center_x, center_y), radius - 5)
        
        # Draw status indicator
        if self.status == RobotStatus.CHARGING:
            # Lightning bolt for charging
            pygame.draw.circle(screen, (255, 255, 0), (center_x, center_y), 8)
        elif self.status == RobotStatus.BUSY:
            # Arrow for busy
            pygame.draw.circle(screen, (255, 100, 100), (center_x, center_y), 6)
        
        # Draw battery bar
        battery_status = self.get_battery_status()
        bar_width = 30
        bar_height = 5
        bar_x = self.x * 40 + 5
        bar_y = self.y * 40 - 12
        
        # Battery background
        pygame.draw.rect(screen, (80, 80, 80), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Battery fill
        fill_width = int((bar_width - 2) * self.charge_percentage / 100)
        pygame.draw.rect(screen, battery_status['color'], 
                        (bar_x + 1, bar_y + 1, fill_width, bar_height - 2))
        
        # Draw robot name
        name_text = font.render(self.name, True, (0, 0, 0))
        name_rect = name_text.get_rect(center=(center_x, center_y + 28))
        screen.blit(name_text, name_rect)
        
        # Draw battery percentage
        charge_text = font.render(f"{self.charge_percentage:.0f}%", True, (0, 0, 0))
        charge_rect = charge_text.get_rect(center=(center_x, bar_y - 8))
        screen.blit(charge_text, charge_rect)
        
        # Draw path if exists
        if self.path and len(self.path) > 0:
            # Draw small dots along path
            for pos in self.path[:5]:  # Show next 5 waypoints
                dot_x = pos[0] * 40 + 20
                dot_y = pos[1] * 40 + 20
                pygame.draw.circle(screen, (150, 150, 200), (dot_x, dot_y), 3)


class Task:
    """
    Task/Delivery assignment for robots
    """
    
    # Task type definitions
    TASK_TYPES = {
        "medicine": {"name": "Medicine Delivery", "icon": "💊", "priority": 3},
        "blood": {"name": "Blood Samples", "icon": "🩸", "priority": 4},
        "supplies": {"name": "Medical Supplies", "icon": "📦", "priority": 2},
        "equipment": {"name": "Medical Equipment", "icon": "🔧", "priority": 2},
        "food": {"name": "Meal Delivery", "icon": "🍽️", "priority": 1},
        "documents": {"name": "Document Delivery", "icon": "📄", "priority": 1},
        "lab_samples": {"name": "Lab Samples", "icon": "🧪", "priority": 4}
    }
    
    def __init__(self, task_id: str, source: Tuple[int, int], destination: Tuple[int, int],
                 urgency: TaskUrgency, item_weight: float, item_type: str):
        # Basic properties
        self.id = task_id
        self.source_x, self.source_y = source
        self.dest_x, self.dest_y = destination
        self.urgency = urgency
        self.item_weight = item_weight
        self.item_type = item_type
        
        # Status tracking
        self.status = TaskStatus.PENDING.value
        self.assigned_robot = None
        
        # Timing
        self.creation_time = time.time()
        self.assignment_time = None
        self.completion_time = None
        self.cancellation_time = None
        
        # Additional info
        self.cancellation_reason = None
        self.attempts = 0
        self.max_attempts = 3
    
    def get_task_name(self) -> str:
        """Get human-readable task name"""
        task_info = self.TASK_TYPES.get(self.item_type, {"name": "Unknown Task", "icon": "❓"})
        return f"{task_info['icon']} {task_info['name']}"
    
    def get_priority_score(self) -> int:
        """Get task priority score"""
        base_priority = self.TASK_TYPES.get(self.item_type, {}).get('priority', 1)
        
        urgency_multiplier = {
            TaskUrgency.NORMAL: 1,
            TaskUrgency.URGENT: 2,
            TaskUrgency.EMERGENCY: 3
        }.get(self.urgency, 1)
        
        return base_priority * urgency_multiplier
    
    def complete(self):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED.value
        self.completion_time = time.time()
        print(f"✅ Task {self.id} completed: {self.get_task_name()}")
    
    def cancel(self, reason: str = "Unknown"):
        """Cancel task"""
        self.status = TaskStatus.CANCELLED.value
        self.cancellation_time = time.time()
        self.cancellation_reason = reason
        print(f"❌ Task {self.id} cancelled: {reason}")
    
    def retry(self):
        """Retry failed task"""
        if self.attempts < self.max_attempts:
            self.attempts += 1
            self.status = TaskStatus.PENDING.value
            self.assigned_robot = None
            return True
        return False
    
    def get_duration(self) -> float:
        """
        Calculate task duration in seconds
        
        Returns:
            float: Duration in seconds, or 0 if not completed
        """
        if self.completion_time and self.creation_time:
            return self.completion_time - self.creation_time
        elif self.cancellation_time and self.creation_time:
            return self.cancellation_time - self.creation_time
        return 0.0
    
    def get_wait_time(self) -> float:
        """Get time waiting for assignment"""
        if self.assignment_time:
            return self.assignment_time - self.creation_time
        return time.time() - self.creation_time
    
    def get_execution_time(self) -> float:
        """Get time from assignment to completion"""
        if self.completion_time and self.assignment_time:
            return self.completion_time - self.assignment_time
        return 0.0
    
    def get_status_info(self) -> str:
        """Get formatted status information"""
        urgency_icons = {
            TaskUrgency.NORMAL: "🟢",
            TaskUrgency.URGENT: "🟡",
            TaskUrgency.EMERGENCY: "🔴"
        }
        
        icon = urgency_icons.get(self.urgency, "❓")
        robot_info = f" → {self.assigned_robot.name}" if self.assigned_robot else ""
        
        return f"{icon} Task {self.id}: {self.get_task_name()} | {self.status}{robot_info}"
    
    def __repr__(self) -> str:
        return f"Task({self.id}, {self.item_type}, {self.urgency.value}, {self.status})"