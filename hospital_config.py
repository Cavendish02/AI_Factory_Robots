"""
Hospital Configuration Module
Defines the hospital map layout, colors, grid settings, and utility functions
"""

# Factory Map Layout - FULLY OPEN VERSION (All Paths Clear)
# Legend:
# '#' = Wall
# ' ' = Floor (walkable)
# 'R1-R4' = Robot starting positions
# 'S' = Source (pickup point)
# 'D' = Destination (delivery point)

# This map has NO internal obstacles to ensure all paths work!
FACTORY_MAP = [
    "###############",
    "#             #",
    "#         OOO #",
    "# OOO  D  O D #",  # Opening
    "#   O  O  OOOO#",
    "#R2 O         #",
    "#OOOO  R4 OOO #",
    "#      D  O   #",  # Opening
    "#     OOO O D #",
    "#         OOOO#",
    "#       R1    #",
    "#   R3 D      #",  # Opening
    "#     OOO     #",
    "#S     O    D #",
    "###############"
]



# Keep backward compatibility
HOSPITAL_MAP = FACTORY_MAP

# Enhanced Color Palette
COLORS = {
    # Environment colors
    'wall': (70, 70, 85),           # Dark gray walls
    'floor': (248, 248, 252),       # Light floor
    'obstacle': (220, 120, 100),    # Orange-red obstacles
    'source': (80, 200, 120),       # Green source
    'destination': (100, 130, 220), # Blue destination
    
    # Robot colors (vibrant and distinct)
    'robot_R1': (255, 70, 70),      # Bright red
    'robot_R2': (70, 220, 70),      # Bright green
    'robot_R3': (70, 150, 255),     # Bright blue
    'robot_R4': (255, 200, 50),     # Golden yellow
    
    # Path and UI colors
    'path': (255, 160, 80),         # Orange path
    'path_secondary': (150, 200, 255), # Light blue alternative path
    'text': (30, 30, 40),           # Dark text
    'text_light': (255, 255, 255),  # White text
    
    # Status colors
    'status_available': (80, 200, 120),   # Green
    'status_busy': (255, 100, 100),       # Red
    'status_charging': (255, 200, 50),    # Yellow
    
    # Battery colors
    'battery_high': (80, 220, 100),       # Green (>60%)
    'battery_medium': (255, 200, 50),     # Yellow (30-60%)
    'battery_low': (255, 80, 80),         # Red (<30%)
    'battery_outline': (100, 100, 120),   # Gray outline
    
    # Dashboard colors
    'dashboard_bg': (245, 245, 250),      # Light gray background
    'dashboard_border': (100, 100, 120),  # Border
    'highlight': (100, 180, 255),         # Highlight blue
}

# Grid Configuration
GRID_SIZE = 40                                      # Size of each grid cell in pixels
SCREEN_WIDTH = len(HOSPITAL_MAP[0]) * GRID_SIZE    # Total screen width
SCREEN_HEIGHT = len(HOSPITAL_MAP) * GRID_SIZE      # Total screen height

# Animation Settings
ANIMATION_SPEED = 2          # Speed of animations
FPS = 60                     # Frames per second
PATH_ANIMATION_DELAY = 4     # Delay between path animation frames

# Robot Configuration
ROBOT_CONFIGS = {
    'R1': {
        'name': 'CargoBot-1',
        'color': COLORS['robot_R1'],
        'initial_charge': 100,
        'speed': 1.0
    },
    'R2': {
        'name': 'CargoBot-2',
        'color': COLORS['robot_R2'],
        'initial_charge': 100,
        'speed': 1.0
    },
    'R3': {
        'name': 'CargoBot-3',
        'color': COLORS['robot_R3'],
        'initial_charge': 100,
        'speed': 1.0
    },
    'R4': {
        'name': 'CargoBot-4',
        'color': COLORS['robot_R4'],
        'initial_charge': 100,
        'speed': 1.0
    }
}

