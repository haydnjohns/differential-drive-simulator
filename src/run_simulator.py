"""
run_simulation.py

Author: Haydn Johns
Date: 2025-05-31
Version: 1.0

Defines robot parameters, initial conditions, movement instructions, and display options.

Imports and calls the simulator's main() function to run the Differential Drive Simulator.

Features:
- Forward and backward movement with left, right, or both wheels
- Visual display of robot path, heading, turns, and more
- Interactive controls for panning, zooming, pausing, and scrubbing frames
    - Rewind/scrub with '[' and ']'
    - Play/pause with 'Space'
    - Zoom in/out with '+' and '-'
    - Reset view with '0'
- Exit with Esc key
"""

import math
from simulator import RobotParameters, InitialConditions, DisplayOptions, main



if __name__ == "__main__":
    robot_params = RobotParameters(
        wheel_diameter=20,  # wheels assumed same diameter
        robot_width=70,  # distance between wheels
        scale=5,  # scaling factor for visualisation only
        step_size=0.5,  # distance between frames, mm
        axle_offset=-40  # distance between centre of wheels and centre of robot, positive puts centre of robot in front of wheels
    )
    # Define initial conditions of robot
    # x and y are in mm
    # heading is in radians, positive is clockwise, 0 is up
    initial_conditions = InitialConditions(
        x=-30,
        y=-20,
        heading=math.radians(30)
    )

    # Movements are tuples of (direction, wheels, no. wheel rotations)
    # Directions: "forward", "backward"
    # Wheels: "left", "right", "both"
    # no. wheel rotations: positive radians
    movements = [
        ("forward", "left", 1),
        ("forward", "right", 1),
        ("forward", "both", 1),
        ("backward", "left", 1),
        ("backward", "right", 1),
        ("backward", "both", 1),
    ]

    display_options = DisplayOptions(
        show_origin=True,  # Persistent node at origin
        show_initial_position=True,  # Persistent node at initial robot position
        show_path=True,  # Traces path
        show_turns=True,  # Nodes generated between instructions (i.e., turns)
        show_heading=True,  # Short line indicating heading
        show_axle=True  # Nodes for wheels and centre of axle
    )

    main(robot_params, initial_conditions, movements, display_options)