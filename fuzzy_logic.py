"""
Fuzzy Logic Module
Implements intelligent charging decision system using fuzzy logic
"""

import numpy as np
from typing import Optional, Dict, Tuple
from enum import Enum

try:
    import skfuzzy as fuzz
    from skfuzzy import control as ctrl
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False
    print("⚠️  Warning: scikit-fuzzy library not installed. Using fallback charging system.")
    print("   Install with: pip install scikit-fuzzy")


class ChargingPriority(Enum):
    """Charging priority levels"""
    CRITICAL = "CR1"      # Immediate charging required
    HIGH = "CR2"          # Charging needed soon
    MEDIUM = "CR3"        # Charging recommended
    LOW = "No Charge"     # No charging needed


class FuzzyChargingSystem:
    """
    Fuzzy Logic-based charging decision system
    Uses charge level, velocity, and workload to determine charging priority
    """
    
    def __init__(self):
        self.available = FUZZY_AVAILABLE
        
        if not FUZZY_AVAILABLE:
            print("   Using fallback rule-based charging system")
            return
        
        try:
            self._initialize_fuzzy_system()
            print("✅ Fuzzy charging system initialized successfully")
        except Exception as e:
            print(f"⚠️  Error initializing fuzzy system: {e}")
            self.available = False
    
    def _initialize_fuzzy_system(self):
        """Initialize fuzzy logic variables and rules"""
        
        # Define fuzzy input variables
        self.charge = ctrl.Antecedent(np.arange(0, 101, 1), 'charge')
        self.velocity = ctrl.Antecedent(np.arange(0, 31, 1), 'velocity')
        self.workload = ctrl.Antecedent(np.arange(0, 21, 1), 'workload')
        self.distance_to_station = ctrl.Antecedent(np.arange(0, 51, 1), 'distance')
        
        # Define fuzzy output variable
        self.charge_priority = ctrl.Consequent(np.arange(0, 11, 1), 'priority')
        
        # Charge level membership functions
        self.charge['critical'] = fuzz.trapmf(self.charge.universe, [0, 0, 15, 25])
        self.charge['low'] = fuzz.trimf(self.charge.universe, [15, 30, 45])
        self.charge['medium'] = fuzz.trimf(self.charge.universe, [35, 50, 65])
        self.charge['high'] = fuzz.trimf(self.charge.universe, [55, 70, 85])
        self.charge['full'] = fuzz.trapmf(self.charge.universe, [75, 90, 100, 100])
        
        # Velocity membership functions
        self.velocity['slow'] = fuzz.trapmf(self.velocity.universe, [0, 0, 8, 15])
        self.velocity['medium'] = fuzz.trimf(self.velocity.universe, [12, 18, 24])
        self.velocity['fast'] = fuzz.trapmf(self.velocity.universe, [20, 25, 30, 30])
        
        # Workload membership functions
        self.workload['light'] = fuzz.trapmf(self.workload.universe, [0, 0, 3, 7])
        self.workload['moderate'] = fuzz.trimf(self.workload.universe, [5, 10, 15])
        self.workload['heavy'] = fuzz.trapmf(self.workload.universe, [12, 17, 20, 20])
        
        # Distance to charging station membership functions
        self.distance_to_station['near'] = fuzz.trapmf(self.distance_to_station.universe, [0, 0, 5, 12])
        self.distance_to_station['medium'] = fuzz.trimf(self.distance_to_station.universe, [10, 20, 30])
        self.distance_to_station['far'] = fuzz.trapmf(self.distance_to_station.universe, [25, 35, 50, 50])
        
        # Priority output membership functions
        self.charge_priority['very_low'] = fuzz.trapmf(self.charge_priority.universe, [0, 0, 1, 2])
        self.charge_priority['low'] = fuzz.trimf(self.charge_priority.universe, [1, 2.5, 4])
        self.charge_priority['medium'] = fuzz.trimf(self.charge_priority.universe, [3, 5, 7])
        self.charge_priority['high'] = fuzz.trimf(self.charge_priority.universe, [6, 7.5, 9])
        self.charge_priority['critical'] = fuzz.trapmf(self.charge_priority.universe, [8, 9, 10, 10])
        
        # Define fuzzy rules
        self.rules = self._create_fuzzy_rules()
        
        # Create control system
        self.charging_ctrl = ctrl.ControlSystem(self.rules)
        self.charging_system = ctrl.ControlSystemSimulation(self.charging_ctrl)
    
    def _create_fuzzy_rules(self):
        """Create comprehensive fuzzy rule set"""
        rules = []
        
        # Critical charge rules (highest priority)
        rules.append(ctrl.Rule(
            self.charge['critical'],
            self.charge_priority['critical']
        ))
        
        rules.append(ctrl.Rule(
            self.charge['low'] & self.distance_to_station['far'],
            self.charge_priority['critical']
        ))
        
        # High priority rules
        rules.append(ctrl.Rule(
            self.charge['low'] & self.workload['heavy'],
            self.charge_priority['high']
        ))
        
        rules.append(ctrl.Rule(
            self.charge['low'] & self.velocity['slow'],
            self.charge_priority['high']
        ))
        
        rules.append(ctrl.Rule(
            self.charge['medium'] & self.workload['heavy'] & self.velocity['slow'],
            self.charge_priority['high']
        ))
        
        # Medium priority rules
        rules.append(ctrl.Rule(
            self.charge['medium'] & self.workload['moderate'],
            self.charge_priority['medium']
        ))
        
        rules.append(ctrl.Rule(
            self.charge['medium'] & self.distance_to_station['near'],
            self.charge_priority['medium']
        ))
        
        rules.append(ctrl.Rule(
            self.charge['low'] & self.workload['light'] & self.velocity['fast'],
            self.charge_priority['medium']
        ))
        
        # Low priority rules
        rules.append(ctrl.Rule(
            self.charge['high'] & self.workload['light'],
            self.charge_priority['low']
        ))
        
        rules.append(ctrl.Rule(
            self.charge['medium'] & self.velocity['fast'] & self.workload['light'],
            self.charge_priority['low']
        ))
        
        rules.append(ctrl.Rule(
            self.charge['high'] & self.velocity['fast'],
            self.charge_priority['low']
        ))
        
        # Very low priority rules
        rules.append(ctrl.Rule(
            self.charge['full'],
            self.charge_priority['very_low']
        ))
        
        rules.append(ctrl.Rule(
            self.charge['high'] & self.workload['light'] & self.velocity['fast'],
            self.charge_priority['very_low']
        ))
        
        return rules
    
    def get_charging_priority(self, robot, available_robots_count: int, 
                            distance_to_station: float = 5.0) -> Tuple[str, float, Dict]:
        """
        Determine charging priority for a robot
        
        Args:
            robot: Robot object
            available_robots_count: Number of available robots
            distance_to_station: Distance to nearest charging station
        
        Returns:
            Tuple of (priority_level, priority_score, details)
        """
        if not self.available:
            return self._fallback_charging_decision(robot, available_robots_count)
        
        try:
            # Prepare inputs
            charge_level = max(0, min(100, robot.charge_percentage))
            velocity = max(0, min(30, robot.velocity))
            workload = max(0, min(20, getattr(robot, 'completed_tasks', 0)))
            distance = max(0, min(50, distance_to_station))
            
            # Set fuzzy system inputs
            self.charging_system.input['charge'] = charge_level
            self.charging_system.input['velocity'] = velocity
            self.charging_system.input['workload'] = workload
            self.charging_system.input['distance'] = distance
            
            # Compute result
            self.charging_system.compute()
            priority_score = self.charging_system.output['priority']
            
            # Convert score to priority level
            if priority_score >= 8.5:
                priority_level = ChargingPriority.CRITICAL.value
            elif priority_score >= 6.0:
                priority_level = ChargingPriority.HIGH.value
            elif priority_score >= 3.5:
                priority_level = ChargingPriority.MEDIUM.value
            else:
                priority_level = ChargingPriority.LOW.value
            
            # Additional details
            details = {
                'priority_score': round(priority_score, 2),
                'charge_level': charge_level,
                'velocity': velocity,
                'workload': workload,
                'distance_to_station': distance,
                'available_robots': available_robots_count,
                'decision_method': 'fuzzy_logic'
            }
            
            return priority_level, priority_score, details
            
        except Exception as e:
            print(f"⚠️  Fuzzy system error: {e}. Using fallback system.")
            return self._fallback_charging_decision(robot, available_robots_count)
    
    def _fallback_charging_decision(self, robot, available_robots_count: int) -> Tuple[str, float, Dict]:
        """
        Fallback rule-based charging decision when fuzzy logic is unavailable
        
        Args:
            robot: Robot object
            available_robots_count: Number of available robots
        
        Returns:
            Tuple of (priority_level, priority_score, details)
        """
        charge = robot.charge_percentage
        velocity = robot.velocity
        
        # Simple rule-based decision
        if charge < 15:
            priority_level = ChargingPriority.CRITICAL.value
            priority_score = 10.0
        elif charge < 25 and velocity < 15:
            priority_level = ChargingPriority.CRITICAL.value
            priority_score = 9.0
        elif charge < 35:
            priority_level = ChargingPriority.HIGH.value
            priority_score = 7.5
        elif charge < 50 and available_robots_count > 2:
            priority_level = ChargingPriority.HIGH.value
            priority_score = 6.5
        elif charge < 60:
            priority_level = ChargingPriority.MEDIUM.value
            priority_score = 4.5
        elif charge < 75:
            priority_level = ChargingPriority.LOW.value
            priority_score = 2.5
        else:
            priority_level = ChargingPriority.LOW.value
            priority_score = 1.0
        
        details = {
            'priority_score': priority_score,
            'charge_level': charge,
            'velocity': velocity,
            'available_robots': available_robots_count,
            'decision_method': 'rule_based_fallback'
        }
        
        return priority_level, priority_score, details
    
    def get_charging_recommendation(self, robot, available_robots_count: int) -> str:
        """
        Get human-readable charging recommendation
        
        Args:
            robot: Robot object
            available_robots_count: Number of available robots
        
        Returns:
            str: Charging recommendation message
        """
        priority, score, details = self.get_charging_priority(robot, available_robots_count)
        
        recommendations = {
            ChargingPriority.CRITICAL.value: 
                f"🔴 CRITICAL: Immediate charging required! (Score: {score:.1f})",
            ChargingPriority.HIGH.value: 
                f"🟠 HIGH: Schedule charging within 10 minutes (Score: {score:.1f})",
            ChargingPriority.MEDIUM.value: 
                f"🟡 MEDIUM: Charging recommended soon (Score: {score:.1f})",
            ChargingPriority.LOW.value: 
                f"🟢 LOW: No immediate charging needed (Score: {score:.1f})"
        }
        
        return recommendations.get(priority, f"Unknown priority: {priority}")
    
    def visualize_membership_functions(self):
        """Visualize fuzzy membership functions (requires matplotlib)"""
        if not self.available:
            print("Fuzzy system not available")
            return
        
        try:
            import matplotlib.pyplot as plt
            
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))
            fig.suptitle('Fuzzy Membership Functions', fontsize=16, fontweight='bold')
            
            # Charge membership functions
            self.charge.view(ax=axes[0, 0])
            axes[0, 0].set_title('Battery Charge Level')
            
            # Velocity membership functions
            self.velocity.view(ax=axes[0, 1])
            axes[0, 1].set_title('Robot Velocity')
            
            # Workload membership functions
            self.workload.view(ax=axes[1, 0])
            axes[1, 0].set_title('Workload (Tasks Completed)')
            
            # Priority output membership functions
            self.charge_priority.view(ax=axes[1, 1])
            axes[1, 1].set_title('Charging Priority Output')
            
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            print("matplotlib not available for visualization")
        except Exception as e:
            print(f"Error visualizing membership functions: {e}")