# Task Types Configuration
TASK_TYPES = {
    'parts': {
        'name': 'parts Delivery',
        'priority': 3,
        'icon': ' ⚙️'
    },
    'tools': {
        'name': 'tools Transport',
        'priority': 2,
        'icon': '🔧'
    },
    'materials': {
        'name': 'materials Delivery',
        'priority': 4,
        'icon': '📦'
    },
    'documents': {
        'name': 'Document Delivery',
        'priority': 1,
        'icon': '📄'
    },
    'food': {
        'name': 'Meal Delivery',
        'priority': 2,
        'icon': '🍽️'
    }
}

def get_map_positions():
    """
    Extract positions of all elements from the hospital map
    
    Returns:
        dict: Dictionary containing positions of robots, obstacles, source, and destination
    """
    positions = {
        'robots': {},
        'obstacles': [],
        'source': None,
        'destination': None,
        'walls': []
    }
    
    for y, row in enumerate(HOSPITAL_MAP):
        for x, cell in enumerate(row):
            # Check for robot positions (R followed by digit)
            if cell == 'R' and x + 1 < len(row) and row[x + 1].isdigit():
                robot_id = f"R{row[x + 1]}"
                positions['robots'][robot_id] = (x, y)
            
            # Check for obstacles
            elif cell == 'O':
                positions['obstacles'].append((x, y))
            
            # Check for source (single 'S' character)
            elif cell == 'S':
                if positions['source'] is None:
                    positions['source'] = (x, y)
            
            # Check for destination (single 'D' character)
            elif cell == 'D':
                if positions['destination'] is None:
                    positions['destination'] = (x, y)
            
            # Check for walls
            elif cell == '#':
                positions['walls'].append((x, y))
    
    return positions

def is_walkable(x, y):
    """
    Check if a position is walkable (not a wall or obstacle)
    
    Args:
        x (int): X coordinate
        y (int): Y coordinate
    
    Returns:
        bool: True if position is walkable, False otherwise
    """
    if y < 0 or y >= len(HOSPITAL_MAP) or x < 0 or x >= len(HOSPITAL_MAP[0]):
        return False
    
    cell = HOSPITAL_MAP[y][x]
    return cell not in ['#', 'O']

def get_neighbors(x, y):
    """
    Get walkable neighboring positions (4-directional: up, down, left, right)
    
    Args:
        x (int): X coordinate
        y (int): Y coordinate
    
    Returns:
        list: List of (x, y) tuples for walkable neighbors
    """
    neighbors = []
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Down, Up, Right, Left
    
    for dx, dy in directions:
        new_x, new_y = x + dx, y + dy
        if is_walkable(new_x, new_y):
            neighbors.append((new_x, new_y))
    
    return neighbors

def manhattan_distance(pos1, pos2):
    """
    Calculate Manhattan distance between two positions
    
    Args:
        pos1 (tuple): First position (x, y)
        pos2 (tuple): Second position (x, y)
    
    Returns:
        int: Manhattan distance
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def euclidean_distance(pos1, pos2):
    """
    Calculate Euclidean distance between two positions
    
    Args:
        pos1 (tuple): First position (x, y)
        pos2 (tuple): Second position (x, y)
    
    Returns:
        float: Euclidean distance
    """
    return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5

def validate_map():
    """
    Validate the hospital map configuration
    
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    positions = get_map_positions()
    
    # Check if source exists
    if positions['source'] is None:
        return False, "No source position found in map"
    
    # Check if destination exists
    if positions['destination'] is None:
        return False, "No destination position found in map"
    
    # Check if at least one robot exists
    if len(positions['robots']) == 0:
        return False, "No robots found in map"
    
    # Check if all configured robots exist
    for robot_id in ROBOT_CONFIGS.keys():
        if robot_id not in positions['robots']:
            return False, f"Robot {robot_id} configured but not found in map"
    
    return True, "Map configuration is valid"

# Validate map on module import
_is_valid, _error_msg = validate_map()
if not _is_valid:
    print(f"⚠️  Warning: {_error_msg}")
else:
    print(f"✅ Hospital map configuration loaded successfully")
    print(f"   - Map size: {len(HOSPITAL_MAP[0])}x{len(HOSPITAL_MAP)} cells")
    print(f"   - Screen size: {SCREEN_WIDTH}x{SCREEN_HEIGHT} pixels")
    print(f"   - Robots: {len(get_map_positions()['robots'])}")
    print(f"   - Obstacles: {len(get_map_positions()['obstacles'])}")