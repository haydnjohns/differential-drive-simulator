"""
simulator.py

Author: Haydn Johns
Date: 2025-05-31
Version: 1.0

Contains the core logic for the Differential Drive Simulator:
- Data classes for robot parameters, initial conditions, and display options.
- The main simulation loop handling movement, drawing, and user interaction.
- Utility functions to support the simulation.

This module is intended to be imported and called from an external script
which provides the input parameters and executes the simulation.
"""

import pygame
import math
import sys
from dataclasses import dataclass

# Configuration
WIDTH, HEIGHT = 1600, 1200
FPS = 120
SCROLL_BUFFER = 100
PAN_SPEED = 5  # finer pan control
ZOOM_STEP = 0.05
ZOOM_MIN = 1
ZOOM_MAX = 20


@dataclass
class RobotParameters:
    wheel_diameter: float
    robot_width: float
    scale: float  # initial scale (zoom)
    step_size: float
    axle_offset: float

    @property
    def half_robot_width(self):
        return self.robot_width / 2

    @property
    def wheel_circumference(self):
        return math.pi * self.wheel_diameter


@dataclass
class InitialConditions:
    x: float
    y: float
    heading: float


@dataclass
class DisplayOptions:
    show_origin: bool
    show_initial_position: bool
    show_path: bool
    show_turns: bool
    show_heading: bool
    show_axle: bool
    show_grid: bool


# [Same imports and dataclass definitions as before...]