# Convenience function for backward compatibility
def simple_charging_check(robot, available_robots_count: int) -> str:
    """
    Simple charging check (legacy function)
    
    Args:
        robot: Robot object
        available_robots_count: Number of available robots
    
    Returns:
        str: Charging priority level
    """
    fuzzy_system = FuzzyChargingSystem()
    priority, _, _ = fuzzy_system.get_charging_priority(robot, available_robots_count)
    return priority


# Battery management utilities
class BatteryManager:
    """Battery monitoring and management utilities"""
    
    @staticmethod
    def estimate_remaining_time(charge_percentage: float, current_velocity: float) -> float:
        """
        Estimate remaining operation time in minutes
        
        Args:
            charge_percentage: Current charge percentage
            current_velocity: Current velocity
        
        Returns:
            float: Estimated remaining time in minutes
        """
        if current_velocity <= 0:
            return float('inf')
        
        # Simplified model: higher velocity drains battery faster
        base_drain_rate = 0.5  # % per minute at velocity 15
        velocity_factor = current_velocity / 15.0
        drain_rate = base_drain_rate * velocity_factor
        
        if drain_rate <= 0:
            return float('inf')
        
        return charge_percentage / drain_rate
    
    @staticmethod
    def calculate_charge_time(current_charge: float, target_charge: float, 
                            charging_rate: float = 5.0) -> float:
        """
        Calculate time needed to charge from current to target level
        
        Args:
            current_charge: Current charge percentage
            target_charge: Target charge percentage
            charging_rate: Charging rate (% per minute)
        
        Returns:
            float: Time needed in minutes
        """
        charge_needed = max(0, target_charge - current_charge)
        return charge_needed / charging_rate
    
    @staticmethod
    def get_battery_health_status(charge_percentage: float) -> Dict:
        """
        Get battery health status and indicators
        
        Args:
            charge_percentage: Current charge percentage
        
        Returns:
            Dict: Battery status information
        """
        if charge_percentage >= 80:
            status = "Excellent"
            icon = "🟢"
            color = "green"
        elif charge_percentage >= 60:
            status = "Good"
            icon = "🟢"
            color = "lightgreen"
        elif charge_percentage >= 40:
            status = "Fair"
            icon = "🟡"
            color = "yellow"
        elif charge_percentage >= 20:
            status = "Low"
            icon = "🟠"
            color = "orange"
        else:
            status = "Critical"
            icon = "🔴"
            color = "red"
        
        return {
            'status': status,
            'icon': icon,
            'color': color,
            'percentage': charge_percentage,
            'needs_charging': charge_percentage < 30
        }