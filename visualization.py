import pygame
import sys
from hospital_config import HOSPITAL_MAP, COLORS, GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT

class HospitalVisualization:
    def __init__(self):
        pygame.init()
        
        # Layout dimensions
        self.map_width = SCREEN_WIDTH
        self.map_height = SCREEN_HEIGHT
        self.right_panel_width = 400  # Reduced width for better fit
        self.top_bar_height = 50
        
        # Calculate total window size
        self.total_width = self.map_width + self.right_panel_width
        self.total_height = self.top_bar_height + self.map_height
        
        # Map positioning
        self.map_x = 0
        self.map_y = self.top_bar_height
        
        # Right panel positioning
        self.panel_x = self.map_width
        self.panel_y = self.top_bar_height
        
        self.screen = pygame.display.set_mode((self.total_width, self.total_height))
        pygame.display.set_caption("AI Factory Robot Management System")
        self.clock = pygame.time.Clock()
        
        # Improved font system
        self.font_tiny = pygame.font.SysFont('Segoe UI', 10)
        self.font_small = pygame.font.SysFont('Segoe UI', 12)
        self.font_regular = pygame.font.SysFont('Segoe UI', 14)
        self.font_medium = pygame.font.SysFont('Segoe UI', 16, bold=True)
        self.font_large = pygame.font.SysFont('Segoe UI', 18, bold=True)
        self.font_title = pygame.font.SysFont('Segoe UI', 22, bold=True)
        
        self.running = True
        self.obstacles = self.extract_obstacles()
        
        # Animation
        self.animation_frame = 0
        self.path_animation_offset = 0
        
        # Modern color scheme
        self.bg_main = (240, 242, 245)
        self.panel_bg = (255, 255, 255)
        self.panel_header = (248, 249, 250)
        self.border = (220, 223, 228)
        self.text_primary = (32, 33, 36)
        self.text_secondary = (95, 99, 104)
        self.accent = (66, 133, 244)
        self.success = (52, 168, 83)
        self.warning = (251, 188, 4)
        self.danger = (234, 67, 53)
        self.info = (101, 103, 237)
        
        # Scroll system for right panel
        self.scroll_offset = 0
        self.max_scroll = 0
        
    def extract_obstacles(self):
        """Extract obstacles from the hospital map"""
        obstacles = []
        for y, row in enumerate(HOSPITAL_MAP):
            for x, cell in enumerate(row):
                if cell == '#' or cell == 'O':
                    obstacles.append((x, y))
        return obstacles
    
    def draw_top_bar(self):
        """Draw compact top bar"""
        # Gradient background
        for i in range(self.top_bar_height):
            ratio = i / self.top_bar_height
            r = int(66 + (20 * ratio))
            g = int(133 + (20 * ratio))
            b = int(244 + (11 * ratio))
            pygame.draw.line(self.screen, (r, g, b), (0, i), (self.total_width, i))
        
        # Title with icon
        title = self.font_title.render("🏥 AI Hospital Robot Management", True, (255, 255, 255))
        self.screen.blit(title, (15, (self.top_bar_height - title.get_height()) // 2))
        
        # Status indicator
        status_text = self.font_small.render("Live System", True, (200, 255, 200))
        status_rect = status_text.get_rect(topright=(self.total_width - 15, 15))
        self.screen.blit(status_text, status_rect)
    
    def draw_hospital_map(self):
        """Draw the hospital map"""
        # Map background
        map_rect = pygame.Rect(self.map_x, self.map_y, self.map_width, self.map_height)
        pygame.draw.rect(self.screen, COLORS['floor'], map_rect)
        
        # Draw cells
        for y, row in enumerate(HOSPITAL_MAP):
            for x, cell in enumerate(row):
                cell_x = self.map_x + (x * GRID_SIZE)
                cell_y = self.map_y + (y * GRID_SIZE)
                rect = pygame.Rect(cell_x, cell_y, GRID_SIZE, GRID_SIZE)
                
                if cell == '#':  # Wall
                    pygame.draw.rect(self.screen, COLORS['wall'], rect)
                    pygame.draw.rect(self.screen, (60, 60, 70), rect, 1)
                    
                elif cell == 'O':  # Obstacle
                    pygame.draw.rect(self.screen, COLORS['obstacle'], rect)
                    pygame.draw.circle(self.screen, (180, 100, 80), rect.center, 8)
                    
                elif cell == 'S':  # Source
                    pygame.draw.rect(self.screen, COLORS['source'], rect)
                    pygame.draw.circle(self.screen, (40, 180, 100), rect.center, 15, 3)
                    text = self.font_tiny.render("S", True, (255, 255, 255))
                    text_rect = text.get_rect(center=rect.center)
                    self.screen.blit(text, text_rect)
                    
                elif cell == 'D':  # Destination
                    pygame.draw.rect(self.screen, COLORS['destination'], rect)
                    pygame.draw.circle(self.screen, (80, 110, 200), rect.center, 15, 3)
                    text = self.font_tiny.render("D", True, (255, 255, 255))
                    text_rect = text.get_rect(center=rect.center)
                    self.screen.blit(text, text_rect)
                
                # Subtle grid
                pygame.draw.rect(self.screen, (230, 230, 235), rect, 1)
        
        # Map border
        pygame.draw.rect(self.screen, self.border, map_rect, 3)
    
    def draw_robot_on_map(self, robot):
        """Draw single robot on map"""
        x = self.map_x + (robot.x * GRID_SIZE) + (GRID_SIZE // 2)
        y = self.map_y + (robot.y * GRID_SIZE) + (GRID_SIZE // 2)
        
        # Shadow
        pygame.draw.circle(self.screen, (0, 0, 0, 30), (x + 2, y + 2), 14)
        
        # Robot body with pulse animation for busy robots
        radius = 13
        if robot.status.value == "Busy":
            pulse = abs((self.animation_frame % 40) - 20) / 20.0
            radius = int(13 + pulse * 2)
        
        # Main circle
        pygame.draw.circle(self.screen, robot.color, (x, y), radius)
        pygame.draw.circle(self.screen, (255, 255, 255), (x, y), radius - 4)
        
        # Status dot
        dot_radius = 4
        if robot.status.value == "Busy":
            pygame.draw.circle(self.screen, self.danger, (x, y), dot_radius)
        elif robot.status.value == "Charging":
            pygame.draw.circle(self.screen, self.warning, (x, y), dot_radius)
        else:
            pygame.draw.circle(self.screen, self.success, (x, y), dot_radius)
        
        # Mini battery indicator
        battery = robot.charge_percentage
        bar_width = 20
        bar_height = 3
        bar_x = x - (bar_width // 2)
        bar_y = y - 22
        
        # Battery outline
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 1)
        
        # Battery fill
        fill_width = int((bar_width - 2) * battery / 100)
        if battery > 50:
            fill_color = self.success
        elif battery > 20:
            fill_color = self.warning
        else:
            fill_color = self.danger
        pygame.draw.rect(self.screen, fill_color, (bar_x + 1, bar_y + 1, fill_width, bar_height - 2))
    
    def draw_robots(self, robots):
        """Draw all robots"""
        for robot in robots:
            self.draw_robot_on_map(robot)
    
    def draw_path(self, path, color=None, width=3, animated=False):
        """Draw path on map"""
        if not path or len(path) < 2:
            return
        
        path_color = color if color else COLORS['path']
        
        for i in range(len(path) - 1):
            x1 = self.map_x + (path[i][0] * GRID_SIZE) + (GRID_SIZE // 2)
            y1 = self.map_y + (path[i][1] * GRID_SIZE) + (GRID_SIZE // 2)
            x2 = self.map_x + (path[i+1][0] * GRID_SIZE) + (GRID_SIZE // 2)
            y2 = self.map_y + (path[i+1][1] * GRID_SIZE) + (GRID_SIZE // 2)
            
            if animated:
                # Dashed animated line
                dx = x2 - x1
                dy = y2 - y1
                dist = (dx**2 + dy**2)**0.5
                if dist > 0:
                    segments = int(dist / 8)
                    for j in range(segments):
                        if (j + self.path_animation_offset) % 4 < 2:
                            t1 = j / segments
                            t2 = min((j + 1) / segments, 1.0)
                            px1 = x1 + dx * t1
                            py1 = y1 + dy * t1
                            px2 = x1 + dx * t2
                            py2 = y1 + dy * t2
                            pygame.draw.line(self.screen, path_color, (px1, py1), (px2, py2), width)
            else:
                pygame.draw.line(self.screen, path_color, (x1, y1), (x2, y2), width)
        
        self.path_animation_offset = (self.path_animation_offset + 1) % 4
    
    def draw_task_animation(self, task, robot):
        """Draw task animation on map"""
        if not task or not robot:
            return
        
        sx = self.map_x + (task.source_x * GRID_SIZE) + (GRID_SIZE // 2)
        sy = self.map_y + (task.source_y * GRID_SIZE) + (GRID_SIZE // 2)
        dx = self.map_x + (task.dest_x * GRID_SIZE) + (GRID_SIZE // 2)
        dy = self.map_y + (task.dest_y * GRID_SIZE) + (GRID_SIZE // 2)
        
        # Animated particles
        for i in range(0, 100, 8):
            if (i + self.animation_frame) % 16 < 8:
                progress = i / 100
                px = sx + (dx - sx) * progress
                py = sy + (dy - sy) * progress
                pygame.draw.circle(self.screen, (0, 255, 150), (int(px), int(py)), 4)
        
        self.animation_frame = (self.animation_frame + 1) % 60

    def draw_right_panel(self, robots, tasks, current_task_info):
        """Draw redesigned right side panel with better layout"""
        px = self.panel_x
        py = self.panel_y
        pw = self.right_panel_width
        ph = self.map_height
        
        # Panel background
        panel_rect = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(self.screen, self.panel_bg, panel_rect)
        pygame.draw.rect(self.screen, self.border, panel_rect, 2)
        
        # Scrollable content area
        content_height = self._calculate_content_height(robots, tasks)
        self.max_scroll = max(0, content_height - ph)
        
        # Apply scroll offset
        draw_y = py + 15 - self.scroll_offset
        
        # ===== SYSTEM OVERVIEW =====
        draw_y = self._draw_system_overview(px, draw_y, pw, robots, tasks)
        
        # ===== ROBOTS SECTION =====
        draw_y = self._draw_robots_section(px, draw_y, pw, robots)
        
        # ===== TASKS SECTION =====
        draw_y = self._draw_tasks_section(px, draw_y, pw, tasks)
        
        # ===== ACTIVE TASK =====
        draw_y = self._draw_active_task(px, draw_y, pw, current_task_info)
        
        # ===== CONTROLS =====
        draw_y = self._draw_controls_section(px, draw_y, pw)
        
        # ===== LEGEND =====
        draw_y = self._draw_legend_section(px, draw_y, pw)
        
        # Draw scroll bar if needed
        if content_height > ph:
            self._draw_scrollbar(px, py, pw, ph, content_height)
    
    def _calculate_content_height(self, robots, tasks):
        """Calculate total content height for scrolling"""
        base_height = 400  # Fixed sections height
        robots_height = len(robots) * 70  # Each robot card
        tasks_height = 120  # Tasks section
        return base_height + robots_height + tasks_height
    
    def _draw_system_overview(self, x, y, width, robots, tasks):
        """Draw system overview section"""
        # Header
        header_rect = pygame.Rect(x + 10, y, width - 20, 35)
        pygame.draw.rect(self.screen, self.panel_header, header_rect, border_radius=8)
        
        title = self.font_medium.render("📊 SYSTEM OVERVIEW", True, self.text_primary)
        self.screen.blit(title, (x + 20, y + 8))
        
        y += 45
        
        # Stats grid
        stats = [
            ("🤖 Robots", f"{len(robots)}", self.info),
            ("✅ Completed", f"{sum(1 for t in tasks if t.status == 'Completed')}", self.success),
            ("🔄 Active", f"{sum(1 for t in tasks if t.status == 'In Progress')}", self.warning),
            ("⏳ Pending", f"{sum(1 for t in tasks if t.status == 'Pending')}", self.danger)
        ]
        
        # Draw stats in 2x2 grid
        for i, (label, value, color) in enumerate(stats):
            row = i // 2
            col = i % 2
            stat_x = x + 15 + (col * (width - 30) // 2)
            stat_y = y + (row * 50)
            
            stat_rect = pygame.Rect(stat_x, stat_y, (width - 40) // 2, 40)
            pygame.draw.rect(self.screen, (245, 247, 250), stat_rect, border_radius=6)
            pygame.draw.rect(self.screen, self.border, stat_rect, 1, border_radius=6)
            
            # Value
            value_text = self.font_large.render(value, True, color)
            value_rect = value_text.get_rect(center=(stat_x + (width - 40) // 4, stat_y + 15))
            self.screen.blit(value_text, value_rect)
            
            # Label
            label_text = self.font_tiny.render(label, True, self.text_secondary)
            label_rect = label_text.get_rect(center=(stat_x + (width - 40) // 4, stat_y + 30))
            self.screen.blit(label_text, label_rect)
        
        return y + 110
    
    def _draw_robots_section(self, x, y, width, robots):
        """Draw robots section with compact cards"""
        # Header
        header_rect = pygame.Rect(x + 10, y, width - 20, 30)
        pygame.draw.rect(self.screen, self.panel_header, header_rect, border_radius=6)
        
        title = self.font_medium.render(f"🤖 ROBOTS ({len(robots)})", True, self.text_primary)
        self.screen.blit(title, (x + 20, y + 6))
        
        y += 40
        
        # Robot cards
        for robot in robots:
            if y - self.scroll_offset < self.panel_y + self.map_height:  # Only draw visible cards
                y = self._draw_robot_card(robot, x, y, width)
            else:
                y += 70  # Account for hidden cards
        
        return y + 10
    
    def _draw_robot_card(self, robot, x, y, width):
        """Draw individual robot card"""
        card = pygame.Rect(x + 10, y, width - 20, 60)
        
        # Card background with subtle shadow
        pygame.draw.rect(self.screen, (250, 251, 252), card, border_radius=8)
        pygame.draw.rect(self.screen, self.border, card, 1, border_radius=8)
        
        # Robot icon and name
        icon_text = self.font_regular.render("🤖", True, self.text_primary)
        self.screen.blit(icon_text, (x + 20, y + 8))
        
        name_text = self.font_regular.render(robot.name, True, self.text_primary)
        self.screen.blit(name_text, (x + 45, y + 8))
        
        # Status with colored dot
        status_color = {
            "Available": self.success,
            "Busy": self.danger,
            "Charging": self.warning
        }.get(robot.status.value, self.text_secondary)
        
        pygame.draw.circle(self.screen, status_color, (x + width - 50, y + 15), 4)
        status_text = self.font_small.render(robot.status.value, True, self.text_secondary)
        self.screen.blit(status_text, (x + width - 40, y + 10))
        
        # Battery bar
        battery_width = width - 100
        battery_bg = pygame.Rect(x + 20, y + 30, battery_width, 12)
        pygame.draw.rect(self.screen, (230, 230, 235), battery_bg, border_radius=6)
        
        battery = robot.charge_percentage
        fill_width = max(4, int((battery_width - 4) * battery / 100))
        fill_color = self.success if battery > 50 else self.warning if battery > 20 else self.danger
        
        fill_rect = pygame.Rect(x + 22, y + 32, fill_width, 8)
        pygame.draw.rect(self.screen, fill_color, fill_rect, border_radius=4)
        
        # Battery text
        battery_text = self.font_tiny.render(f"{battery:.0f}%", True, self.text_secondary)
        self.screen.blit(battery_text, (x + width - 40, y + 30))
        
        # Stats line
        stats_text = self.font_tiny.render(
            f"Tasks: {robot.completed_tasks} | Distance: {robot.total_distance:.0f}m | Speed: {robot.velocity}",
            True, self.text_secondary
        )
        self.screen.blit(stats_text, (x + 20, y + 48))
        
        return y + 70
    
    def _draw_tasks_section(self, x, y, width, tasks):
        """Draw tasks progress section"""
        # Header
        header_rect = pygame.Rect(x + 10, y, width - 20, 30)
        pygame.draw.rect(self.screen, self.panel_header, header_rect, border_radius=6)
        
        completed = sum(1 for t in tasks if t.status == "Completed")
        total = len(tasks)
        progress = (completed / total * 100) if total > 0 else 0
        
        title = self.font_medium.render(f"📋 TASKS ({completed}/{total})", True, self.text_primary)
        self.screen.blit(title, (x + 20, y + 6))
        
        y += 40
        
        # Progress bar
        bar_width = width - 40
        bar_bg = pygame.Rect(x + 20, y, bar_width, 20)
        pygame.draw.rect(self.screen, (230, 230, 235), bar_bg, border_radius=10)
        
        if progress > 0:
            fill_width = int((bar_width - 4) * progress / 100)
            fill_rect = pygame.Rect(x + 22, y + 2, fill_width, 16)
            pygame.draw.rect(self.screen, self.success, fill_rect, border_radius=8)
        
        # Progress text
        progress_text = self.font_small.render(f"{progress:.1f}% Complete", True, self.text_primary)
        text_rect = progress_text.get_rect(center=bar_bg.center)
        self.screen.blit(progress_text, text_rect)
        
        y += 35
        
        # Task breakdown
        breakdown = [
            ("✅ Completed", completed, self.success),
            ("🔄 In Progress", sum(1 for t in tasks if t.status == "In Progress"), self.warning),
            ("⏳ Pending", sum(1 for t in tasks if t.status == "Pending"), self.danger)
        ]
        
        for label, count, color in breakdown:
            breakdown_text = self.font_small.render(f"{label}: {count}", True, color)
            self.screen.blit(breakdown_text, (x + 20, y))
            y += 20
        
        return y + 15
    
    def _draw_active_task(self, x, y, width, current_task_info):
        """Draw active task section"""
        # Header
        header_rect = pygame.Rect(x + 10, y, width - 20, 30)
        pygame.draw.rect(self.screen, self.panel_header, header_rect, border_radius=6)
        
        title = self.font_medium.render("🎯 ACTIVE TASK", True, self.text_primary)
        self.screen.blit(title, (x + 20, y + 6))
        
        y += 40
        
        if current_task_info:
            # Active task card with animation
            card = pygame.Rect(x + 10, y, width - 20, 80)
            border_color = self.accent if self.animation_frame % 60 < 30 else (100, 160, 255)
            
            pygame.draw.rect(self.screen, (240, 248, 255), card, border_radius=8)
            pygame.draw.rect(self.screen, border_color, card, 2, border_radius=8)
            
            # Wrap task info text
            task_lines = self._wrap_text(current_task_info, self.font_small, width - 50)
            for i, line in enumerate(task_lines[:3]):  # Max 3 lines
                task_text = self.font_small.render(line, True, self.accent)
                self.screen.blit(task_text, (x + 20, y + 15 + (i * 18)))
            
            y += 90
        else:
            no_task = self.font_small.render("No active tasks", True, self.text_secondary)
            self.screen.blit(no_task, (x + 20, y))
            y += 40
        
        return y
    
    def _draw_controls_section(self, x, y, width):
        """Draw controls section"""
        # Header
        header_rect = pygame.Rect(x + 10, y, width - 20, 30)
        pygame.draw.rect(self.screen, self.panel_header, header_rect, border_radius=6)
        
        title = self.font_medium.render("⌨️ CONTROLS", True, self.text_primary)
        self.screen.blit(title, (x + 20, y + 6))
        
        y += 40
        
        controls = [
            ("SPACE", "Execute Next Task", self.success),
            ("P", "Pause/Resume", self.warning),
            ("R", "Reset System", self.danger),
            ("ESC", "Exit Program", self.text_secondary)
        ]
        
        for key, desc, color in controls:
            # Key button
            key_rect = pygame.Rect(x + 20, y, 70, 25)
            pygame.draw.rect(self.screen, color, key_rect, border_radius=6)
            
            key_text = self.font_small.render(key, True, (255, 255, 255))
            key_rect_center = key_text.get_rect(center=key_rect.center)
            self.screen.blit(key_text, key_rect_center)
            
            # Description
            desc_text = self.font_small.render(desc, True, self.text_primary)
            self.screen.blit(desc_text, (x + 100, y + 5))
            
            y += 35
        
        return y
    
    def _draw_legend_section(self, x, y, width):
        """Draw map legend section"""
        # Header
        header_rect = pygame.Rect(x + 10, y, width - 20, 30)
        pygame.draw.rect(self.screen, self.panel_header, header_rect, border_radius=6)
        
        title = self.font_medium.render("🗺️ MAP LEGEND", True, self.text_primary)
        self.screen.blit(title, (x + 20, y + 6))
        
        y += 40
        
        legend_items = [
            (COLORS['wall'], "Wall", "#"),
            (COLORS['source'], "Source", "S"),
            (COLORS['destination'], "Destination", "D"),
            (COLORS['obstacle'], "Obstacle", "O"),
            (COLORS['path'], "Robot Path", "---")
        ]
        
        for i, (color, label, symbol) in enumerate(legend_items):
            row_y = y + (i * 25)
            
            # Color box
            color_rect = pygame.Rect(x + 20, row_y, 20, 15)
            pygame.draw.rect(self.screen, color, color_rect, border_radius=3)
            pygame.draw.rect(self.screen, self.border, color_rect, 1, border_radius=3)
            
            # Symbol
            symbol_text = self.font_small.render(symbol, True, self.text_primary)
            self.screen.blit(symbol_text, (x + 45, row_y))
            
            # Label
            label_text = self.font_small.render(label, True, self.text_secondary)
            self.screen.blit(label_text, (x + 80, row_y))
        
        return y + (len(legend_items) * 25) + 20
    
    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _draw_scrollbar(self, x, y, width, height, content_height):
        """Draw scrollbar for the right panel"""
        scrollbar_width = 8
        scrollbar_x = x + width - scrollbar_width - 2
        
        # Calculate scrollbar height and position
        visible_ratio = height / content_height
        scrollbar_height = max(30, int(height * visible_ratio))
        scrollbar_y = y + (self.scroll_offset / content_height) * height
        
        scrollbar_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(self.screen, (200, 200, 200), scrollbar_rect, border_radius=4)
        pygame.draw.rect(self.screen, (150, 150, 150), scrollbar_rect, 1, border_radius=4)
    
    def handle_scroll(self, event):
        """Handle mouse scroll events"""
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - event.y * 30))
    
    def draw_dashboard(self, robots, tasks, current_task_info):
        """Main drawing function"""
        self.screen.fill(self.bg_main)
        self.draw_top_bar()
        self.draw_hospital_map()
        self.draw_robots(robots)  # Draw robots on map
        self.draw_right_panel(robots, tasks, current_task_info)
    
    def handle_events(self):
        """Handle pygame events including scroll"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return "quit"
                elif event.key == pygame.K_SPACE:
                    return "next_task"
                elif event.key == pygame.K_p:
                    return "pause"
                elif event.key == pygame.K_r:
                    return "reset"
            elif event.type == pygame.MOUSEWHEEL:
                self.handle_scroll(event)
        return None
    
    def update(self):
        """Update display"""
        pygame.display.flip()
        self.clock.tick(60)
        self.animation_frame += 1