def main(params: RobotParameters, init: InitialConditions, movements: list, display: DisplayOptions):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Differential Drive Simulator")
    clock = pygame.time.Clock()

    scroll_x = init.x
    scroll_y = init.y
    zoom = params.scale

    instruction_markers = []
    frames = []

    x, y = init.x, init.y
    heading = init.heading
    axle_x = x - params.axle_offset * math.sin(heading)
    axle_y = y - params.axle_offset * math.cos(heading)

    movement_index = 0
    remaining_distance = 0
    active_wheel_command = None
    direction_sign = 1
    previous_wheel = None

    paused = False
    frame_index = 0
    sim_frame_index = 0
    simulation_finished = False

    scrubbing = False
    scrubbing_direction = 0
    sim_frame_index_before_scrub = 0

    def draw_grid():
        grid_spacing = 50  # grid spacing in world units (adjust as you like)
        line_color = (100, 100, 100)  # grid line color

        # Calculate grid lines in world coordinates that should appear on screen
        # Determine min and max world coordinates visible on screen
        left_world = scroll_x - (WIDTH / 2) / zoom
        right_world = scroll_x + (WIDTH / 2) / zoom
        top_world = scroll_y + (HEIGHT / 2) / zoom
        bottom_world = scroll_y - (HEIGHT / 2) / zoom

        # Start and end grid lines for vertical (x) and horizontal (y)
        start_x = int(left_world // grid_spacing * grid_spacing)
        end_x = int(right_world // grid_spacing * grid_spacing + grid_spacing)
        start_y = int(bottom_world // grid_spacing * grid_spacing)
        end_y = int(top_world // grid_spacing * grid_spacing + grid_spacing)

        # Draw vertical grid lines
        x = start_x
        while x <= end_x:
            sx, _ = world_to_screen(x, 0)
            pygame.draw.line(screen, line_color, (sx, 0), (sx, HEIGHT))
            x += grid_spacing

        # Draw horizontal grid lines
        y = start_y
        while y <= end_y:
            _, sy = world_to_screen(0, y)
            pygame.draw.line(screen, line_color, (0, sy), (WIDTH, sy))
            y += grid_spacing

    def world_to_screen(wx, wy):
        sx = WIDTH // 2 + (wx - scroll_x) * zoom
        sy = HEIGHT // 2 - (wy - scroll_y) * zoom
        return int(sx), int(sy)

    def record_frame():
        frames.append({
            'x': x,
            'y': y,
            'heading': heading,
            'axle_x': axle_x,
            'axle_y': axle_y,
            'movement_index': movement_index,
            'remaining_distance': remaining_distance,
            'active_wheel_command': active_wheel_command,
            'direction_sign': direction_sign,
            'instruction_markers': instruction_markers.copy(),
        })

    record_frame()
    path = [(x, y)]

    running = True
    while running:
        clock.tick(FPS)
        screen.fill((71, 71, 71))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                    if paused:
                        sim_frame_index_before_scrub = sim_frame_index
                    else:
                        sim_frame_index = sim_frame_index_before_scrub
                        frame_index = sim_frame_index
                        scrubbing = False
                        scrubbing_direction = 0

                elif event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_0:
                    if frames:
                        xs = [f['x'] for f in frames]
                        ys = [f['y'] for f in frames]
                        min_x, max_x = min(xs), max(xs)
                        min_y, max_y = min(ys), max(ys)
                        width = max_x - min_x
                        height = max_y - min_y
                        padding = max(width, height) * 0.1
                        width += padding
                        height += padding
                        zoom_x = WIDTH / width if width != 0 else ZOOM_MAX
                        zoom_y = HEIGHT / height if height != 0 else ZOOM_MAX
                        zoom = min(zoom_x, zoom_y, ZOOM_MAX)
                        zoom = max(zoom, ZOOM_MIN)
                        scroll_x = (min_x + max_x) / 2
                        scroll_y = (min_y + max_y) / 2

                elif event.key == pygame.K_LEFTBRACKET:
                    if paused or simulation_finished:
                        scrubbing = True
                        scrubbing_direction = -1
                        sim_frame_index_before_scrub = sim_frame_index

                elif event.key == pygame.K_RIGHTBRACKET:
                    if paused or simulation_finished:
                        scrubbing = True
                        scrubbing_direction = 1
                        sim_frame_index_before_scrub = sim_frame_index

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET):
                    scrubbing = False
                    scrubbing_direction = 0

        keys = pygame.key.get_pressed()

        # Pan controls
        if keys[pygame.K_LEFT]:
            scroll_x -= PAN_SPEED / zoom
        if keys[pygame.K_RIGHT]:
            scroll_x += PAN_SPEED / zoom
        if keys[pygame.K_UP]:
            scroll_y += PAN_SPEED / zoom
        if keys[pygame.K_DOWN]:
            scroll_y -= PAN_SPEED / zoom
        if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]:
            zoom = min(zoom + ZOOM_STEP, ZOOM_MAX)
        if keys[pygame.K_MINUS] or keys[pygame.K_UNDERSCORE]:
            zoom = max(zoom - ZOOM_STEP, ZOOM_MIN)

        # Handle scrubbing
        if scrubbing and (paused or simulation_finished):
            scrub_speed = 1
            new_frame_index = frame_index + scrubbing_direction * scrub_speed
            new_frame_index = max(0, min(len(frames) - 1, new_frame_index))
            frame_index = new_frame_index

        # Main simulation loop
        if not paused and not scrubbing and not simulation_finished:
            if remaining_distance <= 0 and movement_index < len(movements):
                direction, wheel_cmd, rotations = movements[movement_index]
                direction_sign = 1 if direction == "forward" else -1
                remaining_distance = rotations * params.wheel_circumference
                active_wheel_command = wheel_cmd

                if display.show_turns and wheel_cmd != previous_wheel:
                    previous_wheel = wheel_cmd
                    instruction_markers.append((x, y))

                movement_index += 1

            if remaining_distance > 0:
                step = min(params.step_size, remaining_distance)

                if active_wheel_command == "both":
                    dx = math.sin(heading) * step * direction_sign
                    dy = math.cos(heading) * step * direction_sign
                    axle_x += dx
                    axle_y += dy
                    x += dx
                    y += dy

                else:
                    theta = direction_sign * step / params.robot_width
                    pivot_x = axle_x - params.half_robot_width * math.cos(heading)
                    pivot_y = axle_y + params.half_robot_width * math.sin(heading)
                    dx_local = params.half_robot_width * math.cos(heading)
                    dy_local = -params.half_robot_width * math.sin(heading)
                    cos_theta = math.cos(theta)
                    sin_theta = math.sin(theta)
                    x_rel_pivot = dx_local * cos_theta - dy_local * sin_theta
                    y_rel_pivot = dx_local * sin_theta + dy_local * cos_theta
                    axle_x = pivot_x + x_rel_pivot
                    axle_y = pivot_y + y_rel_pivot
                    x = params.axle_offset * math.sin(heading) + axle_x
                    y = params.axle_offset * math.cos(heading) + axle_y

                    if active_wheel_command == "left":
                        heading += theta
                    else:
                        heading -= theta

                remaining_distance -= step
                path.append((x, y))

            if movement_index >= len(movements) and remaining_distance <= 0:
                simulation_finished = True

            if not simulation_finished and not any([keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP], keys[pygame.K_DOWN]]):
                screen_x, screen_y = WIDTH // 2 + (x - scroll_x) * zoom, HEIGHT // 2 - (y - scroll_y) * zoom
                if screen_x > WIDTH - SCROLL_BUFFER:
                    scroll_x += (screen_x - (WIDTH - SCROLL_BUFFER)) / zoom
                elif screen_x < SCROLL_BUFFER:
                    scroll_x -= (SCROLL_BUFFER - screen_x) / zoom
                if screen_y > HEIGHT - SCROLL_BUFFER:
                    scroll_y -= (screen_y - (HEIGHT - SCROLL_BUFFER)) / zoom
                elif screen_y < SCROLL_BUFFER:
                    scroll_y += (SCROLL_BUFFER - screen_y) / zoom

            record_frame()
            sim_frame_index = len(frames) - 1
            frame_index = sim_frame_index

        # Draw current frame
        if frames:
            f = frames[frame_index]
            draw_x = f['x']
            draw_y = f['y']
            draw_heading = f['heading']
            draw_axle_x = f['axle_x']
            draw_axle_y = f['axle_y']
            draw_instruction_markers = f['instruction_markers']
        else:
            draw_x, draw_y = x, y
            draw_heading = heading
            draw_axle_x, draw_axle_y = axle_x, axle_y
            draw_instruction_markers = instruction_markers

        if display.show_path and len(path) > 1:
            screen_points = [world_to_screen(px, py) for px, py in path]
            pygame.draw.lines(screen, (200, 200, 150), False, screen_points, 2)

        if display.show_turns:
            for mx, my in draw_instruction_markers:
                sx, sy = world_to_screen(mx, my)
                pygame.draw.circle(screen, (150, 130, 50), (sx, sy), 4)

        half_width = params.robot_width / 2
        left_wheel_x = draw_axle_x - half_width * math.cos(draw_heading)
        left_wheel_y = draw_axle_y + half_width * math.sin(draw_heading)
        right_wheel_x = draw_axle_x + half_width * math.cos(draw_heading)
        right_wheel_y = draw_axle_y - half_width * math.sin(draw_heading)
        
        if display.show_grid:
            draw_grid()
            
        if display.show_axle:
            screen_lx, screen_ly = world_to_screen(left_wheel_x, left_wheel_y)
            screen_rx, screen_ry = world_to_screen(right_wheel_x, right_wheel_y)
            pygame.draw.circle(screen, (255, 0, 0), (screen_lx, screen_ly), 5)
            pygame.draw.circle(screen, (0, 200, 0), (screen_rx, screen_ry), 5)

            screen_axle_x, screen_axle_y = world_to_screen(draw_axle_x, draw_axle_y)
            pygame.draw.circle(screen, (255, 240, 60), (screen_axle_x, screen_axle_y), 5)

        screen_robot_x, screen_robot_y = world_to_screen(draw_x, draw_y)
        pygame.draw.circle(screen, (255, 240, 60), (screen_robot_x, screen_robot_y), 5)

        if display.show_origin:
            origin_screen = world_to_screen(0, 0)
            pygame.draw.circle(screen, (50, 50, 50), origin_screen, 5)

        if display.show_initial_position:
            init_screen = world_to_screen(init.x, init.y)
            pygame.draw.circle(screen, (100, 90, 20), init_screen, 5)

        if display.show_heading:
            dx_heading = math.sin(draw_heading) * 15
            dy_heading = math.cos(draw_heading) * 15
            end_x, end_y = world_to_screen(draw_x + dx_heading, draw_y + dy_heading)
            pygame.draw.line(screen, (255, 255, 255), (screen_robot_x, screen_robot_y), (end_x, end_y), 2)

        pygame.display.flip()

    pygame.quit()
    sys.exit()
